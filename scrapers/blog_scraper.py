"""
Blog / RSS scraper.

Strategy (in order of preference):
  1. Parse RSS/Atom feed if blog_rss is configured
  2. Fallback: fetch HTML and extract <article> / <h2> / <h3> links + summaries
"""
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S GMT",
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y-%m-%d",
]


def _parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.date().isoformat()
        except ValueError:
            pass
    # feedparser gives us a time_struct
    return raw[:10] if len(raw) >= 10 else raw


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


class BlogScraper(BaseScraper):

    def scrape(self, product: dict) -> list[dict]:
        name  = product["name"]
        rss   = product.get("blog_rss")
        blog  = product.get("blog_url")

        if rss:
            logger.info("[blog] %s — parsing RSS %s", name, rss)
            try:
                return self._from_rss(rss, product)
            except Exception as exc:
                logger.warning("[blog] %s RSS failed: %s — falling back to HTML", name, exc)

        if blog:
            logger.info("[blog] %s — scraping HTML %s", name, blog)
            try:
                return self._from_html(blog, product)
            except Exception as exc:
                logger.warning("[blog] %s HTML scrape failed: %s", name, exc)

        return []

    # ── RSS ──────────────────────────────────────────────────────────────────

    def _from_rss(self, rss_url: str, product: dict) -> list[dict]:
        resp  = self.get(rss_url)
        feed  = feedparser.parse(resp.text)
        items = []
        for entry in feed.entries[:20]:          # latest 20 posts
            title = _clean(entry.get("title", ""))
            summary = _clean(
                entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
            )
            # strip HTML tags from summary
            summary = BeautifulSoup(summary, "lxml").get_text(" ", strip=True)[:500]
            pub = entry.get("published") or entry.get("updated") or ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                import time as _time
                pub = datetime.fromtimestamp(
                    _time.mktime(entry.published_parsed), tz=timezone.utc
                ).date().isoformat()
            else:
                pub = _parse_date(pub)

            link = entry.get("link", rss_url)
            if title:
                items.append({
                    "feature_name": title,
                    "description":  summary or title,
                    "release_date": pub,
                    "source_url":   link,
                    "source_type":  "blog",
                })
        return items

    # ── HTML fallback ─────────────────────────────────────────────────────────

    def _from_html(self, blog_url: str, product: dict) -> list[dict]:
        resp = self.get(blog_url)
        soup = BeautifulSoup(resp.text, "lxml")
        items = []

        # Generic strategy: find article cards
        cards = (
            soup.select("article")
            or soup.select("[class*='post']")
            or soup.select("[class*='blog']")
            or soup.select("[class*='news']")
            or soup.select("[class*='card']")
        )

        for card in cards[:20]:
            heading = card.find(re.compile(r"^h[1-4]$"))
            if not heading:
                continue
            title = _clean(heading.get_text())
            if not title:
                continue

            a_tag = heading.find("a") or card.find("a")
            link  = urljoin(blog_url, a_tag["href"]) if a_tag and a_tag.get("href") else blog_url

            # summary: <p> inside card
            p = card.find("p")
            summary = _clean(p.get_text()) if p else ""

            # date: <time> tag or text matching date pattern
            time_tag = card.find("time")
            if time_tag:
                pub = _parse_date(time_tag.get("datetime") or time_tag.get_text())
            else:
                date_text = card.find(string=re.compile(
                    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b|\d{4}-\d{2}-\d{2}"
                ))
                pub = _parse_date(date_text) if date_text else None

            items.append({
                "feature_name": title,
                "description":  summary or title,
                "release_date": pub,
                "source_url":   link,
                "source_type":  "blog",
            })

        return items
