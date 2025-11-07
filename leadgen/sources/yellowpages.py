from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup, Tag

from ..models import Lead

USER_AGENT = "Mozilla/5.0"

RATING_CLASS_MAP = {
    "zero": 0.0,
    "one": 1.0,
    "onehalf": 1.5,
    "two": 2.0,
    "twohalf": 2.5,
    "three": 3.0,
    "threehalf": 3.5,
    "four": 4.0,
    "fourhalf": 4.5,
    "five": 5.0,
}


@dataclass
class YellowPagesScraper:
    """Scrape lead data from YellowPages for a given city and query."""

    city: str
    state: str
    session: Optional[requests.Session] = None
    user_agent: str = USER_AGENT

    def __post_init__(self) -> None:
        self._headers: Dict[str, str] = {
            "User-Agent": self.user_agent,
        }
        if self.session is not None:
            self.session.headers.update(self._headers)

    def fetch(self, query: str, max_pages: int = 1) -> List[Lead]:
        """Fetch listing leads for a given search query."""

        leads: List[Lead] = []
        for page in range(1, max_pages + 1):
            html = self._get_listing_page(query, page)
            if html is None:
                break
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("div.result")
            if not items:
                break
            for item in items:
                lead = self._parse_result(item, query)
                if lead:
                    leads.append(lead)
        return leads

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_listing_page(self, query: str, page: int) -> Optional[str]:
        url = self._build_url(query, page)
        request_kwargs = {"timeout": 20, "headers": self._headers}
        if self.session is not None:
            response = self.session.get(url, **request_kwargs)
        else:
            response = requests.get(url, **request_kwargs)
        if response.status_code >= 400:
            return None
        return response.text

    def _build_url(self, query: str, page: int) -> str:
        query_slug = self._slugify(query)
        location_slug = self._slugify(f"{self.city}-{self.state}")
        base = f"https://www.yellowpages.com/{location_slug}/{query_slug}"
        if page > 1:
            return f"{base}?{urlencode({'page': page})}"
        return base

    @staticmethod
    def _slugify(value: str) -> str:
        return re.sub(r"[^a-z0-9-]+", "-", value.lower().strip()).strip("-")

    def _parse_result(self, item: Tag, query: str) -> Optional[Lead]:
        name_el = item.select_one("a.business-name span")
        if name_el is None:
            return None
        name = name_el.text.strip()

        analytics_data = self._load_json(item.get("data-analytics"))
        description_el = item.select_one(".snippet") or item.select_one(".promo-title")
        categories_el = item.select_one(".categories")
        phone_el = item.select_one(".phones")
        website_el = item.select_one("a.track-visit-website")
        rating_el = item.select_one(".result-rating")
        review_count_el = item.select_one(".result-rating span.count")
        address_el = item.select_one(".street-address")
        locality_el = item.select_one(".locality")

        categories = (
            [category.strip() for category in categories_el.text.split("\n") if category.strip()]
            if categories_el
            else []
        )

        description = description_el.text.strip() if description_el else None
        phone = phone_el.text.strip() if phone_el else None
        website = (
            urljoin("https://www.yellowpages.com", website_el["href"])
            if website_el and website_el.get("href")
            else None
        )
        rating = self._parse_rating(rating_el)
        review_count = self._parse_review_count(review_count_el)
        location = self._build_location(address_el, locality_el)

        extras = {
            "query": query,
            "address": address_el.text.strip() if address_el else None,
        }

        return Lead(
            name=name,
            description=description,
            phone=phone,
            website=website,
            categories=categories,
            source="yellowpages",
            rating=rating,
            review_count=review_count,
            location=location,
            analytics=analytics_data,
            extras=extras,
        )

    @staticmethod
    def _load_json(value: Optional[str]) -> dict:
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _parse_rating(element: Optional[Tag]) -> Optional[float]:
        if element is None:
            return None
        for cls in element.get("class", []):
            if cls in RATING_CLASS_MAP:
                return RATING_CLASS_MAP[cls]
        return None

    @staticmethod
    def _parse_review_count(element: Optional[Tag]) -> Optional[int]:
        if element is None:
            return None
        text = element.text.strip()
        digits = re.findall(r"\d+", text)
        if not digits:
            return None
        try:
            return int(digits[0])
        except ValueError:
            return None

    @staticmethod
    def _build_location(address_el: Optional[Tag], locality_el: Optional[Tag]) -> Optional[str]:
        if not address_el and not locality_el:
            return None
        parts: List[str] = []
        if address_el:
            parts.append(address_el.text.strip())
        if locality_el:
            parts.append(locality_el.text.strip())
        return ", ".join(part for part in parts if part)
