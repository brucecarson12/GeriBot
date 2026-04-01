"""
Chess.com routes api.chess.com through Cloudflare. Plain python-requests traffic is often
challenged or IP-blocked. We set a descriptive User-Agent (required by their docs) plus
common browser/API headers to reduce false blocks.

If you still see 403 HTML from Cloudflare, try:
  - CHESSCOM_CONTACT (email or support URL) in .env
  - CHESSCOM_USER_AGENT to replace the entire header
  - Running the bot from another network (e.g. home vs datacenter/VPN)
"""

import os

_configured = False


def _build_user_agent() -> str:
    # Chrome-style UA + app id; Cloudflare is stricter with bare bot strings.
    base = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 "
        "GeriDiscordBot/1.0"
    )
    override = (os.getenv("CHESSCOM_USER_AGENT") or "").strip()
    if override:
        return override
    contact = (os.getenv("CHESSCOM_CONTACT") or "").strip()
    if contact:
        return f"{base} (contact: {contact})"
    return base


def ensure_chesscom_configured() -> None:
    global _configured
    if _configured:
        return
    import chessdotcom.client as cdcl

    ua = _build_user_agent()
    h = cdcl.Client.request_config.setdefault("headers", {})
    h["User-Agent"] = ua
    # Helps some Cloudflare rules vs bare GETs
    h.setdefault("Accept", "application/json, text/plain, */*")
    h.setdefault("Accept-Language", "en-US,en;q=0.9")
    h.setdefault("Referer", "https://www.chess.com/")
    _configured = True
