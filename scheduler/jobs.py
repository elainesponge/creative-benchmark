"""
APScheduler job: scrape all products daily and rebuild embeddings.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from config import PRODUCTS, SCRAPE_HOUR, SCRAPE_MINUTE
from database.db import insert_feature, log_scrape
from scrapers.blog_scraper import BlogScraper
from scrapers.appstore_scraper import AppStoreScraper
from embeddings.search import embed_new_features

logger = logging.getLogger(__name__)


def run_scrape():
    """Scrape all products from all sources."""
    logger.info("[scheduler] Starting scrape run…")
    blog_scraper     = BlogScraper()
    appstore_scraper = AppStoreScraper()

    for product in PRODUCTS:
        name     = product["name"]
        category = product["category"]

        scrapers = [
            ("blog",     blog_scraper),
            ("appstore", appstore_scraper),
        ]

        for source_type, scraper in scrapers:
            try:
                items = scraper.scrape(product)
                added = 0
                for item in items:
                    fid = insert_feature(
                        product_name=name,
                        category=category,
                        feature_name=item["feature_name"],
                        description=item["description"],
                        release_date=item.get("release_date"),
                        source_url=item.get("source_url"),
                        source_type=item["source_type"],
                    )
                    if fid is not None:
                        added += 1
                log_scrape(name, source_type, "ok", items_added=added)
                logger.info("[scheduler] %s / %s — %d new items", name, source_type, added)
            except Exception as exc:
                msg = str(exc)
                log_scrape(name, source_type, "error", message=msg)
                logger.error("[scheduler] %s / %s error: %s", name, source_type, msg)

    # Rebuild embeddings for newly inserted features
    try:
        embed_new_features()
    except Exception as exc:
        logger.error("[scheduler] Embedding failed: %s", exc)

    logger.info("[scheduler] Scrape run complete.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_scrape,
        trigger="cron",
        hour=SCRAPE_HOUR,
        minute=SCRAPE_MINUTE,
        id="daily_scrape",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[scheduler] Scheduled daily scrape at %02d:%02d.", SCRAPE_HOUR, SCRAPE_MINUTE)
    return scheduler
