from typing import Iterable

import psycopg

from app.core.config import PGVECTOR_DSN


def _to_vector_literal(values: Iterable[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


def _get_conn():
    return psycopg.connect(PGVECTOR_DSN)


def _current_vector_typmod(conn: psycopg.Connection):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.atttypmod
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = 'pdf_chunks'
              AND n.nspname = 'public'
              AND a.attname = 'embedding'
              AND a.attnum > 0
              AND NOT a.attisdropped;
            """
        )
        row = cur.fetchone()
        return row[0] if row else None


def _ensure_schema(conn: psycopg.Connection, dim: int, allow_recreate: bool = False) -> None:
    if dim <= 0:
        raise ValueError("Vector dimension must be greater than zero.")

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        typmod = _current_vector_typmod(conn)
        # In this environment pgvector typmod equals the declared dimensions.
        expected_typmod = dim
        if typmod is None:
            cur.execute(
                f"""
                CREATE TABLE pdf_chunks (
                    id BIGSERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    embedding VECTOR({dim}) NOT NULL
                );
                """
            )
        elif typmod != expected_typmod:
            if not allow_recreate:
                raise ValueError(
                    f"Existing embedding dimension does not match query dimension. "
                    f"Expected {typmod}, got {dim}."
                )
            cur.execute("DROP TABLE IF EXISTS pdf_chunks;")
            cur.execute(
                f"""
                CREATE TABLE pdf_chunks (
                    id BIGSERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    embedding VECTOR({dim}) NOT NULL
                );
                """
            )

        if allow_recreate:
            cur.execute("DROP INDEX IF EXISTS pdf_chunks_embedding_idx;")
            # IVFFLAT supports up to 2000 dimensions. Above that, fall back to exact search.
            if dim <= 2000:
                cur.execute(
                    """
                    CREATE INDEX pdf_chunks_embedding_idx
                    ON pdf_chunks USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                    """
                )
    conn.commit()


def store_embeddings(embeddings: list[list[float]], chunks: list[str]) -> int:
    if not embeddings or not chunks:
        return 0

    if len(embeddings) != len(chunks):
        raise ValueError("Embeddings and chunks length mismatch.")

    with _get_conn() as conn:
        _ensure_schema(conn, len(embeddings[0]), allow_recreate=True)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE pdf_chunks;")
            rows = [(chunk, _to_vector_literal(embedding)) for chunk, embedding in zip(chunks, embeddings)]
            cur.executemany(
                "INSERT INTO pdf_chunks (chunk_text, embedding) VALUES (%s, %s::vector);",
                rows,
            )
            cur.execute("SELECT COUNT(*) FROM pdf_chunks;")
            total = cur.fetchone()[0]
        conn.commit()
    return total


def search(query_embedding: list[float], k: int = 3) -> list[str]:
    with _get_conn() as conn:
        _ensure_schema(conn, len(query_embedding), allow_recreate=False)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pdf_chunks;")
            total = cur.fetchone()[0]
            if total == 0:
                return []

            cur.execute(
                """
                SELECT chunk_text
                FROM pdf_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (_to_vector_literal(query_embedding), max(1, k)),
            )
            return [row[0] for row in cur.fetchall()]
