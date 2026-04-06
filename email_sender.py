#!/usr/bin/env python3
"""Send email alerts for new Mac Mini listings via Resend API."""

import logging

import requests

from email_template import render_email

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def send_alert(listings: list[dict], api_key: str, email_to: str) -> bool:
    """Send an email alert for new Mac Mini listings."""
    count = len(listings)
    subject = f"🖥️ {count} new Mac Mini listing{'s' if count != 1 else ''} on Tori.fi"

    html = render_email(listings)

    resp = requests.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "from": "Mac Mini Tracker <onboarding@resend.dev>",
            "to": [email_to],
            "subject": subject,
            "html": html,
        },
        timeout=15,
    )

    if resp.status_code == 200:
        logger.info(f"Alert sent to {email_to} ({count} listings)")
        return True
    else:
        logger.error(f"Email failed: {resp.status_code} {resp.text}")
        return False
