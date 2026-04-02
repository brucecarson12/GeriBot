"""Discord embeds for Chess.com commands."""

from __future__ import annotations

import discord

_COLOR_PROFILE_ONLINE = 0x81B64C
_COLOR_PROFILE_OFFLINE = 0x312E2B
_COLOR_LEADERBOARD = 0x769656

_MODE_LABELS = [
    ("bullet", "Bullet"),
    ("blitz", "Blitz"),
    ("rapid", "Rapid"),
    ("classical", "Classical"),
    ("correspondence", "Daily"),
]

_MAX_DESC = 4096
_MAX_FIELD = 1020


def _clip_field(text: str, max_len: int = _MAX_FIELD) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _format_followers(n: int) -> str:
    if n >= 1_000_000:
        v = n / 1_000_000
        s = f"{v:.1f}M"
        return s.replace(".0M", "M")
    if n >= 1_000:
        v = n / 1_000
        s = f"{v:.1f}k"
        return s.replace(".0k", "k")
    return str(n)


def _profile_description(profile: dict) -> str | None:
    lines: list[str] = []

    j = profile.get("joined_ts")
    if j is not None:
        lines.append(f"**Joined** <t:{int(j)}:D>")

    badges: list[str] = []
    if profile.get("verified"):
        badges.append("Verified")
    if profile.get("is_streamer"):
        badges.append("Streamer")
    if badges:
        lines.append(" · ".join(badges))

    for url in (profile.get("stream_urls") or [])[:3]:
        lines.append(f"[Stream]({url})")

    if not lines:
        return None
    body = "\n\n".join(lines) if len(lines) > 1 else lines[0]
    if len(body) > _MAX_DESC:
        return body[: _MAX_DESC - 20] + "\n… *(truncated)*"
    return body


def _about_field_value(profile: dict) -> str | None:
    parts: list[str] = []
    if profile.get("display_name"):
        parts.append(f"**Name:** {profile['display_name']}")
    if profile.get("location"):
        parts.append(f"**Location:** {profile['location']}")
    if profile.get("country_code"):
        parts.append(f"**Country:** {profile['country_code']}")
    fo = profile.get("followers")
    if fo is not None:
        parts.append(f"**Followers:** {_format_followers(int(fo))}")
    if not parts:
        return None
    return _clip_field("\n".join(parts))


def build_cdc_profile_embed(stats: dict, profile: dict) -> discord.Embed:
    title_parts = []
    if profile.get("title"):
        title_parts.append(profile["title"])
    title_parts.append(profile.get("chesscom_username") or stats.get("chesscom_username") or "Player")
    title = " ".join(title_parts)

    online = stats.get("online")
    if online is True:
        bar_color = _COLOR_PROFILE_ONLINE
    elif online is False:
        bar_color = _COLOR_PROFILE_OFFLINE
    else:
        bar_color = _COLOR_PROFILE_OFFLINE

    desc = _profile_description(profile)
    embed = discord.Embed(
        title=title[:256],
        url=profile.get("profile_url"),
        description=desc,
        color=bar_color,
    )
    avatar = profile.get("avatar_url")
    if avatar:
        embed.set_thumbnail(url=avatar)

    about = _about_field_value(profile)
    if about:
        embed.add_field(name="About", value=about, inline=False)

    th = stats.get("tactics_highest")
    if th is not None:
        embed.add_field(name="Tactics (high)", value=str(th), inline=True)

    c960 = stats.get("chess960_rating")
    if c960 is not None:
        embed.add_field(name="Chess960 daily", value=str(c960), inline=True)

    ratings: dict = stats.get("ratings") or {}
    for key, label in _MODE_LABELS:
        if key in ratings:
            embed.add_field(name=label, value=str(ratings[key]), inline=True)

    pr = stats.get("puzzle_rush_best")
    if pr is not None:
        embed.add_field(name="Puzzle Rush", value=str(pr), inline=True)

    return embed


def build_cdc_leaderboard_embed(perf: str, perf_label: str, rows: list[tuple[str, int]]) -> discord.Embed:
    value_label = "Best score" if perf == "streak" else "Rating"
    embed = discord.Embed(
        title=f"Chess.com leaderboard — {perf_label}",
        color=_COLOR_LEADERBOARD,
    )
    if not rows:
        embed.description = f"No {value_label.lower()}s could be loaded for registered players."
        return embed

    lines = []
    for i, (user, val) in enumerate(rows, 1):
        lines.append(f"**{i}.** `{user}` — **{val}**")
    body = "\n".join(lines)
    if len(body) > _MAX_DESC:
        body = body[: _MAX_DESC - 20] + "\n… *(truncated)*"
    embed.description = body
    return embed
