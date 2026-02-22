# Creative Benchmark

A feature benchmarking tool that tracks product updates across 25 AI and non-AI creative tools. Scrapes blogs and App Store release notes daily, stores them in a searchable database, and surfaces them via a web UI with semantic search.

## Products tracked

**AI tools** — Runway, Kling, Pika, Pixverse, Vidu, Higgsfield, Heygen, Midjourney, Leonardo, Adobe Firefly, ElevenLabs, OpusClip, Lovart, Krea, Google Flow, Google Vids

**Non-AI tools** — Canva, Adobe Express, Figma, TikTok Studio, YouTube Create, Adobe Premiere, Filmora, InShot, Splice

## Features

- Scrapes **blog posts** and **App Store release notes** for each product
- **Semantic search** powered by `sentence-transformers` (all-MiniLM-L6-v2)
- **Daily scheduled scrape** via APScheduler
- **REST API** for programmatic access
- Deduplicates features across runs

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Add environment variables
cp .env.example .env

# Run the web app
python main.py
```

Then open `http://127.0.0.1:5000`.

## API

| Endpoint | Description |
|---|---|
| `GET /api/features` | Browse features (filter by `product`, `category`) |
| `GET /api/search?q=...` | Semantic search |
| `GET /api/stats` | Scrape stats by product and category |
| `POST /api/scrape` | Trigger a manual scrape |

## Project structure

```
creative-benchmark/
├── config.py          # Product list and settings
├── main.py            # App entrypoint
├── scrapers/          # Blog and App Store scrapers
├── database/          # SQLite helpers
├── embeddings/        # Semantic search index
├── scheduler/         # Daily scrape job
└── web/               # Flask app and templates
```
