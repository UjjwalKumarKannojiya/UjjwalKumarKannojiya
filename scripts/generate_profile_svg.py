#!/usr/bin/env python3
"""Generate an auto-updating GitHub profile card as a pure SVG.

The README embeds assets/profile-card.svg. GitHub Actions regenerates this file
from live GitHub profile/repository data, so the UI stays consistent while the
content changes automatically.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
SVG_PATH = ASSET_DIR / "profile-card.svg"
README_PATH = ROOT / "README.md"

GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
USERNAME = os.getenv("PROFILE_USERNAME") or os.getenv("GITHUB_REPOSITORY", "UjjwalKumarKannojiya").split("/")[0]
USERNAME = USERNAME.strip() or "UjjwalKumarKannojiya"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "auto-profile-readme-svg",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

COLORS = {
    "bg": "#0d1117",
    "panel": "#151b23",
    "panel2": "#111820",
    "border": "#30363d",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "white": "#f0f6fc",
    "blue": "#2f81f7",
    "purple": "#a371f7",
    "green": "#3fb950",
    "green2": "#26d968",
    "cyan": "#79c0ff",
    "darkgreen": "#003820",
}

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "C": "#555555",
    "C++": "#f34b7d",
    "R": "#198CE7",
    "PHP": "#4F5D95",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Vue": "#41b883",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Kotlin": "#A97BFF",
    "Swift": "#F05138",
}

TOPIC_LABELS = {
    "react": "React",
    "nextjs": "Next.js",
    "next-js": "Next.js",
    "tailwindcss": "Tailwind",
    "tailwind": "Tailwind",
    "nodejs": "Node.js",
    "node-js": "Node.js",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "appwrite": "Appwrite",
    "machine-learning": "Machine Learning",
    "ml": "ML",
    "ai": "AI",
    "data-science": "Data Science",
    "figma": "Figma",
    "uiux": "UI/UX",
    "ui-ux": "UI/UX",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "python": "Python",
    "java": "Java",
    "vite": "Vite",
    "bootstrap": "Bootstrap",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "scikit-learn",
}


def api_get(path: str, default: Any = None, *, raw_headers: bool = False) -> Any:
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            body = res.read().decode("utf-8")
            data = json.loads(body) if body else default
            if raw_headers:
                return data, dict(res.headers)
            return data
    except Exception as exc:
        print(f"[warn] GitHub API failed for {url}: {exc}", file=sys.stderr)
        return (default, {}) if raw_headers else default


def github_paginated(path: str, limit_pages: int = 5) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    url = f"{GITHUB_API}{path}"
    for _ in range(limit_pages):
        data, headers = api_get(url, [], raw_headers=True)
        if isinstance(data, list):
            items.extend(data)
        link = headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r"<([^>]+)>", part)
                if m:
                    next_url = m.group(1)
        if not next_url:
            break
        url = next_url
    return items


def parse_last_page_from_link(link: str) -> int | None:
    for part in link.split(","):
        if 'rel="last"' in part:
            m = re.search(r"[?&]page=(\d+)", part)
            if m:
                return int(m.group(1))
    return None


def commit_count_for_repo(repo: dict[str, Any]) -> int:
    owner = repo.get("owner", {}).get("login") or USERNAME
    name = repo.get("name")
    if not name:
        return 0
    encoded_author = urllib.parse.quote(USERNAME)
    path = f"/repos/{owner}/{name}/commits?author={encoded_author}&per_page=1"
    data, headers = api_get(path, [], raw_headers=True)
    if not isinstance(data, list) or not data:
        return 0
    last = parse_last_page_from_link(headers.get("Link", ""))
    return last if last is not None else 1


def safe(text: Any) -> str:
    return html.escape(str(text or ""), quote=True)


def initials(name: str, username: str) -> str:
    base = name or username
    parts = re.findall(r"[A-Za-z0-9]+", base)
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (base[:2] or "GH").upper()


def compact_number(num: int | float) -> str:
    try:
        n = int(num)
    except Exception:
        return "0"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n/1_000:.1f}k".replace(".0k", "k")
    return str(n)


def split_name(display_name: str, username: str) -> tuple[str, str]:
    name = display_name or username
    parts = name.split()
    if len(parts) >= 3:
        return " ".join(parts[:2]), " ".join(parts[2:])
    if len(parts) == 2:
        return parts[0], parts[1]
    return name, ""


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = str(text or "").split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines[:3]


def detect_tech(repos: list[dict[str, Any]]) -> tuple[list[str], Counter[str], Counter[str]]:
    language_bytes: Counter[str] = Counter()
    topics: Counter[str] = Counter()

    for repo in repos[:50]:
        if repo.get("fork"):
            continue
        owner = repo.get("owner", {}).get("login") or USERNAME
        name = repo.get("name")
        if not name:
            continue
        langs = api_get(f"/repos/{owner}/{name}/languages", {})
        if isinstance(langs, dict):
            for lang, count in langs.items():
                language_bytes[lang] += int(count or 0)
        for topic in repo.get("topics", []) or []:
            t = str(topic).lower().strip()
            if t:
                topics[t] += 1

    tech: list[str] = []
    for lang, _ in language_bytes.most_common(10):
        tech.append(lang)
    for topic, _ in topics.most_common(20):
        label = TOPIC_LABELS.get(topic, topic.replace("-", " ").title())
        if label not in tech:
            tech.append(label)
    return tech[:18], language_bytes, topics


def activity_by_day() -> Counter[str]:
    events = github_paginated(f"/users/{USERNAME}/events/public?per_page=100", limit_pages=3)
    counter: Counter[str] = Counter()
    for event in events:
        created = str(event.get("created_at", ""))[:10]
        if created:
            weight = 1
            if event.get("type") == "PushEvent":
                commits = event.get("payload", {}).get("commits") or []
                weight = max(1, len(commits))
            counter[created] += weight
    return counter


def make_button(x: int, y: int, label: str, width: int, icon: str = "") -> str:
    label_text = f"{icon}  {label}" if icon else label
    return f'''
    <g>
      <rect x="{x}" y="{y}" width="{width}" height="40" rx="7" fill="{COLORS['panel']}" stroke="{COLORS['border']}"/>
      <text x="{x + 18}" y="{y + 26}" font-size="15" fill="{COLORS['text']}" font-family="monospace">{safe(label_text)}</text>
    </g>'''


def make_metric(x: int, y: int, width: int, value: str, label: str, color: str) -> str:
    return f'''
    <g>
      <rect x="{x}" y="{y}" width="{width}" height="92" rx="10" fill="{COLORS['panel']}" stroke="{COLORS['border']}"/>
      <text x="{x + width/2}" y="{y + 43}" text-anchor="middle" font-size="30" font-weight="800" fill="{color}" font-family="Arial, sans-serif">{safe(value)}</text>
      <text x="{x + width/2}" y="{y + 68}" text-anchor="middle" font-size="13" fill="{COLORS['text']}" font-family="monospace">{safe(label)}</text>
    </g>'''


def make_section_label(x: int, y: int, label: str) -> str:
    return f'<text x="{x}" y="{y}" font-size="15" fill="{COLORS["blue"]}" font-weight="700" letter-spacing="4" font-family="monospace">// {safe(label.upper())}</text>'


def make_graph(x: int, y: int, activity: Counter[str]) -> str:
    today = dt.date.today()
    # start on Sunday, 52 weeks back
    start = today - dt.timedelta(days=52 * 7 - 1)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    cell = 10
    gap = 5
    parts = [f'<rect x="{x}" y="{y}" width="810" height="215" rx="10" fill="{COLORS["panel"]}" stroke="{COLORS["border"]}"/>']
    parts.append(f'<text x="{x+26}" y="{y+36}" font-size="15" fill="{COLORS["text"]}" font-family="monospace">streak &amp; activity</text>')
    grid_x = x + 26
    grid_y = y + 56
    for week in range(52):
        for day in range(7):
            d = start + dt.timedelta(days=week * 7 + day)
            if d > today:
                level = 0
            else:
                c = activity.get(d.isoformat(), 0)
                if c == 0:
                    level = 0
                elif c < 2:
                    level = 1
                elif c < 4:
                    level = 2
                elif c < 7:
                    level = 3
                else:
                    level = 4
            color = ["#0e4429", "#006d32", "#26a641", "#39d353", "#56f072"][level]
            opacity = "0.55" if level == 0 else "1"
            px = grid_x + week * (cell + gap)
            py = grid_y + day * (cell + gap)
            parts.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{color}" opacity="{opacity}"/>')
    return "\n".join(parts)


def make_tech_pills(x: int, y: int, tech: list[str]) -> str:
    parts: list[str] = []
    px, py = x, y
    max_x = 820
    for i, label in enumerate(tech[:18]):
        w = max(82, min(170, 34 + len(label) * 8))
        if px + w > max_x:
            px = x
            py += 42
        color = [COLORS["blue"], COLORS["purple"], COLORS["green"], "#238636", "#8957e5"][i % 5]
        parts.append(f'''
        <g>
          <rect x="{px}" y="{py}" width="{w}" height="28" rx="7" fill="{color}" opacity="0.9"/>
          <text x="{px + w/2}" y="{py + 19}" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff" font-family="Arial, sans-serif">{safe(label.upper())}</text>
        </g>''')
        px += w + 10
    return "\n".join(parts)


def make_projects(x: int, y: int, repos: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    visible = [r for r in repos if not r.get("fork")][:3]
    for i, repo in enumerate(visible):
        cx = x + i * 266
        name = repo.get("name") or "repo"
        desc = repo.get("description") or "Recently updated repository"
        lang = repo.get("language") or "Code"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        lines = wrap_text(desc, 28)
        desc_svg = "".join(
            f'<text x="{cx+18}" y="{y+70+j*18}" font-size="12" fill="{COLORS["muted"]}" font-family="Arial, sans-serif">{safe(line)}</text>'
            for j, line in enumerate(lines)
        )
        cards.append(f'''
        <g>
          <rect x="{cx}" y="{y}" width="246" height="130" rx="10" fill="{COLORS['panel']}" stroke="{COLORS['border']}"/>
          <text x="{cx+18}" y="{y+30}" font-size="16" fill="{COLORS['cyan']}" font-weight="700" font-family="Arial, sans-serif">{safe(name[:24])}</text>
          <text x="{cx+18}" y="{y+50}" font-size="12" fill="{COLORS['text']}" font-family="monospace">{safe(lang)}</text>
          {desc_svg}
          <text x="{cx+18}" y="{y+112}" font-size="12" fill="{COLORS['muted']}" font-family="monospace">★ {stars}   ⑂ {forks}</text>
        </g>''')
    return "\n".join(cards)


def ensure_readme() -> None:
    README_PATH.write_text('''<div align="center">\n\n<img src="./assets/profile-card.svg" alt="GitHub Profile" width="100%" />\n\n</div>\n\n<!--\nThis README intentionally uses a generated SVG image so GitHub shows the same custom UI everywhere.\nDo not edit assets/profile-card.svg manually. It is regenerated by GitHub Actions.\n-->\n''', encoding="utf-8")


def build_svg() -> str:
    user = api_get(f"/users/{USERNAME}", {})
    if not isinstance(user, dict):
        user = {}

    repos = github_paginated(f"/users/{USERNAME}/repos?per_page=100&sort=pushed&type=owner", limit_pages=4)
    if not repos:
        repos = []
    repos = sorted(repos, key=lambda r: str(r.get("pushed_at") or r.get("updated_at") or ""), reverse=True)
    public_repos = [r for r in repos if not r.get("private") and not r.get("fork")]

    display_name = user.get("name") or USERNAME
    first_line, second_line = split_name(display_name, USERNAME)
    bio = user.get("bio") or "Full-stack developer & UI/UX enthusiast crafting scalable products at the intersection of code and design."
    location = user.get("location") or "Earth"
    followers = int(user.get("followers") or 0)
    following = int(user.get("following") or 0)
    repo_count = int(user.get("public_repos") or len(public_repos))
    total_stars = sum(int(r.get("stargazers_count") or 0) for r in public_repos)
    total_forks = sum(int(r.get("forks_count") or 0) for r in public_repos)

    tech, language_bytes, topics = detect_tech(public_repos)
    if not tech:
        tech = ["Python", "JavaScript", "React", "UI/UX", "Data Science"]
    tech_count = len(set(tech))

    total_commits = 0
    for repo in public_repos[:40]:
        total_commits += commit_count_for_repo(repo)
        time.sleep(0.05)

    activity = activity_by_day()

    social_buttons: list[str] = []
    socials = [
        ("Instagram", os.getenv("SOCIAL_INSTAGRAM", "").strip(), "◎", 145),
        ("LinkedIn", os.getenv("SOCIAL_LINKEDIN", "").strip(), "in", 135),
        ("Email", os.getenv("SOCIAL_EMAIL", "").strip(), "✉", 120),
    ]
    # If no social variables are configured, still show GitHub and Website from live profile data.
    if not any(url for _, url, _, _ in socials):
        socials = [("GitHub", user.get("html_url") or f"https://github.com/{USERNAME}", "⌘", 120)]
        if user.get("blog"):
            socials.append(("Website", user.get("blog"), "↗", 125))
    sx = 55
    for label, url, icon, width in socials:
        if url:
            social_buttons.append(make_button(sx, 306, label, width, icon))
            sx += width + 14

    metrics = "\n".join([
        make_metric(55, 406, 250, compact_number(total_commits), "commits", COLORS["blue"]),
        make_metric(325, 406, 250, compact_number(repo_count), "projects", COLORS["purple"]),
        make_metric(595, 406, 250, compact_number(tech_count), "tech stacks", COLORS["green"]),
    ])

    bio_lines = wrap_text(bio, 66)
    bio_svg = "".join(
        f'<text x="205" y="{206 + i*24}" font-size="18" fill="{COLORS["text"]}" font-family="Arial, sans-serif">{safe(line)}</text>'
        for i, line in enumerate(bio_lines)
    )

    top_langs = ", ".join([lang for lang, _ in language_bytes.most_common(4)]) or "Code, Design, Data"
    updated_at = dt.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1120" viewBox="0 0 900 1120" role="img" aria-label="GitHub profile card for {safe(display_name)}">
  <title>{safe(display_name)} GitHub Profile</title>
  <defs>
    <linearGradient id="nameGrad" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="{COLORS['white']}"/>
      <stop offset="45%" stop-color="{COLORS['white']}"/>
      <stop offset="100%" stop-color="{COLORS['purple']}"/>
    </linearGradient>
    <linearGradient id="avatarGrad" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#79c0ff"/>
      <stop offset="100%" stop-color="#a371f7"/>
    </linearGradient>
    <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="10" stdDeviation="20" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>

  <rect width="900" height="1120" rx="18" fill="{COLORS['bg']}"/>
  <rect x="24" y="20" width="852" height="1075" rx="18" fill="#0f1721" stroke="#17212f" filter="url(#softShadow)"/>

  <circle cx="110" cy="110" r="58" fill="url(#avatarGrad)"/>
  <circle cx="110" cy="110" r="53" fill="#8b8be8"/>
  <text x="110" y="126" text-anchor="middle" font-size="42" font-weight="900" fill="#05070d" font-family="Arial, sans-serif">{safe(initials(display_name, USERNAME))}</text>

  <text x="205" y="70" font-size="16" letter-spacing="2" fill="{COLORS['blue']}" font-family="monospace">const dev = &#123;</text>
  <text x="205" y="118" font-size="42" font-weight="900" fill="url(#nameGrad)" font-family="Arial, sans-serif">{safe(first_line)}</text>
  <text x="205" y="162" font-size="42" font-weight="900" fill="{COLORS['purple']}" font-family="Arial, sans-serif">{safe(second_line)}</text>
  <text x="205" y="184" font-size="16" fill="{COLORS['blue']}" font-family="monospace">&#125;</text>
  {bio_svg}
  <text x="205" y="276" font-size="14" fill="{COLORS['muted']}" font-family="monospace">@{safe(USERNAME)} • {safe(location)} • {compact_number(followers)} followers • {compact_number(following)} following</text>

  <line x1="55" y1="292" x2="845" y2="292" stroke="{COLORS['border']}"/>
  {make_section_label(55, 336, 'socials')}
  {''.join(social_buttons)}

  {make_section_label(55, 386, 'metrics')}
  {metrics}

  {make_section_label(55, 545, 'contribution graph')}
  {make_graph(55, 570, activity)}

  {make_section_label(55, 825, 'detected tech stack')}
  {make_tech_pills(55, 850, tech)}

  {make_section_label(55, 960, 'latest projects')}
  {make_projects(55, 985, public_repos)}

  <text x="845" y="1080" text-anchor="end" font-size="12" fill="{COLORS['muted']}" font-family="monospace">stars {compact_number(total_stars)} • forks {compact_number(total_forks)} • top: {safe(top_langs[:60])}</text>
  <text x="55" y="1080" font-size="12" fill="{COLORS['muted']}" font-family="monospace">auto-updated: {safe(updated_at)}</text>
</svg>
'''
    return svg


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    ensure_readme()
    SVG_PATH.write_text(build_svg(), encoding="utf-8")
    print(f"Generated {SVG_PATH}")


if __name__ == "__main__":
    main()
