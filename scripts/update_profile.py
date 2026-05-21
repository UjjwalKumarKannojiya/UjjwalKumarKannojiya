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
SVG_PATH = ASSETS / "hero.svg"
README_PATH = ROOT / "README.md"

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
    "tech_categories": {
        "Languages": ["C", "HTML5", "Java", "JavaScript", "TypeScript", "R", "Python", "CSS3"],
        "Frontend": ["React", "Next JS", "Vite", "TailwindCSS", "Bootstrap"],
        "Backend & Database": ["NodeJS", "NPM", "Apache", "MongoDB", "MySQL"],
        "Cloud & Data": ["AWS", "Azure", "Netlify", "Apache Hadoop", "Apache Hive", "Power BI"],
        "AI / ML": ["TensorFlow", "NumPy", "PyTorch", "scikit-learn", "Pandas"],
        "Design & Tools": ["Canva", "Figma", "Sketch", "Dribbble", "Adobe", "Adobe Photoshop", "Adobe Premiere Pro", "GitHub", "Git", "Postman", "Notion"],
        "Interests": ["Riot Games", "Epic Games", "Steam", "nVIDIA"],
    },
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


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return DEFAULT_CONFIG


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def md_esc(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def short(value: Any, length: int) -> str:
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(value) <= length:
        return value
    return value[:max(0, length - 1)].rstrip() + "…"


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def request_graphql(username: str, token: str) -> Dict[str, Any]:
    body = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "premium-clean-profile",
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

    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, len(days), 7)]

    repos = [
        {
            "name": username,
            "description": "Personal GitHub profile repository.",
            "url": f"https://github.com/{username}/{username}",
            "stargazerCount": 0,
            "forkCount": 0,
            "updatedAt": now_utc().isoformat(),
            "pushedAt": now_utc().isoformat(),
            "isFork": False,
            "primaryLanguage": {"name": "Markdown", "color": "#083fa1"},
            "repositoryTopics": {"nodes": []},
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
                fill, opacity = "#122033", "0.68"
            elif count < 3:
                fill, opacity = "#0e7a3f", "0.95"
            elif count < 7:
                fill, opacity = "#16a34a", "1"
            else:
                fill, opacity = "#31e981", "1"
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
  <rect x="16" y="16" width="{w - 32}" height="{h - 32}" rx="15" fill="#0b1220" opacity="0.72"/>
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

    heatmap_svg = build_heatmap(weeks, 78, 590)
    quote_svg = build_quote_animation(72, 820)

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
<g transform="translate({px},450)" class="metricCard">
  <rect width="164" height="88" rx="18" fill="#121b2a" stroke="#263652"/>
  <text x="82" y="39" text-anchor="middle" class="metricValue" fill="{color}">{esc(value)}</text>
  <text x="82" y="65" text-anchor="middle" class="metricLabel">{esc(label)}</text>
</g>""")

    return f"""<svg width="1000" height="960" viewBox="0 0 1000 960" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(name)} GitHub profile">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1000" y2="960" gradientUnits="userSpaceOnUse">
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
      .metricValue {{ font: 900 30px Inter, Segoe UI, Arial, sans-serif; }}
      .metricLabel {{ font: 600 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8fa3c8; }}
      .card {{ animation: float 6s ease-in-out infinite; }}
      .metricCard {{ animation: cardPulse 4.5s ease-in-out infinite; }}
      @keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
      @keyframes cardPulse {{ 0%,100% {{ opacity: 0.96; }} 50% {{ opacity: 1; }} }}
    </style>
  </defs>

  <rect width="1000" height="960" rx="34" fill="url(#bg)"/>
  <circle cx="840" cy="120" r="210" fill="#1d4ed8" opacity="0.11"/>
  <circle cx="120" cy="875" r="250" fill="#8b5cf6" opacity="0.10"/>

  <path d="M40 78 C230 28, 410 125, 612 72 S890 68, 960 38" stroke="#39d5ff" stroke-width="2" stroke-dasharray="12 18" opacity="0.55">
    <animate attributeName="stroke-dashoffset" values="0;-300" dur="12s" repeatCount="indefinite"/>
  </path>

  <rect x="28" y="28" width="944" height="904" rx="30" stroke="#24344e" stroke-width="1.5"/>
  <rect x="48" y="48" width="904" height="864" rx="26" fill="#0b1220" opacity="0.76" stroke="#1e2c43"/>

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

  <line x1="72" y1="365" x2="928" y2="365" stroke="#263652"/>

  <text x="72" y="430" class="label">// LIVE METRICS</text>
  {''.join(metric_parts)}

  <text x="72" y="572" class="label">// CONTRIBUTION HEATMAP</text>
  <rect x="64" y="582" width="870" height="154" rx="18" fill="#121b2a" stroke="#263652"/>
  {heatmap_svg}

  <text x="72" y="796" class="label">// RANDOM DEV QUOTE</text>
  {quote_svg}

  <text x="928" y="920" text-anchor="end" class="tiny">Design · Code · Data · AI</text>
</svg>"""


def badge_url(badge: str) -> str:
    return f"https://img.shields.io/badge/{badge}"


def build_social_markdown(config: Dict[str, Any]) -> str:
    badges = []
    for social in config.get("socials", DEFAULT_CONFIG["socials"]):
        label = md_esc(social.get("label", "Link"))
        url = social.get("url", "#")
        badge = social.get("badge")
        if badge:
            badges.append(f'<a href="{url}"><img src="{badge_url(badge)}" alt="{label}" /></a>')
    return "\n".join(badges)


def build_tech_stack_markdown(config: Dict[str, Any]) -> str:
    categories = config.get("tech_categories") or DEFAULT_CONFIG["tech_categories"]
    blocks = ['<div align="center">', '', '## `// tech_stack`', '']

    for category, items in categories.items():
        badges = []
        for item in items:
            badge = BADGES.get(item)
            if badge:
                badges.append(f'<img src="{badge_url(badge)}" alt="{md_esc(item)}" />')
        if badges:
            blocks.append(f'<b>{md_esc(category)}</b>')
            blocks.append('<br/>')
            blocks.append(" ".join(badges))
            blocks.append('<br/><br/>')

    blocks.append('</div>')
    return "\n".join(blocks)


def build_projects_markdown(username: str, repos: List[Dict[str, Any]]) -> str:
    public_repos = [r for r in repos if not r.get("isFork")]
    if not public_repos:
        public_repos = repos

    public_repos = public_repos[:6]
    if not public_repos:
        return """<div align="center">

## `// latest_projects`

No public projects found yet.

</div>"""

    lines = ['<div align="center">', '', '## `// latest_projects`', '']

    for repo in public_repos:
        name = repo.get("name", "")
        if not name:
            continue
        safe_name = md_esc(name)
        lines.append(
            f'<a href="https://github.com/{username}/{safe_name}">'
            f'<img width="48%" src="https://github-readme-stats.vercel.app/api/pin/?username={username}&repo={safe_name}&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=58a6ff&text_color=e6edf3&icon_color=a855f7" />'
            f'</a>'
        )

    lines += ['', '</div>']
    return "\n".join(lines)


def build_stats_markdown(username: str) -> str:
    return f"""<div align="center">

## `// github_stats`

<img height="180em" src="https://github-readme-stats.vercel.app/api?username={username}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&show_icons=true&icon_color=58a6ff&title_color=58a6ff&text_color=e6edf3&bg_color=0d1117" />
<img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username={username}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&layout=compact&title_color=58a6ff&text_color=e6edf3&bg_color=0d1117" />

<br/>

<img src="https://streak-stats.demolab.com/?user={username}&theme=github-dark-blue&hide_border=true&stroke=0d1117&ring=58a6ff&fire=a371f7&currStreakLabel=58a6ff&background=0d1117&dates=8b949e" />

</div>"""


def build_readme(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username", "UjjwalKumarKannojiya")
    repos = ((user.get("repositories") or {}).get("nodes")) or []

    return f"""<div align="center">

<img src="./assets/hero.svg" width="100%" alt="{md_esc(username)} profile banner" />

<br/>
<br/>

{build_social_markdown(config)}

</div>

<br/>

{build_tech_stack_markdown(config)}

<br/>

{build_projects_markdown(username, repos)}

<br/>

{build_stats_markdown(username)}
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

    print("Profile updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
