#!/usr/bin/env python3
"""HTML email template for Mac Mini price alerts."""

from datetime import datetime, timezone

MODEL_COLORS = {
    "M4": {"bg": "#0071E3", "text": "#FFFFFF"},
    "M2": {"bg": "#34C759", "text": "#FFFFFF"},
    "M1": {"bg": "#FF9500", "text": "#FFFFFF"},
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
    colors = MODEL_COLORS.get(model, {"bg": "#86868B", "text": "#FFFFFF"})
    condition = _condition_label(listing.get("condition", ""))
    price = listing.get("price", 0)
    ram = listing.get("ram_gb") or "?"
    title = listing.get("title", "Mac Mini")
    url = listing.get("url", "#")

    return f"""
    <tr><td style="padding:0 0 2px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#FFFFFF;">
        <tr>
          <td style="padding:20px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="vertical-align:middle;">
                  <span style="display:inline-block;background:{colors['bg']};color:{colors['text']};font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:10px;font-weight:600;letter-spacing:0.8px;padding:4px 10px;border-radius:4px;text-transform:uppercase;">{model}</span>
                  <span style="display:inline-block;color:#86868B;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:12px;font-weight:500;padding-left:10px;">{ram} GB &nbsp;&middot;&nbsp; {condition}</span>
                </td>
                <td align="right" style="vertical-align:middle;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:22px;font-weight:600;color:#1D1D1F;letter-spacing:-0.5px;white-space:nowrap;">{price:.0f} &euro;</td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:10px;">
                  <span style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;color:#424245;line-height:1.5;">{title}</span>
                </td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:14px;">
                  <a href="{url}" target="_blank" style="display:inline-block;background:#1D1D1F;color:#FFFFFF;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:12px;font-weight:500;text-decoration:none;padding:9px 22px;border-radius:980px;letter-spacing:0.1px;">View listing &rarr;</a>
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
<body style="margin:0;padding:0;background:#F5F5F7;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F5F5F7;">
    <tr><td align="center" style="padding:0;">
      <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">

        <!-- Header -->
        <tr><td style="padding:44px 28px 32px 28px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:28px;font-weight:600;color:#1D1D1F;letter-spacing:-0.5px;line-height:1.15;">
              {count} new Mac Mini<br>listing{"s" if count != 1 else ""}
            </td></tr>
            <tr><td style="padding-top:8px;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:14px;color:#86868B;font-weight:400;letter-spacing:0.1px;">
              M1 / M2 / M4 &nbsp;&middot;&nbsp; 16 GB+ &nbsp;&middot;&nbsp; under 500 &euro;
            </td></tr>
          </table>
        </td></tr>

        <!-- Listings -->
        <tr><td style="padding:0 16px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-radius:14px;overflow:hidden;">
            {cards}
          </table>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:28px 28px 44px 28px;">
          <p style="margin:0;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:12px;color:#86868B;font-weight:400;">
            tori.fi &nbsp;&middot;&nbsp; {now}
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
