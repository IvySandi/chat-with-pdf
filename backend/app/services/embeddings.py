import google.generativeai as genai

from app.core.config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

genai.configure(api_key=GEMINI_API_KEY)


def _resolve_embedding_model(model_name: str) -> str:
    cleaned = model_name.strip()
    if cleaned in {"text-embedding-004", "models/text-embedding-004"}:
        return "models/gemini-embedding-001"
    if "/" not in cleaned:
        return f"models/{cleaned}"
    return cleaned


def get_embeddings(texts, task_type: str = "retrieval_document"):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in backend/.env")
    if not texts:
        return []

    # Batch texts in fewer API calls so upload does not appear stuck on large PDFs.
    response = genai.embed_content(
        model=_resolve_embedding_model(GEMINI_EMBEDDING_MODEL),
        content=texts,
        task_type=task_type,
        request_options={"timeout": 60},
    )

    # SDK response shape differs by version:
    # - single: {"embedding": [..]}
    # - batch: {"embedding": [[..], [..]]} or {"embeddings": [{"values":[..]}, ...]}
    if hasattr(response, "to_dict"):
        data = response.to_dict()
    elif isinstance(response, dict):
        data = response
    else:
        data = {}

    if "embedding" in data:
        emb = data["embedding"]
        if emb and isinstance(emb, list) and isinstance(emb[0], (float, int)):
            return [emb]
        if emb and isinstance(emb, list) and isinstance(emb[0], list):
            return emb

    if "embeddings" in data:
        items = data["embeddings"] or []
        vectors = []
        for item in items:
            if isinstance(item, dict) and "values" in item:
                vectors.append(item["values"])
            elif isinstance(item, list):
                vectors.append(item)
        if vectors:
            return vectors

    raise ValueError(f"Unexpected Gemini embedding response format: {data}")
