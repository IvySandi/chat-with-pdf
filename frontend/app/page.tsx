import Link from "next/link";

export default function HomePage(): JSX.Element {
  return (
    <main className="page-shell">
      <header className="top-nav">
        <div className="brand">Chat With PDF</div>
        <nav className="nav-links">
          <Link className="nav-link" href="/upload">Upload</Link>
          <Link className="nav-link" href="/chat">Chat</Link>
        </nav>
      </header>

      <section className="hero">
        <h1>Turn any PDF into a searchable conversation.</h1>
        <p>
          Upload a document, index it with embeddings, and ask grounded questions.
          Built for focused research, quick document analysis, and reliable retrieval.
        </p>

        <div className="grid">
          <article className="card">
            <h3>1. Upload & Index</h3>
            <p>Send your PDF and build semantic chunks for fast retrieval.</p>
            <Link className="btn" href="/upload">Go to Upload</Link>
          </article>

          <article className="card">
            <h3>2. Ask Questions</h3>
            <p>Query your indexed document and get context-grounded responses.</p>
            <Link className="btn" href="/chat">Open Chat</Link>
          </article>
        </div>
      </section>
    </main>
  );
}
