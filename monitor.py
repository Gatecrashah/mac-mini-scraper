#!/usr/bin/env python3
"""Main monitor: scrapes, detects new listings, sends alerts, updates history."""

import json
import logging
import os
from datetime import datetime, timezone

from email_sender import send_alert
from scraper import extract_listing_id, scrape_tori

HISTORY_FILE = "listings.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_history(history: dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def main():
    logger.info("Starting Mac Mini price monitor")
    history = load_history()
    now = datetime.now(timezone.utc).isoformat()

    # Mark all existing listings as possibly inactive
    for lid in history:
        history[lid]["active"] = False

    listings = scrape_tori()
    new_listings = []

    for listing in listings:
        lid = extract_listing_id(listing["url"])

        if lid in history:
            # Still active — update last_seen and price
            history[lid]["active"] = True
            history[lid]["last_seen"] = now
            if listing["price"] != history[lid]["price"]:
                history[lid]["price"] = listing["price"]
        else:
            # New listing
            history[lid] = {
                "title": listing["title"],
                "model": listing["model"],
                "ram_gb": listing["ram_gb"],
                "price": listing["price"],
                "url": listing["url"],
                "condition": listing["condition"],
                "image": listing["image"],
                "first_seen": now,
                "last_seen": now,
                "active": True,
                "notified": False,
            }
            new_listings.append(history[lid])

    logger.info(
        f"Active: {sum(1 for v in history.values() if v['active'])}, "
        f"New: {len(new_listings)}, "
        f"Total tracked: {len(history)}"
    )

    # Send email for new listings
    if new_listings:
        # Mark as notified before sending so we don't double-send on failure+retry
        for nl in new_listings:
            nl["notified"] = True

        api_key = os.getenv("RESEND_API_KEY")
        email_to = os.getenv("EMAIL_TO")
        if api_key and email_to:
            send_alert(new_listings, api_key, email_to)
        else:
            logger.warning("RESEND_API_KEY or EMAIL_TO not set, skipping email")

    save_history(history)
    logger.info("Done")


if __name__ == "__main__":
    main()
