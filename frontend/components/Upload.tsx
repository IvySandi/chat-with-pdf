"use client";

import Link from "next/link";
import { useState, type ChangeEvent } from "react";

import { uploadPdf } from "@/lib/api";

export default function Upload(): JSX.Element {
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function onFileChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const selected = event.target.files?.[0];
    if (!selected) return;

    try {
      setIsLoading(true);
      setStatus("Uploading and indexing PDF...");
      const result = await uploadPdf(selected);
      const chunksText = result.chunks ? ` Indexed ${result.chunks} chunks.` : "";
      const storedText = result.stored ? ` Stored ${result.stored} vectors.` : "";
      setStatus(`${result.message}.${chunksText}${storedText}`.replace("..", "."));
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to upload PDF");
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
          <Link className="nav-link" href="/chat">Chat</Link>
        </nav>
      </header>

      <section className="panel">
        <h2>Upload Document</h2>
        <p className="muted">Choose one PDF file. We will chunk, embed, and store vectors for semantic search.</p>

        <input
          className="file"
          type="file"
          accept="application/pdf"
          onChange={onFileChange}
          disabled={isLoading}
        />

        {status ? <p className="status">{status}</p> : null}
      </section>
    </main>
  );
}
