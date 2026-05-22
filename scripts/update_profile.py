#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONFIG_PATH = ROOT / "profile_config.json"
SVG_PATH = ASSETS / "profile-hero.svg"
README_PATH = ROOT / "README.md"

DEFAULT_CONFIG = {
    "profile": {
        "headline": "Full-Stack Developer · UI/UX Enthusiast · ML Explorer",
        "tagline": "Crafting scalable products at the intersection of code and design.",
        "fallback_name": "Ujjwal Kumar Kannojiya",
        "fallback_username": "UjjwalKumarKannojiya",
        "location": "India",
    },
    "socials": [
        {"label": "Instagram", "url": "https://instagram.com/ni.mi.sh.___", "badge": "Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white"},
        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/ujjwal-kannojiya-78744723a/", "badge": "LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"},
        {"label": "Email", "url": "mailto:nk875002@gmail.com", "badge": "Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"},
    ],
    "tech_categories": {
        "Languages": ["C", "HTML5", "Java", "JavaScript", "TypeScript", "R", "Python", "CSS3"],
        "Frontend": ["React", "Next JS", "Vite", "TailwindCSS", "Bootstrap"],
        "Backend & Databases": ["NodeJS", "NPM", "Apache", "MongoDB", "MySQL"],
        "Cloud & Big Data": ["AWS", "Azure", "Netlify", "Apache Hadoop", "Apache Hive", "Power BI"],
        "Machine Learning": ["TensorFlow", "NumPy", "PyTorch", "scikit-learn", "Pandas"],
        "Design & Tools": ["Canva", "Figma", "Sketch", "Dribbble", "Adobe", "Adobe Photoshop", "Adobe Premiere Pro", "GitHub", "Git", "Postman", "Notion"],
        "Interests": ["Riot Games", "Epic Games", "Steam", "nVIDIA"],
    },
}

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

GRAPHQL_QUERY = (
    "query($login: String!) {"
    " user(login: $login) {"
    " login name bio location followers { totalCount } following { totalCount }"
    " repositories(first: 100, privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}, ownerAffiliations: OWNER) {"
    " totalCount nodes { name description url stargazerCount forkCount updatedAt pushedAt isFork primaryLanguage { name color } repositoryTopics(first: 12) { nodes { topic { name } } } }"
    " }"
    " contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } }"
    " }"
    "}"
)


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
    return value[: max(0, length - 1)].rstrip() + "…"


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
            "User-Agent": "fresh-profile-readme",
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
        "location": config["profile"].get("location", "India"),
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


def repo_list(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    username = user.get("login", "")
    repos = ((user.get("repositories") or {}).get("nodes")) or []
    visible = [r for r in repos if not r.get("isFork") and r.get("name") != username]
    return visible or [r for r in repos if not r.get("isFork")] or repos


def build_heatmap(weeks: List[Dict[str, Any]], x: int, y: int) -> str:
    latest_weeks = weeks[-52:] if len(weeks) > 52 else weeks
    cell = 11
    gap = 4
    parts = []
    for wi, week in enumerate(latest_weeks):
        days = week.get("contributionDays") or []
        for di, day in enumerate(days[:7]):
            count = int(day.get("contributionCount") or 0)
            if count == 0:
                fill = "#161b22"
            elif count < 3:
                fill = "#0e4429"
            elif count < 7:
                fill = "#26a641"
            else:
                fill = "#39d353"
            px = x + wi * (cell + gap)
            py = y + di * (cell + gap)
            delay = (wi * 0.014 + di * 0.03) % 2.4
            parts.append(
                f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2.5" fill="{fill}" stroke="#263652" stroke-width="0.6">'
                f'<animate attributeName="opacity" values="1;0.46;1" dur="4s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
    return "\n".join(parts)


def build_quote_animation(x: int, y: int, w: int = 816, h: int = 84) -> str:
    quotes = [
        ("Code is like humor. When you have to explain it, it is bad.", "Cory House"),
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
  <rect width="{w}" height="{h}" rx="16" fill="#161b22" stroke="#21262d"/>
  <rect x="0" y="0" width="3" height="{h}" rx="1.5" fill="#a371f7"/>
"""]

    for i, (quote, author) in enumerate(quotes):
        values, keytimes = timings[i]
        base = "1" if i == 0 else "0"
        parts.append(f"""
  <g opacity="{base}">
    <text x="24" y="36" class="quoteText">{esc(short(quote, 82))}</text>
    <text x="24" y="60" class="quoteAuthor">— {esc(author)}</text>
    <animate attributeName="opacity" values="{values}" keyTimes="{keytimes}" dur="12s" repeatCount="indefinite"/>
  </g>
""")

    parts.append(f"""
  <rect x="-840" y="0" width="840" height="{h}" fill="#161b22" opacity="0.9">
    <animate attributeName="x" values="-840;840;840;-840" keyTimes="0;0.18;0.78;1" dur="4s" repeatCount="indefinite"/>
  </rect>
</g>
""")
    return "".join(parts)


def generate_svg(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username", "UjjwalKumarKannojiya")
    name = user.get("name") or config["profile"].get("fallback_name", username)
    location = user.get("location") or config["profile"].get("location", "India")
    headline = config["profile"].get("headline", "")
    tagline = config["profile"].get("tagline", "")

    repos = repo_list(user)
    all_repos = ((user.get("repositories") or {}).get("nodes")) or []
    repo_count = int((user.get("repositories") or {}).get("totalCount") or len(all_repos))
    followers = int((user.get("followers") or {}).get("totalCount") or 0)
    total_stars = sum(int(r.get("stargazerCount") or 0) for r in all_repos)
    total_forks = sum(int(r.get("forkCount") or 0) for r in all_repos)

    calendar = ((user.get("contributionsCollection") or {}).get("contributionCalendar") or {})
    total_contribs = int(calendar.get("totalContributions") or 0)
    weeks = calendar.get("weeks") or []

    heatmap = build_heatmap(weeks, 76, 500)
    quote = build_quote_animation(76, 686)
    latest_one = repos[0].get("name", "new project") if repos else "new project"

    metrics = [
        ("Contributions", total_contribs, "#58a6ff"),
        ("Projects", repo_count, "#a371f7"),
        ("Stars", total_stars, "#d29922"),
        ("Forks", total_forks, "#f85149"),
        ("Followers", followers, "#3fb950"),
    ]

    metric_parts = []
    for i, (label, value, color) in enumerate(metrics):
        x = 76 + i * 168
        metric_parts.append(f"""
<g transform="translate({x},348)">
  <rect width="148" height="78" rx="12" fill="#161b22" stroke="#21262d"/>
  <text x="74" y="34" text-anchor="middle" class="metricValue" fill="{color}">{esc(value)}</text>
  <text x="74" y="57" text-anchor="middle" class="metricLabel">{esc(label)}</text>
</g>""")

    return f"""<svg width="1000" height="820" viewBox="0 0 1000 820" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(name)} GitHub profile">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1000" y2="820" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0d1117"/>
      <stop offset="1" stop-color="#080b12"/>
    </linearGradient>
    <linearGradient id="nameGrad" x1="240" y1="0" x2="620" y2="0" gradientUnits="userSpaceOnUse">
      <stop stop-color="#e6edf3"/>
      <stop offset="0.52" stop-color="#58a6ff"/>
      <stop offset="1" stop-color="#a371f7"/>
    </linearGradient>
    <radialGradient id="orb" cx="50%" cy="50%" r="50%">
      <stop stop-color="#58a6ff" stop-opacity="0.65"/>
      <stop offset="1" stop-color="#58a6ff" stop-opacity="0"/>
    </radialGradient>
    <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="9" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .section {{ font: 800 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: 3px; fill: #58a6ff; }}
      .muted {{ font: 500 14px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8b949e; }}
      .body {{ font: 600 18px Inter, Segoe UI, Arial, sans-serif; fill: #e6edf3; }}
      .metricValue {{ font: 900 27px Inter, Segoe UI, Arial, sans-serif; }}
      .metricLabel {{ font: 600 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8b949e; }}
      .quoteText {{ font: 600 15px Inter, Segoe UI, Arial, sans-serif; fill: #8b949e; font-style: italic; }}
      .quoteAuthor {{ font: 700 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #a371f7; }}
      @keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
      @keyframes pulse {{ 0%,100% {{ opacity: .96; }} 50% {{ opacity: 1; }} }}
      .avatar {{ animation: float 6s ease-in-out infinite; }}
      .metricCard {{ animation: pulse 4.5s ease-in-out infinite; }}
    </style>
  </defs>

  <rect width="1000" height="820" rx="22" fill="url(#bg)"/>
  <rect x="24" y="24" width="952" height="772" rx="20" fill="#0d1117" stroke="#21262d"/>
  <circle cx="870" cy="78" r="190" fill="url(#orb)" opacity="0.42"/>
  <circle cx="98" cy="780" r="220" fill="#a371f7" opacity="0.07"/>
  <path d="M48 90 C220 42 340 122 525 76 C700 32 825 42 952 75" stroke="#58a6ff" stroke-width="1.6" stroke-dasharray="8 16" opacity=".55">
    <animate attributeName="stroke-dashoffset" values="0;-240" dur="12s" repeatCount="indefinite"/>
  </path>

  <g class="avatar">
    <circle cx="142" cy="132" r="62" fill="#8b8cf0" stroke="#58a6ff" stroke-width="3" filter="url(#softGlow)">
      <animate attributeName="r" values="62;67;62" dur="4s" repeatCount="indefinite"/>
    </circle>
    <text x="142" y="150" text-anchor="middle" style="font:900 36px Inter,Segoe UI,Arial,sans-serif;fill:#0d1117">UJ</text>
  </g>

  <text x="238" y="94" class="muted">const dev = &#123;</text>
  <text x="238" y="150" style="font:900 44px Inter,Segoe UI,Arial,sans-serif;fill:url(#nameGrad)">{esc(short(name, 34))}</text>
  <text x="238" y="196" class="muted">&#125; @{esc(username)} · {esc(short(location, 30))}</text>
  <text x="238" y="246" class="body">{esc(short(headline, 80))}</text>
  <text x="238" y="276" class="muted">{esc(short(tagline, 92))}</text>

  <line x1="76" y1="316" x2="924" y2="316" stroke="#21262d"/>

  <text x="76" y="336" class="section">// LIVE METRICS</text>
  {''.join(metric_parts)}

  <text x="76" y="476" class="section">// CONTRIBUTION GRAPH</text>
  <rect x="62" y="486" width="876" height="124" rx="14" fill="#161b22" stroke="#21262d"/>
  {heatmap}

  <text x="76" y="662" class="section">// RANDOM DEV QUOTE</text>
  {quote}

  <text x="76" y="792" class="muted">latest focus: {esc(short(latest_one, 40))}</text>
  <text x="924" y="792" text-anchor="end" class="muted">Design · Code · Data · AI</text>
</svg>"""


def badge_url(badge: str) -> str:
    return f"https://img.shields.io/badge/{badge}"


def build_social_markdown(config: Dict[str, Any]) -> str:
    items = []
    for social in config.get("socials", DEFAULT_CONFIG["socials"]):
        label = md_esc(social.get("label", "Link"))
        url = social.get("url", "#")
        badge = social.get("badge")
        if badge:
            items.append(f'<a href="{url}"><img src="{badge_url(badge)}" alt="{label}" /></a>')
    return "\n".join(items)


def build_tech_stack_markdown(config: Dict[str, Any]) -> str:
    categories = config.get("tech_categories") or DEFAULT_CONFIG["tech_categories"]
    lines = ['<div align="center">', '', '## `// tech_stack`', '']

    for title, stack in categories.items():
        badges = []
        for item in stack:
            badge = BADGES.get(item)
            if badge:
                badges.append(f'<img src="{badge_url(badge)}" alt="{md_esc(item)}" />')
        if badges:
            lines.append(f'<b>{md_esc(title)}</b>')
            lines.append('<br/>')
            lines.append(" ".join(badges))
            lines.append('<br/><br/>')

    lines.append('</div>')
    return "\n".join(lines)


def build_projects_markdown(username: str, repos: List[Dict[str, Any]]) -> str:
    latest = repos[:6]
    lines = ['<div align="center">', '', '## `// latest_projects`', '']

    if not latest:
        lines += ['No public projects found yet.', '', '</div>']
        return "\n".join(lines)

    for idx, repo in enumerate(latest):
        name = repo.get("name", "")
        if not name:
            continue
        repo_param = urllib.parse.quote(name, safe="")
        user_param = urllib.parse.quote(username, safe="")
        link_name = urllib.parse.quote(name, safe="")
        card = (
            f'<a href="https://github.com/{user_param}/{link_name}">'
            f'<img width="48%" src="https://github-readme-stats.vercel.app/api/pin/?username={user_param}&repo={repo_param}&theme=github_dark&hide_border=true&bg_color=0D1117&title_color=58A6FF&text_color=E6EDF3&icon_color=A371F7" />'
            f'</a>'
        )
        lines.append(card)
        if idx % 2 == 1:
            lines.append('<br/>')

    lines += ['', '</div>']
    return "\n".join(lines)


def build_stats_markdown(username: str) -> str:
    user = urllib.parse.quote(username, safe="")
    return f"""<div align="center">

## `// github_stats`

<img height="180em" src="https://github-readme-stats.vercel.app/api?username={user}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&show_icons=true&icon_color=58A6FF&title_color=58A6FF&text_color=E6EDF3&bg_color=0D1117" />
<img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username={user}&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&layout=compact&title_color=58A6FF&text_color=E6EDF3&bg_color=0D1117" />

<br/>

<img src="https://streak-stats.demolab.com/?user={user}&theme=github-dark-blue&hide_border=true&stroke=0D1117&ring=58A6FF&fire=A371F7&currStreakLabel=58A6FF&background=0D1117&dates=8B949E" />

<br/>

<img src="https://github-profile-trophy.vercel.app/?username={user}&theme=onestar&no-frame=true&no-bg=true&margin-w=6&column=7" />

</div>"""


def build_readme(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username", "UjjwalKumarKannojiya")
    repos = repo_list(user)

    return f"""<div align="center">

<img src="./assets/profile-hero.svg" width="100%" alt="{md_esc(username)} profile banner" />

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
            raise RuntimeError("GITHUB_TOKEN not available; using fallback data.")
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
