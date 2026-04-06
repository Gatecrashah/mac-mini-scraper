#!/usr/bin/env python3
"""HTML email template for Mac Mini price alerts."""

from datetime import datetime, timezone

MODEL_COLORS = {
    "M4": {"bg": "#3B82F6", "text": "#FFFFFF"},
    "M2": {"bg": "#10B981", "text": "#FFFFFF"},
    "M1": {"bg": "#F59E0B", "text": "#1A1207"},
}

CONDITION_MAP = {
    "https://schema.org/UsedCondition": "Used",
    "https://schema.org/NewCondition": "New",
    "https://schema.org/RefurbishedCondition": "Refurbished",
    "https://schema.org/DamagedCondition": "Damaged",
}


def _condition_label(raw: str) -> str:
    return CONDITION_MAP.get(raw, raw.replace("https://schema.org/", "").replace("Condition", ""))


def _listing_card(listing: dict) -> str:
    model = listing.get("model", "?")
    colors = MODEL_COLORS.get(model, {"bg": "#6B7280", "text": "#FFFFFF"})
    condition = _condition_label(listing.get("condition", ""))
    price = listing.get("price", 0)
    ram = listing.get("ram_gb") or "?"
    title = listing.get("title", "Mac Mini")
    url = listing.get("url", "#")

    return f"""
    <tr><td style="padding:0 0 12px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#1E293B;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="padding:16px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td>
                  <span style="display:inline-block;background:{colors['bg']};color:{colors['text']};font-family:'SF Pro Display',Helvetica,Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:0.5px;padding:3px 10px;border-radius:6px;text-transform:uppercase;">{model}</span>
                  <span style="display:inline-block;background:#334155;color:#94A3B8;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:11px;font-weight:500;padding:3px 8px;border-radius:6px;margin-left:6px;">{ram} GB</span>
                  <span style="display:inline-block;background:#334155;color:#94A3B8;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:11px;font-weight:500;padding:3px 8px;border-radius:6px;margin-left:4px;">{condition}</span>
                </td>
                <td align="right" style="font-family:'SF Pro Display',Helvetica,Arial,sans-serif;font-size:24px;font-weight:700;color:#FDE68A;white-space:nowrap;">{price:.0f}&thinsp;&euro;</td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:8px;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:14px;color:#CBD5E1;line-height:1.4;">{title}</td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:12px;">
                  <a href="{url}" target="_blank" style="display:inline-block;background:#EF4444;color:#FFFFFF;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:13px;font-weight:600;text-decoration:none;padding:8px 20px;border-radius:8px;">View on Tori.fi &rarr;</a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td></tr>"""


def render_email(listings: list[dict]) -> str:
    """Render HTML email for new Mac Mini listings, sorted by price ascending."""
    sorted_listings = sorted(listings, key=lambda x: x.get("price", 0))
    count = len(sorted_listings)
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")

    cards = "".join(_listing_card(l) for l in sorted_listings)

    return f"""<!DOCTYPE html>
<html lang="fi">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0F172A;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#0F172A;">
    <tr><td align="center" style="padding:0;">
      <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">

        <!-- Header -->
        <tr><td style="padding:32px 24px 24px 24px;text-align:center;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr><td align="center">
              <span style="display:inline-block;width:40px;height:40px;background:#1E293B;border-radius:10px;line-height:40px;font-size:20px;text-align:center;">&#9724;</span>
            </td></tr>
            <tr><td align="center" style="padding-top:14px;font-family:'SF Pro Display',Helvetica,Arial,sans-serif;font-size:22px;font-weight:700;color:#F1F5F9;letter-spacing:-0.3px;">
              {count} new Mac Mini listing{"s" if count != 1 else ""}
            </td></tr>
            <tr><td align="center" style="padding-top:4px;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:13px;color:#64748B;">
              M1 / M2 / M4 &middot; 16 GB+ &middot; under 500&thinsp;&euro;
            </td></tr>
          </table>
        </td></tr>

        <!-- Listings -->
        <tr><td style="padding:0 16px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            {cards}
          </table>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:20px 24px 32px 24px;text-align:center;">
          <p style="margin:0;font-family:'SF Pro Text',Helvetica,Arial,sans-serif;font-size:11px;color:#475569;">
            Scraped from tori.fi &middot; {now}
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
