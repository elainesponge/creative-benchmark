"""
Flask web application.
Routes:
  GET /              — browse latest features (filter by product / category)
  GET /search        — semantic search across feature descriptions
  GET /api/features  — JSON API for browsing
  GET /api/search    — JSON API for semantic search
  POST /api/scrape   — trigger a manual scrape run
"""
import logging
import sqlite3

from flask import Flask, render_template, request, jsonify, g

from config import DB_PATH, PRODUCTS

app = Flask(__name__)
logger = logging.getLogger(__name__)

# ── DB helpers ────────────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    product   = request.args.get("product", "")
    category  = request.args.get("category", "")
    page      = max(1, int(request.args.get("page", 1)))
    per_page  = 30
    offset    = (page - 1) * per_page

    db     = get_db()
    where  = []
    params = []

    if product:
        where.append("product_name = ?")
        params.append(product)
    if category:
        where.append("category = ?")
        params.append(category)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    total = db.execute(
        f"SELECT COUNT(*) FROM features {where_sql}", params
    ).fetchone()[0]

    rows = db.execute(
        f"""SELECT id, product_name, category, feature_name, description,
                   release_date, source_url, source_type, scraped_at
            FROM features {where_sql}
            ORDER BY release_date DESC NULLS LAST, scraped_at DESC
            LIMIT ? OFFSET ?""",
        params + [per_page, offset],
    ).fetchall()

    products   = [p["name"] for p in PRODUCTS]
    categories = ["ai", "non-ai"]

    return render_template(
        "index.html",
        features=rows,
        products=products,
        categories=categories,
        selected_product=product,
        selected_category=category,
        page=page,
        per_page=per_page,
        total=total,
        pages=(total + per_page - 1) // per_page,
    )


@app.route("/search")
def search_page():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        from embeddings.search import semantic_search, load_all_embeddings
        load_all_embeddings()
        hits = semantic_search(query, top_k=20)

        if hits:
            db  = get_db()
            ids = [h[0] for h in hits]
            score_map = {h[0]: h[1] for h in hits}

            placeholders = ",".join("?" * len(ids))
            rows = db.execute(
                f"""SELECT id, product_name, category, feature_name, description,
                           release_date, source_url, source_type
                    FROM features WHERE id IN ({placeholders})""",
                ids,
            ).fetchall()

            # Attach score and sort by score
            results = sorted(
                [{"row": r, "score": score_map[r["id"]]} for r in rows],
                key=lambda x: x["score"],
                reverse=True,
            )

    return render_template("search.html", query=query, results=results)


# ── JSON API ──────────────────────────────────────────────────────────────────

@app.route("/api/features")
def api_features():
    product  = request.args.get("product", "")
    category = request.args.get("category", "")
    limit    = min(100, int(request.args.get("limit", 50)))
    offset   = int(request.args.get("offset", 0))

    db     = get_db()
    where  = []
    params = []

    if product:
        where.append("product_name = ?")
        params.append(product)
    if category:
        where.append("category = ?")
        params.append(category)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = db.execute(
        f"""SELECT id, product_name, category, feature_name, description,
                   release_date, source_url, source_type, scraped_at
            FROM features {where_sql}
            ORDER BY release_date DESC NULLS LAST, scraped_at DESC
            LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter required"}), 400

    from embeddings.search import semantic_search, load_all_embeddings
    load_all_embeddings()
    hits = semantic_search(query, top_k=20)
    if not hits:
        return jsonify([])

    db  = get_db()
    ids = [h[0] for h in hits]
    score_map = {h[0]: h[1] for h in hits}

    placeholders = ",".join("?" * len(ids))
    rows = db.execute(
        f"""SELECT id, product_name, category, feature_name, description,
                   release_date, source_url, source_type
            FROM features WHERE id IN ({placeholders})""",
        ids,
    ).fetchall()

    data = sorted(
        [dict(r) | {"score": round(score_map[r["id"]], 4)} for r in rows],
        key=lambda x: x["score"],
        reverse=True,
    )
    return jsonify(data)


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    """Trigger a manual scrape in a background thread."""
    import threading
    from scheduler.jobs import run_scrape

    t = threading.Thread(target=run_scrape, daemon=True)
    t.start()
    return jsonify({"status": "started"})


@app.route("/api/stats")
def api_stats():
    db = get_db()
    total    = db.execute("SELECT COUNT(*) FROM features").fetchone()[0]
    by_prod  = db.execute(
        "SELECT product_name, COUNT(*) as cnt FROM features GROUP BY product_name ORDER BY cnt DESC"
    ).fetchall()
    by_cat   = db.execute(
        "SELECT category, COUNT(*) as cnt FROM features GROUP BY category"
    ).fetchall()
    last_run = db.execute(
        "SELECT run_at, status FROM scrape_log ORDER BY run_at DESC LIMIT 1"
    ).fetchone()
    return jsonify({
        "total_features": total,
        "by_product":  [dict(r) for r in by_prod],
        "by_category": [dict(r) for r in by_cat],
        "last_scrape": dict(last_run) if last_run else None,
    })
