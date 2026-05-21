#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONFIG_PATH = ROOT / "profile_config.json"
SVG_PATH = ASSETS / "animated-profile.svg"

DEFAULT_CONFIG = {
    "profile": {
        "headline": "Full-Stack Developer · UI/UX Enthusiast · ML Explorer",
        "tagline": "Crafting scalable products at the intersection of code and design.",
        "fallback_name": "Ujjwal Kumar Kannojiya",
        "fallback_username": "UjjwalKumarKannojiya",
    },
    "socials": [
        {"label": "Instagram", "url": "https://instagram.com/ni.mi.sh.___", "icon": "◎"},
        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/ujjwal-kannojiya-78744723a/", "icon": "in"},
        {"label": "Email", "url": "mailto:nk875002@gmail.com", "icon": "✉"},
    ],
    "tech_stack_original_order": [
        "C", "HTML5", "Java", "JavaScript", "TypeScript", "R", "Python", "CSS3",
        "AWS", "Azure", "Netlify", "Apache Hadoop", "Apache Hive", "Bootstrap",
        "Next JS", "React", "Vite", "Apache", "MongoDB", "MySQL", "Canva", "Figma",
        "Sketch", "Dribbble", "Adobe", "Adobe Photoshop", "Adobe Premiere Pro",
        "TensorFlow", "NumPy", "PyTorch", "scikit-learn", "Pandas", "GitHub", "Git",
        "Riot Games", "Epic Games", "Steam", "nVIDIA", "Power BI", "Postman",
        "Notion", "NodeJS", "NPM", "TailwindCSS",
    ],
}

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    bio
    location
    avatarUrl
    url
    followers { totalCount }
    following { totalCount }
    repositories(first: 100, privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        name
        description
        url
        stargazerCount
        forkCount
        updatedAt
        pushedAt
        isFork
        primaryLanguage { name color }
        repositoryTopics(first: 12) { nodes { topic { name } } }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
          }
        }
      }
    }
  }
}
"""


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def short(value: Any, length: int) -> str:
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(value) <= length:
        return value
    return value[: max(0, length - 1)].rstrip() + "…"


def request_graphql(username: str, token: str) -> Dict[str, Any]:
    body = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "animated-profile-readme",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.loads(res.read().decode("utf-8"))

    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], indent=2))

    user = (payload.get("data") or {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")

    return user


def fallback_user(config: Dict[str, Any], username: str) -> Dict[str, Any]:
    today = dt.date.today()
    days = []
    for i in range(371):
        d = today - dt.timedelta(days=370 - i)
        count = 0
        if i % 7 in (1, 2, 3) and i % 5 != 0:
            count = (i * 3) % 11
        days.append({"date": d.isoformat(), "contributionCount": count, "color": "#0e4429" if count else "#0b2a22"})

    weeks = []
    for i in range(0, len(days), 7):
        weeks.append({"contributionDays": days[i : i + 7]})

    repos = [
        {
            "name": username,
            "description": "Auto-updating GitHub profile README.",
            "url": f"https://github.com/{username}/{username}",
            "stargazerCount": 0,
            "forkCount": 0,
            "updatedAt": dt.datetime.utcnow().isoformat() + "Z",
            "pushedAt": dt.datetime.utcnow().isoformat() + "Z",
            "isFork": False,
            "primaryLanguage": {"name": "Markdown", "color": "#083fa1"},
            "repositoryTopics": {"nodes": [{"topic": {"name": "github-profile"}}]},
        }
    ]

    return {
        "login": username,
        "name": config["profile"].get("fallback_name", username),
        "bio": config["profile"].get("headline", ""),
        "location": "India",
        "url": f"https://github.com/{username}",
        "avatarUrl": "",
        "followers": {"totalCount": 0},
        "following": {"totalCount": 0},
        "repositories": {"totalCount": len(repos), "nodes": repos},
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": sum(d["contributionCount"] for d in days),
                "weeks": weeks,
            }
        },
    }


def normalize_stack_name(name: str) -> str:
    mapping = {
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "python": "Python",
        "java": "Java",
        "c": "C",
        "r": "R",
        "html": "HTML5",
        "html5": "HTML5",
        "css": "CSS3",
        "css3": "CSS3",
        "nextjs": "Next JS",
        "next.js": "Next JS",
        "react": "React",
        "vite": "Vite",
        "tailwind": "TailwindCSS",
        "tailwindcss": "TailwindCSS",
        "node": "NodeJS",
        "nodejs": "NodeJS",
        "node.js": "NodeJS",
        "mongodb": "MongoDB",
        "mysql": "MySQL",
        "aws": "AWS",
        "azure": "Azure",
        "netlify": "Netlify",
        "hadoop": "Apache Hadoop",
        "hive": "Apache Hive",
        "bootstrap": "Bootstrap",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "figma": "Figma",
        "postman": "Postman",
        "notion": "Notion",
        "powerbi": "Power BI",
        "power-bi": "Power BI",
        "git": "Git",
        "github": "GitHub",
        "npm": "NPM",
    }
    key = str(name or "").strip().lower()
    return mapping.get(key, name)


def collect_live_stack(repos: List[Dict[str, Any]]) -> set:
    detected = set()
    for repo in repos:
        lang = ((repo.get("primaryLanguage") or {}).get("name") or "").strip()
        if lang:
            detected.add(normalize_stack_name(lang))
        for node in (((repo.get("repositoryTopics") or {}).get("nodes")) or []):
            topic = (((node or {}).get("topic") or {}).get("name") or "").strip()
            if topic:
                detected.add(normalize_stack_name(topic))
    return detected


def build_heatmap(weeks: List[Dict[str, Any]], x: int, y: int) -> str:
    latest_weeks = weeks[-52:] if len(weeks) > 52 else weeks
    cell = 12
    gap = 4
    parts = []
    for wi, week in enumerate(latest_weeks):
        days = week.get("contributionDays") or []
        for di, day in enumerate(days[:7]):
            count = int(day.get("contributionCount") or 0)
            if count == 0:
                fill = "#122033"
                opacity = "0.72"
            elif count < 3:
                fill = "#0e7a3f"
                opacity = "0.95"
            elif count < 7:
                fill = "#16a34a"
                opacity = "1"
            else:
                fill = "#31e981"
                opacity = "1"
            px = x + wi * (cell + gap)
            py = y + di * (cell + gap)
            delay = (wi * 0.018 + di * 0.035) % 2
            parts.append(
                f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="{opacity}">'
                f'<animate attributeName="opacity" values="{opacity};0.38;{opacity}" dur="3.8s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
    return "\n".join(parts)


def pill(text: str, x: int, y: int, active: bool = False, max_chars: int = 18) -> Tuple[str, int]:
    label = short(text, max_chars)
    w = max(80, len(label) * 8 + 34)
    fill = "#1b2538" if not active else "url(#pillActive)"
    stroke = "#2f405a" if not active else "#39d5ff"
    text_color = "#aab8d6" if not active else "#f7fbff"
    shadow = 'filter="url(#glowSmall)"' if active else ""
    s = (
        f'<g transform="translate({x},{y})" {shadow}>'
        f'<rect width="{w}" height="34" rx="17" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'<text x="{w/2:.1f}" y="22" text-anchor="middle" class="pillText" fill="{text_color}">{esc(label)}</text>'
        f'</g>'
    )
    return s, w


def wrap_pills(items: List[str], active_set: set, x: int, y: int, max_width: int, max_rows: int = 6) -> Tuple[str, int]:
    parts = []
    cx = x
    cy = y
    rows = 1
    for idx, item in enumerate(items):
        active = item in active_set
        p, w = pill(item, cx, cy, active=active)
        if cx + w > x + max_width:
            rows += 1
            if rows > max_rows:
                remaining = len(items) - idx
                p, w = pill(f"+{remaining} more", x, cy + 44, active=False)
                parts.append(p)
                cy += 44
                break
            cx = x
            cy += 44
            p, w = pill(item, cx, cy, active=active)
        parts.append(p)
        cx += w + 12
    return "\n".join(parts), cy + 34


def project_cards(repos: List[Dict[str, Any]], x: int, y: int) -> str:
    cards = []
    public_repos = [r for r in repos if not r.get("isFork")]
    if not public_repos:
        public_repos = repos
    for i, repo in enumerate(public_repos[:4]):
        col = i % 2
        row = i // 2
        px = x + col * 450
        py = y + row * 132
        name = short(repo.get("name", "project"), 28)
        desc = short(repo.get("description") or "No description added yet.", 88)
        stars = repo.get("stargazerCount") or 0
        forks = repo.get("forkCount") or 0
        lang = (repo.get("primaryLanguage") or {}).get("name") or "Code"
        color = (repo.get("primaryLanguage") or {}).get("color") or "#58a6ff"
        cards.append(f"""
<g transform="translate({px},{py})" class="projectCard">
  <rect width="420" height="106" rx="18" fill="#121b2a" stroke="#263652"/>
  <text x="24" y="34" class="projectName">{esc(name)}</text>
  <text x="24" y="58" class="projectDesc">{esc(desc)}</text>
  <circle cx="29" cy="82" r="5" fill="{esc(color)}"/>
  <text x="42" y="87" class="tiny">{esc(lang)}</text>
  <text x="280" y="87" class="tiny">★ {stars}</text>
  <text x="340" y="87" class="tiny">⑂ {forks}</text>
</g>""")
    return "\n".join(cards)


def generate_svg(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username", "UjjwalKumarKannojiya")
    name = user.get("name") or config["profile"].get("fallback_name", username)
    bio = user.get("bio") or config["profile"].get("headline", "")
    location = user.get("location") or "India"
    headline = config["profile"].get("headline", "")
    tagline = config["profile"].get("tagline", "")

    repos = ((user.get("repositories") or {}).get("nodes")) or []
    repo_count = int((user.get("repositories") or {}).get("totalCount") or len(repos))
    followers = int((user.get("followers") or {}).get("totalCount") or 0)
    following = int((user.get("following") or {}).get("totalCount") or 0)
    total_stars = sum(int(r.get("stargazerCount") or 0) for r in repos)
    total_forks = sum(int(r.get("forkCount") or 0) for r in repos)

    calendar = ((user.get("contributionsCollection") or {}).get("contributionCalendar") or {})
    total_contribs = int(calendar.get("totalContributions") or 0)
    weeks = calendar.get("weeks") or []

    live_stack = collect_live_stack(repos)
    ordered_stack = config.get("tech_stack_original_order") or DEFAULT_CONFIG["tech_stack_original_order"]
    stack_svg, _stack_bottom = wrap_pills(ordered_stack, live_stack, 72, 1008, 900, max_rows=6)

    heatmap_svg = build_heatmap(weeks, 78, 704)
    projects_svg = project_cards(repos, 72, 1320)

    social_parts = []
    sx = 72
    for social in config.get("socials", []):
        label = social.get("label", "Link")
        icon = social.get("icon", "•")
        w = max(120, len(label) * 10 + 54)
        social_parts.append(f"""
<g transform="translate({sx},438)" class="socialButton">
  <rect width="{w}" height="42" rx="14" fill="#121b2a" stroke="#2d3d59"/>
  <text x="22" y="27" class="socialIcon">{esc(icon)}</text>
  <text x="54" y="27" class="small">{esc(label)}</text>
</g>""")
        sx += w + 16

    metrics = [
        ("Contributions", total_contribs, "#39d5ff"),
        ("Projects", repo_count, "#a855f7"),
        ("Stars", total_stars, "#facc15"),
        ("Forks", total_forks, "#fb923c"),
        ("Followers", followers, "#22c55e"),
    ]
    metric_parts = []
    for i, (label, value, color) in enumerate(metrics):
        px = 72 + i * 184
        metric_parts.append(f"""
<g transform="translate({px},{548})" class="metricCard">
  <rect width="164" height="88" rx="18" fill="#121b2a" stroke="#263652"/>
  <text x="82" y="39" text-anchor="middle" class="metricValue" fill="{color}">{esc(value)}</text>
  <text x="82" y="65" text-anchor="middle" class="metricLabel">{esc(label)}</text>
</g>""")

    updated = dt.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    svg = f"""<svg width="1000" height="1660" viewBox="0 0 1000 1660" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(name)} animated GitHub profile">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1000" y2="1660" gradientUnits="userSpaceOnUse">
      <stop stop-color="#07111f"/>
      <stop offset="0.46" stop-color="#0b1020"/>
      <stop offset="1" stop-color="#080b14"/>
    </linearGradient>
    <linearGradient id="heroText" x1="0" y1="0" x2="440" y2="120" gradientUnits="userSpaceOnUse">
      <stop stop-color="#ffffff"/>
      <stop offset="0.48" stop-color="#58a6ff"/>
      <stop offset="1" stop-color="#a855f7"/>
    </linearGradient>
    <linearGradient id="pillActive" x1="0" y1="0" x2="170" y2="34" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0ea5e9"/>
      <stop offset="1" stop-color="#8b5cf6"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glowSmall" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .label {{ font: 700 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: 4px; fill: #39d5ff; }}
      .tiny {{ font: 500 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8fa3c8; }}
      .small {{ font: 600 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #c8d3ea; }}
      .socialIcon {{ font: 800 16px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #58a6ff; }}
      .pillText {{ font: 800 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: 0.3px; }}
      .metricValue {{ font: 900 30px Inter, Segoe UI, Arial, sans-serif; }}
      .metricLabel {{ font: 600 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8fa3c8; }}
      .projectName {{ font: 800 18px Inter, Segoe UI, Arial, sans-serif; fill: #f8fbff; }}
      .projectDesc {{ font: 500 13px Inter, Segoe UI, Arial, sans-serif; fill: #93a4c3; }}
      .card {{ animation: float 6s ease-in-out infinite; }}
      .metricCard {{ animation: cardPulse 4.5s ease-in-out infinite; }}
      .card {{ animation: float 6s ease-in-out infinite; }}
.metricCard {{ animation: cardPulse 4.5s ease-in-out infinite; }}
.projectCard {{ animation: projectGlow 5s ease-in-out infinite; }}
.socialButton {{ animation: glowPulse 5s ease-in-out infinite; }}

@keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
@keyframes projectGlow {{ 0%,100% {{ opacity: 0.94; }} 50% {{ opacity: 1; }} }}
@keyframes cardPulse {{ 0%,100% {{ opacity: 0.96; }} 50% {{ opacity: 1; }} }}
@keyframes glowPulse {{ 0%,100% {{ opacity: 0.92; }} 50% {{ opacity: 1; }} }}
    </style>
  </defs>

  <rect width="1000" height="1660" rx="34" fill="url(#bg)"/>
  <circle cx="840" cy="120" r="210" fill="#1d4ed8" opacity="0.11"/>
  <circle cx="120" cy="1490" r="260" fill="#8b5cf6" opacity="0.10"/>
  <path d="M40 78 C230 28, 410 125, 612 72 S890 68, 960 38" stroke="#39d5ff" stroke-width="2" stroke-dasharray="12 18" opacity="0.55">
    <animate attributeName="stroke-dashoffset" values="0;-300" dur="12s" repeatCount="indefinite"/>
  </path>
  <rect x="28" y="28" width="944" height="1604" rx="30" stroke="#24344e" stroke-width="1.5"/>
  <rect x="48" y="48" width="904" height="1564" rx="26" fill="#0b1220" opacity="0.76" stroke="#1e2c43"/>

  <g class="card">
    <circle cx="135" cy="155" r="64" fill="#8b8cf0" stroke="#58a6ff" stroke-width="3" filter="url(#glow)">
      <animate attributeName="r" values="64;68;64" dur="4s" repeatCount="indefinite"/>
    </circle>
    <text x="135" y="172" text-anchor="middle" style="font: 900 38px Inter, Segoe UI, Arial, sans-serif; fill:#07111f;">UJ</text>
    <text x="230" y="116" class="tiny" fill="#58a6ff">const dev = &#123;</text>
    <text x="230" y="164" style="font: 900 43px Inter, Segoe UI, Arial, sans-serif; fill:url(#heroText);">{esc(short(name, 34))}</text>
    <text x="230" y="210" class="tiny">&#125;  @{esc(username)} · {esc(short(location, 28))}</text>
    <text x="230" y="258" style="font: 600 18px Inter, Segoe UI, Arial, sans-serif; fill:#d7e2f7;">{esc(short(headline, 80))}</text>
    <text x="230" y="286" style="font: 500 17px Inter, Segoe UI, Arial, sans-serif; fill:#93a4c3;">{esc(short(tagline or bio, 92))}</text>
  </g>

  <line x1="72" y1="362" x2="928" y2="362" stroke="#263652"/>
  <text x="72" y="420" class="label">// SOCIALS</text>
  {''.join(social_parts)}

  <text x="72" y="530" class="label">// LIVE METRICS</text>
  {''.join(metric_parts)}

  <text x="72" y="684" class="label">// CONTRIBUTION HEATMAP</text>
  <rect x="64" y="690" width="870" height="154" rx="18" fill="#121b2a" stroke="#263652"/>
  {heatmap_svg}

  <text x="72" y="910" class="label">// TECH STACK</text>
  <text x="72" y="942" class="tiny">Order copied from your first README. Bright pills are detected from your repos/topics.</text>
  {stack_svg}

  <text x="72" y="1280" class="label">// LATEST PROJECTS</text>
  <text x="72" y="1304" class="tiny">Automatically sorted by latest push/update time.</text>
  {projects_svg}

  <line x1="72" y1="1590" x2="928" y2="1590" stroke="#263652"/>
  <text x="72" y="1620" class="tiny">auto-updated: {esc(updated)}</text>
  <text x="928" y="1620" text-anchor="end" class="tiny">Design · Code · Data · AI</text>
</svg>"""
    return svg


def main() -> int:
    config = load_config()
    username = os.getenv("PROFILE_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER") or config["profile"].get("fallback_username")
    token = os.getenv("GITHUB_TOKEN") or ""

    env_socials = [
        ("SOCIAL_INSTAGRAM", "Instagram", "◎"),
        ("SOCIAL_LINKEDIN", "LinkedIn", "in"),
        ("SOCIAL_EMAIL", "Email", "✉"),
    ]
    socials = []
    for env_name, label, icon in env_socials:
        value = os.getenv(env_name, "").strip()
        if value:
            if env_name == "SOCIAL_EMAIL" and not value.startswith("mailto:"):
                value = f"mailto:{value}"
            socials.append({"label": label, "url": value, "icon": icon})
    if socials:
        config["socials"] = socials

    try:
        if not token:
            raise RuntimeError("GITHUB_TOKEN not available; using fallback preview data.")
        user = request_graphql(username, token)
    except Exception as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        user = fallback_user(config, username)

    ASSETS.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(generate_svg(user, config), encoding="utf-8")
    print(f"Generated {SVG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
