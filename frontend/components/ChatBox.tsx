"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { sendChatMessage } from "@/lib/api";

export default function ChatBox(): JSX.Element {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setStatus("Searching your indexed PDF...");
    setAnswer("");

    try {
      const result = await sendChatMessage({ question });
      setAnswer(result.answer);
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to get answer");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <header className="top-nav">
        <div className="brand">Chat With PDF</div>
        <nav className="nav-links">
          <Link className="nav-link" href="/">Home</Link>
          <Link className="nav-link" href="/upload">Upload</Link>
        </nav>
      </header>

      <section className="panel">
        <h2>Ask Questions</h2>
        <p className="muted">Ask specific questions about your uploaded document. Answers are based on retrieved chunks.</p>

        <form onSubmit={onSubmit}>
          <textarea
            className="textarea"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: Summarize the key points from section 3."
          />

          <div className="row">
            <button className="btn" type="submit" disabled={isLoading}>
              {isLoading ? "Thinking..." : "Ask"}
            </button>
          </div>
        </form>

        {status ? <p className="status">{status}</p> : null}
        {answer ? <article className="answer">{answer}</article> : null}
      </section>
    </main>
  );
}
