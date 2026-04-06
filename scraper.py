#!/usr/bin/env python3
"""Scrapes tori.fi for used Mac Mini listings matching our criteria."""

import json
import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.tori.fi/recommerce/forsale/search"
PARAMS = {"q": "mac mini", "price_to": "500"}
MAX_PAGES = 4

# Models we care about and their regex patterns
MODEL_PATTERNS = {
    "M4": re.compile(r"\bM4\b", re.IGNORECASE),
    "M2": re.compile(r"\bM2\b", re.IGNORECASE),
    "M1": re.compile(r"\bM1\b", re.IGNORECASE),
}

# Patterns for RAM extraction — titles use formats like:
# "16 Gt/256 Gt", "8GB / 256GB SSD", "16GB RAM", "8/512 Gt"
# In a pair, RAM is always the smaller number.
RAM_PATTERNS = [
    # Both have units: "16 Gt/256 Gt", "8GB / 512GB"
    re.compile(r"(\d+)\s*(?:Gt|GB)\s*/\s*(\d+)\s*(?:Gt|GB)", re.IGNORECASE),
    # Only second has unit: "8/512 Gt", "8/256GB"
    re.compile(r"(\d+)\s*/\s*(\d+)\s*(?:Gt|GB)", re.IGNORECASE),
]
RAM_SOLO_PATTERN = re.compile(r"(\d+)\s*(?:Gt|GB)", re.IGNORECASE)


def parse_model(title: str) -> str | None:
    """Extract Mac Mini model (M1/M2/M4) from listing title."""
    for model, pattern in MODEL_PATTERNS.items():
        if pattern.search(title):
            return model
    return None


def parse_ram_gb(title: str) -> int | None:
    """Extract RAM in GB from listing title.

    Handles "16 Gt/256 Gt", "8/512 Gt", "16GB RAM" etc.
    In RAM/Storage pairs, RAM is always the smaller number.
    """
    for pattern in RAM_PATTERNS:
        match = pattern.search(title)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            ram = min(a, b)
            if ram >= 4:  # Filter out false positives like "M1 / 8gb" matching "1/8"
                return ram
    match = RAM_SOLO_PATTERN.search(title)
    if match:
        return int(match.group(1))
    return None


def fetch_page(session: requests.Session, page: int) -> list[dict]:
    """Fetch one page of search results and extract JSON-LD product data."""
    params = {**PARAMS, "page": str(page)}
    resp = session.get(SEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Find the CollectionPage JSON-LD script (there are multiple LD+JSON blocks)
    items = []
    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        data = json.loads(script.string)
        if data.get("@type") == "CollectionPage":
            items = data.get("mainEntity", {}).get("itemListElement", [])
            break

    if not items:
        return []

    listings = []
    for entry in items:
        product = entry.get("item", entry)
        if product.get("@type") != "Product":
            continue

        offers = product.get("offers", {})
        try:
            price = float(offers.get("price", 0))
        except (ValueError, TypeError):
            continue

        condition = product.get("itemCondition") or offers.get("itemCondition", "")

        listings.append({
            "title": product.get("name", ""),
            "price": price,
            "url": product.get("url", ""),
            "condition": condition,
            "image": product.get("image", ""),
        })

    return listings


def scrape_tori() -> list[dict]:
    """Scrape all pages of Mac Mini listings from tori.fi and filter to matching ones."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9",
    })

    all_listings = []
    for page in range(1, MAX_PAGES + 1):
        try:
            listings = fetch_page(session, page)
            if not listings:
                break
            all_listings.extend(listings)
            logger.info(f"Page {page}: {len(listings)} listings")
        except Exception:
            logger.exception(f"Failed to fetch page {page}")
            break

    # Filter: M1/M2/M4, price <= 500€, exclude only if RAM is explicitly < 16GB
    matched = []
    for listing in all_listings:
        title = listing["title"]
        model = parse_model(title)
        if not model:
            continue

        if listing["price"] > 500:
            continue

        ram = parse_ram_gb(title)
        if ram is not None and ram < 16:
            continue

        listing["model"] = model
        listing["ram_gb"] = ram
        matched.append(listing)

    logger.info(f"Total scraped: {len(all_listings)}, matched filters: {len(matched)}")
    return matched


def extract_listing_id(url: str) -> str:
    """Extract tori listing ID from URL."""
    return "tori_" + url.rstrip("/").split("/")[-1]
