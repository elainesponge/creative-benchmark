"""
Semantic similarity search using sentence-transformers.

Model: all-MiniLM-L6-v2  (~80 MB, fast, good quality)

Embeddings are stored as pickled numpy arrays in the `embeddings` table.
On startup (or after new inserts) they're loaded into memory for fast cosine search.
"""
import logging
import pickle
import sqlite3

import numpy as np

from config import DB_PATH

logger = logging.getLogger(__name__)

_MODEL = None        # lazy-loaded
_CACHE: dict[int, np.ndarray] = {}   # feature_id → embedding vector


def _model():
    global _MODEL
    if _MODEL is None:
        logger.info("[embeddings] Loading sentence-transformer model…")
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("[embeddings] Model ready.")
    return _MODEL


def embed_text(text: str) -> np.ndarray:
    return _model().encode(text, normalize_embeddings=True).astype("float32")


# ── Persistence ──────────────────────────────────────────────────────────────

def save_embedding(feature_id: int, vector: np.ndarray):
    blob = pickle.dumps(vector)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO embeddings (feature_id, vector) VALUES (?,?)
           ON CONFLICT(feature_id) DO UPDATE SET vector=excluded.vector""",
        (feature_id, blob),
    )
    conn.commit()
    conn.close()
    _CACHE[feature_id] = vector


def load_all_embeddings():
    """Load all stored embeddings into memory cache."""
    global _CACHE
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT feature_id, vector FROM embeddings").fetchall()
    conn.close()
    _CACHE = {row[0]: pickle.loads(row[1]) for row in rows}
    logger.info("[embeddings] Loaded %d vectors into cache.", len(_CACHE))


def embed_new_features():
    """Find features without embeddings and compute + store them."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT f.id, f.feature_name, f.description
           FROM features f
           LEFT JOIN embeddings e ON e.feature_id = f.id
           WHERE e.feature_id IS NULL"""
    ).fetchall()
    conn.close()

    if not rows:
        return

    logger.info("[embeddings] Computing embeddings for %d new features…", len(rows))
    texts = [f"{r[1]}. {r[2]}" for r in rows]
    vectors = _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)

    for (fid, _, _), vec in zip(rows, vectors):
        save_embedding(fid, vec.astype("float32"))

    logger.info("[embeddings] Done.")


# ── Search ────────────────────────────────────────────────────────────────────

def semantic_search(query: str, top_k: int = 20) -> list[tuple[int, float]]:
    """
    Returns [(feature_id, score), …] sorted by descending cosine similarity.
    Cosine similarity is trivial since all vectors are L2-normalised.
    """
    if not _CACHE:
        load_all_embeddings()
    if not _CACHE:
        return []

    q_vec = embed_text(query)

    ids     = list(_CACHE.keys())
    matrix  = np.stack([_CACHE[i] for i in ids])   # (N, D)
    scores  = matrix @ q_vec                         # cosine sim

    top_idx = np.argsort(scores)[::-1][:top_k]
    return [(ids[i], float(scores[i])) for i in top_idx]
