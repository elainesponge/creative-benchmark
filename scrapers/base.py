"""
Base scraper with shared HTTP helpers and retry logic.
"""
import time
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES, USER_AGENT

logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        })

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True,
    )
    def get(self, url: str, **kwargs) -> requests.Response:
        resp = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return resp

    def scrape(self, product: dict) -> list[dict]:
        """
        Override in subclasses.
        Returns a list of dicts with keys:
            feature_name, description, release_date, source_url, source_type
        """
        raise NotImplementedError
