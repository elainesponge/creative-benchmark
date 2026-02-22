"""
Entry point.

Usage:
  python main.py                 # start web server + daily scheduler
  python main.py --scrape        # run a one-off scrape and exit
  python main.py --embed         # (re)build embeddings for all features
"""
import argparse
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def main():
    parser = argparse.ArgumentParser(description="Creative Benchmark")
    parser.add_argument("--scrape", action="store_true", help="Run scrape once and exit")
    parser.add_argument("--embed",  action="store_true", help="Rebuild embeddings and exit")
    parser.add_argument("--host",   default="127.0.0.1")
    parser.add_argument("--port",   default=5000, type=int)
    parser.add_argument("--debug",  action="store_true")
    args = parser.parse_args()

    # Ensure DB is initialised
    from database.db import init_db
    init_db()

    if args.scrape:
        from scheduler.jobs import run_scrape
        run_scrape()
        sys.exit(0)

    if args.embed:
        from embeddings.search import embed_new_features
        embed_new_features()
        sys.exit(0)

    # Start daily scheduler
    from scheduler.jobs import start_scheduler
    scheduler = start_scheduler()

    # Start Flask
    from web.app import app
    logger.info("Starting web server at http://%s:%d", args.host, args.port)
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
