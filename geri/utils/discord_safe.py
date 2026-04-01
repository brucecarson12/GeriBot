"""Keep outbound Discord text within limits."""

DISCORD_CONTENT_MAX = 2000
SAFE_MAX = 1900


def clip_message(text: str, max_len: int = SAFE_MAX) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def user_facing_error(exc: BaseException) -> str:
    """Short message for users; full detail stays in logs."""
    name = type(exc).__name__
    try:
        from chessdotcom.errors import ChessDotComClientError

        if isinstance(exc, ChessDotComClientError):
            body = (exc.text or "")[:2000]
            if (
                "Just a moment" in body
                or "__cf_chl" in body
                or "challenge-platform" in body
                or "Sorry, you have been blocked" in body
                or "Attention Required!" in body
                or "cf-error-details" in body
            ):
                return (
                    f"{name} ({exc.status_code}): Chess.com / Cloudflare blocked this request "
                    "(not a bad username). Try: set CHESSCOM_USER_AGENT in .env with a clear "
                    "name + contact; run the bot from another network if you’re on VPN/datacenter; "
                    "wait and retry. The public API cannot pass browser CAPTCHAs."
                )
            return clip_message(
                f"{name} (HTTP {exc.status_code}) from Chess.com API. "
                f"If the player exists, try again; otherwise check the username."
            )
    except Exception:
        pass
    raw = str(exc).strip()
    if len(raw) > 300:
        raw = raw[:297] + "…"
    return clip_message(f"{name}: {raw}" if raw else name)
