import google.generativeai as genai

from app.services.embeddings import get_embeddings
from app.services.vector_store import search
from app.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL

genai.configure(api_key=GEMINI_API_KEY)


def _normalize_model_name(model_name: str) -> str:
    cleaned = model_name.strip()
    if cleaned.startswith("models/"):
        return cleaned.split("/", 1)[1]
    return cleaned


def _candidate_chat_models(model_name: str) -> list[str]:
    cleaned = model_name.strip()
    if cleaned.startswith("models/"):
        cleaned = cleaned.split("/", 1)[1]

    candidates = [cleaned, "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash-001"]
    seen = set()
    result = []
    for name in candidates:
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _discover_generate_content_models() -> list[str]:
    discovered: list[str] = []
    for model in genai.list_models():
        methods = getattr(model, "supported_generation_methods", None) or []
        if "generateContent" in methods and model.name.startswith("models/"):
            discovered.append(_normalize_model_name(model.name))
    return discovered

def answer_query(query: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in backend/.env")

    query_embedding = get_embeddings([query], task_type="retrieval_query")[0]
    context_chunks = search(query_embedding)
    if not context_chunks:
        return "No indexed PDF content found. Please upload a PDF first."

    context = "\n\n".join(context_chunks)

    prompt = f"""
Answer using ONLY the context below.

Context:
{context}

Question:
{query}
"""

    last_error = None
    configured = _candidate_chat_models(GEMINI_CHAT_MODEL)
    discovered = _discover_generate_content_models()
    model_candidates = configured + [m for m in discovered if m not in configured]

    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text or ""
        except Exception as exc:
            last_error = exc

    # Fallback: still return something useful from semantic search results.
    excerpt = context_chunks[0][:1200]
    return (
        "Gemini chat model is unavailable for this API key right now. "
        "Top matching excerpt from your PDF:\n\n"
        f"{excerpt}\n\n"
        f"(Tried models: {model_candidates}. Last error: {last_error})"
    )
