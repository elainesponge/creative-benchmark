"""
Twitter / X scraper — uses Tweepy v4 with Bearer Token (free tier, read-only).
Falls back to Nitter RSS if the API call fails (e.g. 402 Payment Required).

Set TWITTER_BEARER_TOKEN in your .env file.

If no token is configured the scraper goes straight to the Nitter fallback.
"""
import logging
import os
import re
from datetime import timezone, datetime
from email.utils import parsedate_to_datetime

import requests
import feedparser

logger = logging.getLogger(__name__)

try:
    import tweepy
    _TWEEPY_OK = True
except ImportError:
    _TWEEPY_OK = False
    logger.warning("[twitter] tweepy not installed — skipping Twitter API, using Nitter only")


# Keywords that suggest a feature announcement (not a reply/retweet noise)
_FEATURE_PATTERNS = re.compile(
    r"\b(launch|release|announc|introduc|new feature|update|ship|drop|now (support|available)|"
    r"beta|v\d+\.\d+|upgrade|improv|add(ed|ing)|present|debut)\b",
    re.I,
)

# Public Nitter instances to try in order
_NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.1d4.us",
    "https://nitter.net",
]


def _is_feature_tweet(text: str) -> bool:
    return bool(_FEATURE_PATTERNS.search(text))


def _parse_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.astimezone(timezone.utc).date().isoformat()
    except Exception:
        return None


def _scrape_nitter(handle: str) -> list[dict]:
    """Try each Nitter instance until one returns results."""
    for instance in _NITTER_INSTANCES:
        url = f"{instance}/{handle}/rss"
        try:
            resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            if not feed.entries:
                continue

            items = []
            for entry in feed.entries[:20]:
                text = entry.get("summary", "") or entry.get("title", "")
                # Strip HTML tags
                text = re.sub(r"<[^>]+>", "", text).strip()

                if not _is_feature_tweet(text):
                    continue

                # Build tweet URL from entry link, falling back to x.com
                source_url = entry.get("link", f"https://x.com/{handle}")
                source_url = source_url.replace(instance, "https://x.com")

                first_line = text.split("\n")[0].strip()
                feature_name = first_line[:80] + ("…" if len(first_line) > 80 else "")

                release_date = _parse_date(entry.get("published"))

                items.append({
                    "feature_name": feature_name,
                    "description":  text[:500],
                    "release_date": release_date,
                    "source_url":   source_url,
                    "source_type":  "twitter",
                })

            logger.info("[twitter/nitter] %s — got %d items from %s", handle, len(items), instance)
            return items

        except Exception as exc:
            logger.debug("[twitter/nitter] %s failed on %s: %s", handle, instance, exc)
            continue

    logger.warning("[twitter/nitter] all instances failed for @%s", handle)
    return []


class TwitterScraper:

    def __init__(self):
        self.token = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.client = None
        if _TWEEPY_OK and self.token:
            self.client = tweepy.Client(bearer_token=self.token, wait_on_rate_limit=True)

    def scrape(self, product: dict) -> list[dict]:
        handle = product.get("twitter_handle")
        if not handle:
            return []

        name = product["name"]
        logger.info("[twitter] %s — @%s", name, handle)

        # Try Twitter API first
        if self.client:
            try:
                user_resp = self.client.get_user(username=handle, user_fields=["id"])
                if not user_resp.data:
                    raise ValueError("no user data")
                user_id = user_resp.data.id

                tweets = self.client.get_users_tweets(
                    id=user_id,
                    max_results=20,
                    exclude=["replies", "retweets"],
                    tweet_fields=["created_at", "text"],
                )
                if not tweets.data:
                    raise ValueError("no tweets returned")

                items = []
                for tweet in tweets.data:
                    text = tweet.text or ""
                    if not _is_feature_tweet(text):
                        continue

                    first_line = text.split("\n")[0].strip()
                    feature_name = first_line[:80] + ("…" if len(first_line) > 80 else "")

                    release_date = None
                    if tweet.created_at:
                        release_date = tweet.created_at.astimezone(timezone.utc).date().isoformat()

                    tweet_url = f"https://x.com/{handle}/status/{tweet.id}"
                    items.append({
                        "feature_name": feature_name,
                        "description":  text[:500],
                        "release_date": release_date,
                        "source_url":   tweet_url,
                        "source_type":  "twitter",
                    })
                return items

            except Exception as exc:
                logger.warning("[twitter] API failed for %s (%s) — falling back to Nitter", name, exc)

        # Nitter RSS fallback
        return _scrape_nitter(handle)
