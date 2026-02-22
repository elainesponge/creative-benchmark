"""
App Store scraper — uses Apple's public iTunes Lookup API (no auth required).
Endpoint: https://itunes.apple.com/lookup?id=<app_id>&country=us
"""
import logging
import re
from datetime import datetime

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

LOOKUP_URL = "https://itunes.apple.com/lookup"

# Version note lines we don't want
_NOISE = re.compile(
    r"^(bug fix(es)?|performance improvement|minor fix|stability|this (version|update)|thank you)",
    re.I,
)


def _split_release_notes(notes: str) -> list[str]:
    """Split the 'releaseNotes' blob into individual bullet points / sentences."""
    if not notes:
        return []

    # Try splitting on bullet-like patterns first
    bullets = re.split(r"[\n\r•\-–—]+", notes)
    results = []
    for b in bullets:
        b = b.strip(" .,;")
        if len(b) > 15 and not _NOISE.match(b):
            results.append(b)
    return results[:10]      # cap at 10 items per update


class AppStoreScraper(BaseScraper):

    def scrape(self, product: dict) -> list[dict]:
        app_id = product.get("appstore_id")
        if not app_id:
            return []

        name = product["name"]
        logger.info("[appstore] %s — id %s", name, app_id)

        try:
            resp = self.get(LOOKUP_URL, params={"id": app_id, "country": "us"})
            data = resp.json()
        except Exception as exc:
            logger.warning("[appstore] %s failed: %s", name, exc)
            return []

        results = data.get("results", [])
        if not results:
            return []

        app = results[0]
        notes   = app.get("releaseNotes", "")
        version = app.get("version", "")
        raw_date = app.get("currentVersionReleaseDate", "")

        # Parse date
        release_date = None
        if raw_date:
            try:
                release_date = datetime.fromisoformat(
                    raw_date.replace("Z", "+00:00")
                ).date().isoformat()
            except ValueError:
                release_date = raw_date[:10]

        app_url = app.get("trackViewUrl", "")
        items   = []

        features = _split_release_notes(notes)
        if not features:
            # treat the whole note as one item
            clean = (notes or "").strip()
            if clean:
                features = [clean[:300]]

        for feat in features:
            items.append({
                "feature_name": f"v{version}: {feat[:80]}" if version else feat[:80],
                "description":  feat,
                "release_date": release_date,
                "source_url":   app_url,
                "source_type":  "appstore",
            })

        return items
