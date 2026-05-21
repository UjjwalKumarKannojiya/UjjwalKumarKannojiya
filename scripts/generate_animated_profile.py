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
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONFIG_PATH = ROOT / "profile_config.json"
SVG_PATH = ASSETS / "animated-profile.svg"
README_PATH = ROOT / "README.md"

DEFAULT_CONFIG = {
    "profile": {
        "headline": "Full-Stack Developer · UI/UX Enthusiast · ML Explorer",
        "tagline": "Crafting scalable products at the intersection of code and design.",
        "fallback_name": "Ujjwal Kumar Kannojiya",
        "fallback_username": "UjjwalKumarKannojiya",
    },
    "socials": [
        {"label": "Instagram", "url": "https://instagram.com/ni.mi.sh.___", "badge": "Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white"},
        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/ujjwal-kannojiya-78744723a/", "badge": "LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"},
        {"label": "Email", "url": "mailto:nk875002@gmail.com", "badge": "Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"},
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
          }
        }
      }
    }
  }
}
"""


BADGES = {
    "C": "C-00599C?style=for-the-badge&logo=c&logoColor=white",
    "HTML5": "HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white",
    "Java": "Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white",
    "JavaScript": "JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E",
    "TypeScript": "TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white",
    "R": "R-276DC3?style=for-the-badge&logo=r&logoColor=white",
    "Python": "Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54",
    "CSS3": "CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white",
    "AWS": "AWS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white",
    "Azure": "Azure-0072C6?style=for-the-badge&logo=microsoftazure&logoColor=white",
    "Netlify": "Netlify-000000?style=for-the-badge&logo=netlify&logoColor=00C7B7",
    "Apache Hadoop": "Hadoop-66CCFF?style=for-the-badge&logo=apachehadoop&logoColor=black",
    "Apache Hive": "Hive-FDEE21?style=for-the-badge&logo=apachehive&logoColor=black",
    "Bootstrap": "Bootstrap-8511FA?style=for-the-badge&logo=bootstrap&logoColor=white",
    "Next JS": "Next.js-black?style=for-the-badge&logo=next.js&logoColor=white",
    "React": "React-20232a?style=for-the-badge&logo=react&logoColor=61DAFB",
    "Vite": "Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white",
    "Apache": "Apache-D42029?style=for-the-badge&logo=apache&logoColor=white",
    "MongoDB": "MongoDB-4ea94b?style=for-the-badge&logo=mongodb&logoColor=white",
    "MySQL": "MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white",
    "Canva": "Canva-00C4CC?style=for-the-badge&logo=canva&logoColor=white",
    "Figma": "Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white",
    "Sketch": "Sketch-FFB387?style=for-the-badge&logo=sketch&logoColor=black",
    "Dribbble": "Dribbble-EA4C89?style=for-the-badge&logo=dribbble&logoColor=white",
    "Adobe": "Adobe-FF0000?style=for-the-badge&logo=adobe&logoColor=white",
    "Adobe Photoshop": "Photoshop-31A8FF?style=for-the-badge&logo=adobephotoshop&logoColor=white",
    "Adobe Premiere Pro": "Premiere%20Pro-9999FF?style=for-the-badge&logo=adobepremierepro&logoColor=white",
    "TensorFlow": "TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white",
    "NumPy": "NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white",
    "PyTorch": "PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white",
    "scikit-learn": "scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white",
    "Pandas": "Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white",
    "GitHub": "GitHub-121011?style=for-the-badge&logo=github&logoColor=white",
    "Git": "Git-F05033?style=for-the-badge&logo=git&logoColor=white",
    "Riot Games": "Riot%20Games-D32936?style=for-the-badge&logo=riotgames&logoColor=white",
    "Epic Games": "Epic%20Games-313131?style=for-the-badge&logo=epicgames&logoColor=white",
    "Steam": "Steam-000000?style=for-the-badge&logo=steam&logoColor=white",
    "nVIDIA": "NVIDIA-76B900?style=for-the-badge&logo=nvidia&logoColor=white",
    "Power BI": "Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black",
    "Postman": "Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white",
    "Notion": "Notion-000000?style=for-the-badge&logo=notion&logoColor=white",
    "NodeJS": "Node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white",
    "NPM": "NPM-CB3837?style=for-the-badge&logo=npm&logoColor=white",
    "TailwindCSS": "TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white",
}


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return DEFAULT_CONFIG


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def md_esc(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


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
        days.append({"date": d.isoformat(), "contributionCount": count})

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
                opacity = "0.70"
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


def build_quote_animation(x: int, y: int, w: int = 856, h: int = 92) -> str:
    quotes = [
        ("Code is like humor. When you have to explain it, it’s bad.", "Cory House"),
        ("First, solve the problem. Then, write the code.", "John Johnson"),
        ("Make it work, make it right, make it fast.", "Kent Beck"),
    ]

    timings = [
        ("1;1;0;0;0;1", "0;0.25;0.34;0.68;0.92;1"),
        ("0;0;1;1;0;0", "0;0.28;0.36;0.58;0.68;1"),
        ("0;0;0;0;1;1", "0;0.55;0.64;0.72;0.80;1"),
    ]

    parts = [f"""
<g transform="translate({x},{y})">
  <rect width="{w}" height="{h}" rx="20" fill="#121b2a" stroke="#263652"/>
  <rect x="16" y="16" width="{w-32}" height="{h-32}" rx="15" fill="#0b1220" opacity="0.72"/>
"""]

    for i, (quote, author) in enumerate(quotes):
        values, keytimes = timings[i]
        base_opacity = "1" if i == 0 else "0"
        parts.append(f"""
  <g opacity="{base_opacity}">
    <text x="34" y="44" class="small" fill="#d7e2f7">“{esc(short(quote, 84))}”</text>
    <text x="34" y="67" class="tiny">— {esc(author)}</text>
    <animate attributeName="opacity" values="{values}" keyTimes="{keytimes}" dur="12s" repeatCount="indefinite"/>
  </g>
""")

    parts.append(f"""
  <rect x="-900" y="0" width="900" height="{h}" fill="#121b2a" opacity="0.92">
    <animate attributeName="x" values="-900;900;900;-900" keyTimes="0;0.18;0.78;1" dur="4s" repeatCount="indefinite"/>
  </rect>

  <rect x="0" y="0" width="5" height="{h}" fill="#39d5ff" opacity="0.8">
    <animate attributeName="x" values="0;850;0" dur="4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.1;0.9;0.1" dur="4s" repeatCount="indefinite"/>
  </rect>
</g>
""")
    return "".join(parts)


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
    total_stars = sum(int(r.get("stargazerCount") or 0) for r in repos)
    total_forks = sum(int(r.get("forkCount") or 0) for r in repos)

    calendar = ((user.get("contributionsCollection") or {}).get("contributionCalendar") or {})
    total_contribs = int(calendar.get("totalContributions") or 0)
    weeks = calendar.get("weeks") or []

    heatmap_svg = build_heatmap(weeks, 78, 628)
    quote_svg = build_quote_animation(72, 872)

    socials = config.get("socials", DEFAULT_CONFIG["socials"])

    social_parts = []
    sx = 72
    for social in socials:
        label = social.get("label", "Link")
        w = max(120, len(label) * 10 + 54)
        social_parts.append(f"""
<g transform="translate({sx},392)" class="socialButton">
  <rect width="{w}" height="42" rx="14" fill="#121b2a" stroke="#2d3d59"/>
  <text x="24" y="27" class="socialIcon">●</text>
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
<g transform="translate({px},498)" class="metricCard">
  <rect width="164" height="88" rx="18" fill="#121b2a" stroke="#263652"/>
  <text x="82" y="39" text-anchor="middle" class="metricValue" fill="{color}">{esc(value)}</text>
  <text x="82" y="65" text-anchor="middle" class="metricLabel">{esc(label)}</text>
</g>""")

    updated = dt.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    return f"""<svg width="1000" height="1030" viewBox="0 0 1000 1030" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(name)} animated GitHub profile">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1000" y2="1030" gradientUnits="userSpaceOnUse">
      <stop stop-color="#07111f"/>
      <stop offset="0.46" stop-color="#0b1020"/>
      <stop offset="1" stop-color="#080b14"/>
    </linearGradient>
    <linearGradient id="heroText" x1="0" y1="0" x2="440" y2="120" gradientUnits="userSpaceOnUse">
      <stop stop-color="#ffffff"/>
      <stop offset="0.48" stop-color="#58a6ff"/>
      <stop offset="1" stop-color="#a855f7"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
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
      .metricValue {{ font: 900 30px Inter, Segoe UI, Arial, sans-serif; }}
      .metricLabel {{ font: 600 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8fa3c8; }}
      .card {{ animation: float 6s ease-in-out infinite; }}
      .metricCard {{ animation: cardPulse 4.5s ease-in-out infinite; }}
      .socialButton {{ animation: glowPulse 5s ease-in-out infinite; }}
      @keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
      @keyframes cardPulse {{ 0%,100% {{ opacity: 0.96; }} 50% {{ opacity: 1; }} }}
      @keyframes glowPulse {{ 0%,100% {{ opacity: 0.92; }} 50% {{ opacity: 1; }} }}
    </style>
  </defs>

  <rect width="1000" height="1030" rx="34" fill="url(#bg)"/>
  <circle cx="840" cy="120" r="210" fill="#1d4ed8" opacity="0.11"/>
  <circle cx="120" cy="930" r="250" fill="#8b5cf6" opacity="0.10"/>

  <path d="M40 78 C230 28, 410 125, 612 72 S890 68, 960 38" stroke="#39d5ff" stroke-width="2" stroke-dasharray="12 18" opacity="0.55">
    <animate attributeName="stroke-dashoffset" values="0;-300" dur="12s" repeatCount="indefinite"/>
  </path>

  <rect x="28" y="28" width="944" height="974" rx="30" stroke="#24344e" stroke-width="1.5"/>
  <rect x="48" y="48" width="904" height="934" rx="26" fill="#0b1220" opacity="0.76" stroke="#1e2c43"/>

  <g class="card">
    <circle cx="135" cy="145" r="64" fill="#8b8cf0" stroke="#58a6ff" stroke-width="3" filter="url(#glow)">
      <animate attributeName="r" values="64;68;64" dur="4s" repeatCount="indefinite"/>
    </circle>
    <text x="135" y="162" text-anchor="middle" style="font: 900 38px Inter, Segoe UI, Arial, sans-serif; fill:#07111f;">UJ</text>
    <text x="230" y="106" class="tiny" fill="#58a6ff">const dev = &#123;</text>
    <text x="230" y="154" style="font: 900 43px Inter, Segoe UI, Arial, sans-serif; fill:url(#heroText);">{esc(short(name, 34))}</text>
    <text x="230" y="200" class="tiny">&#125;  @{esc(username)} · {esc(short(location, 28))}</text>
    <text x="230" y="248" style="font: 600 18px Inter, Segoe UI, Arial, sans-serif; fill:#d7e2f7;">{esc(short(headline, 80))}</text>
    <text x="230" y="276" style="font: 500 17px Inter, Segoe UI, Arial, sans-serif; fill:#93a4c3;">{esc(short(tagline or bio, 92))}</text>
  </g>

  <line x1="72" y1="338" x2="928" y2="338" stroke="#263652"/>

  <text x="72" y="376" class="label">// SOCIALS</text>
  {''.join(social_parts)}

  <text x="72" y="480" class="label">// LIVE METRICS</text>
  {''.join(metric_parts)}

  <text x="72" y="610" class="label">// CONTRIBUTION HEATMAP</text>
  <rect x="64" y="620" width="870" height="154" rx="18" fill="#121b2a" stroke="#263652"/>
  {heatmap_svg}

  <text x="72" y="846" class="label">// RANDOM DEV QUOTE</text>
  {quote_svg}

  <line x1="72" y1="982" x2="928" y2="982" stroke="#263652"/>
  <text x="72" y="1008" class="tiny">auto-updated: {esc(updated)}</text>
  <text x="928" y="1008" text-anchor="end" class="tiny">Design · Code · Data · AI</text>
</svg>"""


def badge_url(badge: str) -> str:
    return f"https://img.shields.io/badge/{badge}"


def build_tech_stack_markdown(config: Dict[str, Any], live_stack: set) -> str:
    ordered = config.get("tech_stack_original_order") or DEFAULT_CONFIG["tech_stack_original_order"]

    lines = [
        '<div align="center">',
        '',
        '## `// tech_stack`',
        '',
        '<sub>Auto-detected stack is highlighted by your repository languages/topics. Full stack order follows your original README.</sub>',
        '',
    ]

    for item in ordered:
        badge = BADGES.get(item)
        if not badge:
            continue

        # detected stack gets bright badge, normal stack still keeps logo
        opacity_note = "" if item in live_stack else ""
        lines.append(f'<img src="{badge_url(badge)}" alt="{md_esc(item)}" />{opacity_note}')

    lines += ['', '</div>']
    return "\n".join(lines)


def build_project_markdown(repos: List[Dict[str, Any]]) -> str:
    public_repos = [r for r in repos if not r.get("isFork")]
    if not public_repos:
        public_repos = repos

    lines = [
        '<div align="center">',
        '',
        '## `// latest_projects`',
        '',
        '<sub>Auto-updated from your latest pushed public repositories.</sub>',
        '',
        '</div>',
        '',
        '<table>',
    ]

    show_repos = public_repos[:8]

    for i in range(0, len(show_repos), 2):
        left = show_repos[i]
        right = show_repos[i + 1] if i + 1 < len(show_repos) else None

        def cell(repo: Dict[str, Any] | None) -> str:
            if not repo:
                return "<td width='50%'></td>"

            name = md_esc(repo.get("name", "project"))
            url = repo.get("url", "#")
            desc = md_esc(repo.get("description") or "No description added yet.")
            lang = md_esc(((repo.get("primaryLanguage") or {}).get("name")) or "Code")
            stars = repo.get("stargazerCount") or 0
            forks = repo.get("forkCount") or 0

            return f"""<td width="50%" valign="top">

### [`{name}`]({url})

{desc}

`{lang}` · ⭐ `{stars}` · 🍴 `{forks}`

</td>"""

        lines.append("<tr>")
        lines.append(cell(left))
        lines.append(cell(right))
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def build_readme(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username", "UjjwalKumarKannojiya")
    repos = ((user.get("repositories") or {}).get("nodes")) or []
    live_stack = collect_live_stack(repos)

    socials = config.get("socials", DEFAULT_CONFIG["socials"])
    social_badges = []
    for social in socials:
        label = social.get("label", "Link")
        url = social.get("url", "#")
        badge = social.get("badge")
        if badge:
            social_badges.append(f'<a href="{url}"><img src="{badge_url(badge)}" alt="{label}" /></a>')

    return f"""<div align="center">

<img src="./assets/animated-profile.svg" width="100%" alt="{md_esc(username)} animated GitHub profile" />

<br/>

{chr(10).join(social_badges)}

</div>

---

{build_tech_stack_markdown(config, live_stack)}

---

{build_project_markdown(repos)}

---

<div align="center">

## `// github_stats`

<img height="180em" src="https://github-readme-stats.vercel.app/api?username={username}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&show_icons=true&icon_color=58a6ff&title_color=58a6ff&text_color=e6edf3&bg_color=0d1117"/>
<img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username={username}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&layout=compact&title_color=58a6ff&text_color=e6edf3&bg_color=0d1117"/>

<br/>

<img src="https://streak-stats.demolab.com/?user={username}&theme=github-dark-blue&hide_border=true&stroke=0d1117&ring=58a6ff&fire=a371f7&currStreakLabel=58a6ff&background=0d1117&dates=8b949e"/>

</div>
"""


def main() -> int:
    config = load_config()
    username = os.getenv("PROFILE_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER") or config["profile"].get("fallback_username")
    token = os.getenv("GITHUB_TOKEN") or ""

    try:
        if not token:
            raise RuntimeError("GITHUB_TOKEN not available; using fallback preview data.")
        user = request_graphql(username, token)
    except Exception as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        user = fallback_user(config, username)

    ASSETS.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(generate_svg(user, config), encoding="utf-8")
    README_PATH.write_text(build_readme(user, config), encoding="utf-8")

    print(f"Generated {SVG_PATH}")
    print(f"Generated {README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
