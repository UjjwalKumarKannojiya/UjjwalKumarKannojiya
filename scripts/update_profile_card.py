#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
SVG_PATH = ASSETS_DIR / "profile-card.svg"
README_PATH = ROOT / "README.md"
CONFIG_PATH = ROOT / "profile_config.json"


DEFAULT_CONFIG = {
    "profile": {
        "fallback_name": "Ujjwal Kumar Kannojiya",
        "fallback_username": "UjjwalKumarKannojiya",
        "headline": "Full-stack developer & UI/UX enthusiast crafting",
        "highlight": "scalable products",
        "tagline_suffix": "at the intersection of code and design.",
        "open_status": "open to opportunities",
    },
    "socials": [
        {"label": "Instagram", "url": "https://instagram.com/ni.mi.sh.___"},
        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/ujjwal-kannojiya-78744723a/"},
        {"label": "Email", "url": "mailto:nk875002@gmail.com"},
    ],
    "tech_groups": {
        "blue": ["Python", "JavaScript", "TypeScript", "Java", "C", "R"],
        "purple": ["React", "Next.js", "Node.js", "TailwindCSS", "Bootstrap", "Vite"],
        "green": ["TensorFlow", "PyTorch", "scikit-learn", "NumPy", "Pandas"],
        "orange": ["MongoDB", "MySQL", "AWS", "Azure", "Apache Hadoop"],
        "red": ["Figma", "Adobe PS", "Premiere Pro", "Power BI"],
    },
}


GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    followers { totalCount }
    repositories(
      first: 100,
      privacy: PUBLIC,
      ownerAffiliations: OWNER,
      orderBy: {field: PUSHED_AT, direction: DESC}
    ) {
      totalCount
      nodes {
        name
        url
        isFork
        stargazerCount
        forkCount
        pushedAt
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
        repositoryTopics(first: 20) {
          nodes { topic { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
          }
        }
      }
    }
  }
}
"""


NORMALIZE = {
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
    "react": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "tailwind": "TailwindCSS",
    "tailwindcss": "TailwindCSS",
    "tailwind-css": "TailwindCSS",
    "bootstrap": "Bootstrap",
    "vite": "Vite",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "mysql": "MySQL",
    "aws": "AWS",
    "azure": "Azure",
    "hadoop": "Apache Hadoop",
    "apache-hadoop": "Apache Hadoop",
    "figma": "Figma",
    "powerbi": "Power BI",
    "power-bi": "Power BI",
}


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def short(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def metric_number(value: int) -> str:
    if value >= 1000:
        return f"{value / 1000:.1f}k".replace(".0k", "k")
    return str(value)


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return DEFAULT_CONFIG


def request_github(username: str, token: str) -> Dict[str, Any]:
    body = json.dumps(
        {
            "query": GRAPHQL_QUERY,
            "variables": {"login": username},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "dynamic-profile-card",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], indent=2))

    user = (payload.get("data") or {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {username}")

    return user


def fallback_user(config: Dict[str, Any], username: str) -> Dict[str, Any]:
    demo_levels = [0, 0, 1, 1, 2, 2, 1, 3, 3, 2, 1, 0, 1, 2, 3, 4, 4, 3]
    days = [{"contributionCount": demo_levels[i % len(demo_levels)]} for i in range(371)]
    weeks = [{"contributionDays": days[i : i + 7]} for i in range(0, 371, 7)]

    return {
        "login": username,
        "name": config["profile"].get("fallback_name", username),
        "followers": {"totalCount": 0},
        "repositories": {"totalCount": 0, "nodes": []},
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": 0,
                "weeks": weeks,
            }
        },
    }


def get_repos(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    login = user.get("login", "")
    all_repos = ((user.get("repositories") or {}).get("nodes")) or []

    visible = [
        repo
        for repo in all_repos
        if not repo.get("isFork") and repo.get("name") != login
    ]

    return visible or [repo for repo in all_repos if not repo.get("isFork")] or all_repos


def normalize_stack_name(name: str) -> str:
    key = str(name or "").strip().lower()
    return NORMALIZE.get(key, str(name or "").strip())


def repo_topics(repo: Dict[str, Any]) -> set[str]:
    topic_nodes = ((repo.get("repositoryTopics") or {}).get("nodes")) or []
    topics = set()

    for node in topic_nodes:
        raw = (((node or {}).get("topic") or {}).get("name")) or ""
        if raw:
            topics.add(raw.strip().lower())

    return topics


def detected_stack(user: Dict[str, Any]) -> set[str]:
    found = set()

    for repo in get_repos(user):
        primary = normalize_stack_name(((repo.get("primaryLanguage") or {}).get("name")) or "")
        if primary:
            found.add(primary)

        for edge in ((repo.get("languages") or {}).get("edges") or []):
            lang = normalize_stack_name((((edge or {}).get("node") or {}).get("name")) or "")
            if lang:
                found.add(lang)

        for topic in repo_topics(repo):
            normalized = normalize_stack_name(topic)
            if normalized:
                found.add(normalized)

    return found


def ordered_tech_groups(user: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, List[str]]:
    found = detected_stack(user)
    groups = config.get("tech_groups") or DEFAULT_CONFIG["tech_groups"]

    return {
        color: sorted(items, key=lambda item: (item not in found, items.index(item)))
        for color, items in groups.items()
    }


def language_stats(user: Dict[str, Any]) -> List[Tuple[str, int, str]]:
    sizes: Dict[str, int] = {}
    colors: Dict[str, str] = {}

    for repo in get_repos(user):
        for edge in ((repo.get("languages") or {}).get("edges") or []):
            node = (edge or {}).get("node") or {}
            lang = node.get("name") or ""
            size = int((edge or {}).get("size") or 0)
            color = node.get("color") or "#58A6FF"

            if not lang or size <= 0:
                continue

            sizes[lang] = sizes.get(lang, 0) + size
            colors[lang] = color

    if not sizes:
        for repo in get_repos(user):
            lang = ((repo.get("primaryLanguage") or {}).get("name")) or ""
            color = ((repo.get("primaryLanguage") or {}).get("color")) or "#58A6FF"

            if not lang:
                continue

            sizes[lang] = sizes.get(lang, 0) + 1
            colors[lang] = color

    fallback = [
        ("Python", 72, "#3572A5"),
        ("JavaScript", 60, "#F1E05A"),
        ("TypeScript", 45, "#2B7489"),
        ("Java", 30, "#B07219"),
    ]

    if not sizes:
        return fallback

    total_size = sum(sizes.values()) or 1
    result = []

    for lang, size in sorted(sizes.items(), key=lambda item: item[1], reverse=True)[:4]:
        percent = max(6, round((size / total_size) * 100))
        result.append((lang, percent, colors.get(lang, "#58A6FF")))

    while len(result) < 4:
        result.append(fallback[len(result)])

    return result


def projects_svg(user: Dict[str, Any]) -> str:
    latest = get_repos(user)[:4]

    if not latest:
        return '''
        <text x="18" y="54" class="barLabel">No public projects found</text>
        <rect x="18" y="66" width="300" height="6" rx="3" fill="#21262D"/>
        <rect x="18" y="66" width="90" height="6" rx="3" fill="#A371F7" class="barFill"/>'''

    rows = []

    for index, repo in enumerate(latest):
        y = 52 + index * 21
        name = short(repo.get("name", "project"), 25)
        stars = int(repo.get("stargazerCount") or 0)
        forks = int(repo.get("forkCount") or 0)
        lang = ((repo.get("primaryLanguage") or {}).get("name")) or "Code"
        lang_color = ((repo.get("primaryLanguage") or {}).get("color")) or "#58A6FF"

        rows.append(
            f'''
            <circle cx="22" cy="{y - 4}" r="3" fill="{esc(lang_color)}" class="softPulse"/>
            <text x="34" y="{y}" class="barLabel">{esc(name)}</text>
            <text x="250" y="{y}" class="barPct">{esc(short(lang, 10))}</text>
            <text x="330" y="{y}" class="barPct">★ {stars} ⑂ {forks}</text>'''
        )

    return "\n".join(rows)


def contribution_levels(user: Dict[str, Any]) -> List[int]:
    weeks = (((user.get("contributionsCollection") or {}).get("contributionCalendar") or {}).get("weeks")) or []
    levels = []

    for week in weeks[-53:]:
        for day in (week.get("contributionDays") or [])[:7]:
            count = int(day.get("contributionCount") or 0)

            if count == 0:
                level = 0
            elif count < 3:
                level = 1
            elif count < 7:
                level = 2
            elif count < 12:
                level = 3
            else:
                level = 4

            levels.append(level)

    return levels


def contribution_grid_svg(user: Dict[str, Any]) -> str:
    colors = {
        0: ("#161B22", "#21262D"),
        1: ("#0E4429", "#26A641"),
        2: ("#006D32", "#26A641"),
        3: ("#26A641", "#39D353"),
        4: ("#39D353", "#39D353"),
    }

    levels = contribution_levels(user)
    cells = []

    for week_index in range(53):
        for day_index in range(7):
            data_index = week_index * 7 + day_index
            level = levels[data_index] if data_index < len(levels) else 0
            fill, stroke = colors[level]

            x = 54 + week_index * 14
            y = 610 + day_index * 14
            delay = (week_index * 0.018 + day_index * 0.03) % 2.4

            cells.append(
                f'''
                <rect x="{x}" y="{y}" width="11" height="11" rx="2"
                      fill="{fill}" stroke="{stroke}" class="pulseCell"
                      style="animation-delay:{delay:.2f}s"/>'''
            )

    return "\n".join(cells)


def bar_rows_svg(stats: List[Tuple[str, int, str]], x: int, y: int) -> str:
    rows = []

    for index, (label, percent, color) in enumerate(stats[:4]):
        yy = y + index * 22
        bar_width = round(204 * percent / 100)

        rows.append(
            f'''
            <text x="{x}" y="{yy + 8}" class="barLabel">{esc(short(label, 10))}</text>
            <rect x="{x + 86}" y="{yy}" width="204" height="6" rx="3" fill="#21262D"/>
            <rect x="{x + 86}" y="{yy}" width="{bar_width}" height="6" rx="3" fill="{esc(color)}" class="barFill"/>
            <text x="{x + 322}" y="{yy + 8}" class="barPct">{percent}%</text>'''
        )

    return "\n".join(rows)


def pill_svg(label: str, group: str, x: int, y: int) -> Tuple[str, int]:
    palette = {
        "blue": "#58A6FF",
        "purple": "#A371F7",
        "green": "#3FB950",
        "orange": "#D2992A",
        "red": "#F85149",
    }

    color = palette.get(group, "#58A6FF")
    width = max(54, len(label) * 7 + 24)

    svg = f'''
    <g transform="translate({x} {y})" class="softPulse">
      <rect width="{width}" height="24" rx="12"
            fill="{color}" fill-opacity="0.10"
            stroke="{color}" stroke-opacity="0.30"/>
      <text x="{width / 2:.1f}" y="16" text-anchor="middle"
            class="pill" fill="{color}">{esc(label)}</text>
    </g>'''

    return svg, width


def tech_pills_svg(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    groups = ordered_tech_groups(user, config)
    x, y = 32, 924
    parts = []

    for group in ["blue", "purple", "green", "orange", "red"]:
        for label in groups.get(group, []):
            item, width = pill_svg(label, group, x, y)

            if x + width > 828:
                x = 32
                y += 34
                item, width = pill_svg(label, group, x, y)

            parts.append(item)
            x += width + 8

    return "\n".join(parts)


SVG_TEMPLATE = """<svg width="860" height="1140" viewBox="0 0 860 1140" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="__FULL_NAME__ GitHub profile card">
  <defs>
    <linearGradient id="avatarGrad" x1="55" y1="52" x2="145" y2="142" gradientUnits="userSpaceOnUse">
      <stop stop-color="#58A6FF"/>
      <stop offset="1" stop-color="#A371F7"/>
    </linearGradient>

    <radialGradient id="blueGlow" cx="50%" cy="50%" r="50%">
      <stop stop-color="#58A6FF" stop-opacity="0.12"/>
      <stop offset="1" stop-color="#58A6FF" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="purpleGlow" cx="50%" cy="50%" r="50%">
      <stop stop-color="#A371F7" stop-opacity="0.11"/>
      <stop offset="1" stop-color="#A371F7" stop-opacity="0"/>
    </radialGradient>

    <clipPath id="cardClip">
      <rect x="0" y="0" width="860" height="1140" rx="12"/>
    </clipPath>

    <style>
      .section { font: 700 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #58A6FF; letter-spacing: 2.2px; }
      .muted { font: 400 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }
      .body { font: 500 14px Inter, Segoe UI, Arial, sans-serif; fill: #8B949E; }
      .metricNum { font: 800 25px Inter, Segoe UI, Arial, sans-serif; }
      .metricLabel { font: 400 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }
      .pill { font: 700 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: .3px; }
      .barLabel { font: 400 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }
      .barPct { font: 400 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }
      .quoteText { font: italic 13px Inter, Segoe UI, Arial, sans-serif; fill: #8B949E; }
      .quoteAttr { font: 700 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #A371F7; }

      @keyframes heroBreathe {
        0%, 100% { opacity: 0.96; }
        50% { opacity: 1; }
      }

      @keyframes avatarGlow {
        0%, 100% { opacity: 0.92; }
        50% { opacity: 1; }
      }

      @keyframes flowDash {
        0% { stroke-dashoffset: 0; opacity: 0.30; }
        50% { opacity: 0.90; }
        100% { stroke-dashoffset: -260; opacity: 0.30; }
      }

      @keyframes typing {
        0% { clip-path: inset(0 100% 0 0); }
        50% { clip-path: inset(0 0 0 0); }
        70% { clip-path: inset(0 0 0 0); }
        100% { clip-path: inset(0 100% 0 0); }
      }

      @keyframes blink {
        0%, 49% { opacity: 1; }
        50%, 100% { opacity: 0; }
      }

      @keyframes pulseCell {
        0%, 100% { opacity: 0.82; }
        50% { opacity: 1; }
      }

      @keyframes metricFloat {
        0%, 100% { opacity: 0.96; }
        50% { opacity: 1; }
      }

      @keyframes barGrow {
        0% { transform: scaleX(0.35); }
        100% { transform: scaleX(1); }
      }

      @keyframes wipe {
        0% { transform: translateX(-820px); opacity: 0.95; }
        24% { transform: translateX(820px); opacity: 0.95; }
        25%, 100% { transform: translateX(820px); opacity: 0; }
      }

      @keyframes softPulse {
        0%, 100% { opacity: 0.90; }
        50% { opacity: 1; }
      }

      .heroBreathe { animation: heroBreathe 5.8s ease-in-out infinite; }
      .avatarGroup { animation: avatarGlow 3.8s ease-in-out infinite; }
      .flowLine { animation: flowDash 8s linear infinite; }
      .typingText { animation: typing 3s steps(30) infinite; }
      .cursor { animation: blink .7s step-end infinite; }
      .pulseCell { animation: pulseCell 3.8s ease-in-out infinite; }
      .metricCard { animation: metricFloat 5s ease-in-out infinite; }
      .barFill { transform-box: fill-box; transform-origin: left; animation: barGrow 1.2s ease-out both; }
      .wipeBlock { animation: wipe 4s ease-in-out infinite; }
      .softPulse { animation: softPulse 4.4s ease-in-out infinite; }
    </style>
  </defs>

  <g clip-path="url(#cardClip)">
    <rect width="860" height="1140" rx="12" fill="#0D1117"/>
    <rect x="0.5" y="0.5" width="859" height="1139" rx="11.5" stroke="#21262D"/>

    <circle cx="825" cy="-20" r="150" fill="url(#blueGlow)">
      <animate attributeName="cx" values="825;810;825" dur="7s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="-20;-10;-20" dur="7s" repeatCount="indefinite"/>
    </circle>

    <circle cx="-18" cy="1040" r="125" fill="url(#purpleGlow)">
      <animate attributeName="cx" values="-18;2;-18" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="1040;1028;1040" dur="8s" repeatCount="indefinite"/>
    </circle>

    <path class="flowLine" d="M34 72 C170 24 282 112 420 70 C560 28 700 26 826 74"
          fill="none" stroke="#58A6FF" stroke-width="1.4"
          stroke-dasharray="8 16" opacity="0.45"/>

    <g transform="translate(32 40)" class="heroBreathe">
      <g class="avatarGroup">
        <circle cx="45" cy="45" r="45" fill="url(#avatarGrad)">
          <animate attributeName="r" values="45;48;45" dur="4s" repeatCount="indefinite"/>
        </circle>
        <circle cx="45" cy="45" r="43.5" stroke="#21262D" stroke-width="3" fill="none">
          <animate attributeName="r" values="43.5;46.5;43.5" dur="4s" repeatCount="indefinite"/>
        </circle>
        <text x="45" y="58" text-anchor="middle" style="font-weight:800;font-size:32px;fill:#0D1117;font-family:Inter,Segoe UI,Arial,sans-serif;">UK</text>
      </g>

      <text x="122" y="13" class="muted"><tspan fill="#58A6FF">const</tspan> dev = {</text>
      <text x="122" y="52" style="font-weight:800;font-size:32px;fill:#E6EDF3;font-family:Inter,Segoe UI,Arial,sans-serif;">__FIRST_LINE__</text>
      <text x="122" y="88" style="font-weight:800;font-size:32px;fill:#A371F7;font-family:Inter,Segoe UI,Arial,sans-serif;">__SECOND_LINE__</text>
      <text x="122" y="116" class="muted">}</text>
      <text x="122" y="150" class="body">__HEADLINE__</text>
      <text x="122" y="172" class="body"><tspan fill="#58A6FF" font-weight="700">__HIGHLIGHT__</tspan> __TAGLINE__</text>
    </g>

    <line x1="32" y1="250" x2="828" y2="250" stroke="#21262D"/>

    <text x="32" y="292" class="section">// SOCIALS</text>

    <g transform="translate(32 314)">
      <rect width="114" height="34" rx="6" fill="#161B22" stroke="#21262D"/>
      <circle cx="18" cy="17" r="7" fill="none" stroke="#8B949E" stroke-width="1.5"/>
      <circle cx="18" cy="17" r="2.8" fill="none" stroke="#8B949E" stroke-width="1.4"/>
      <circle cx="24" cy="11" r="1.6" fill="#8B949E"/>
      <text x="38" y="22" class="muted">Instagram</text>
    </g>

    <g transform="translate(156 314)">
      <rect width="104" height="34" rx="6" fill="#161B22" stroke="#21262D"/>
      <rect x="14" y="10" width="16" height="16" rx="2" fill="#8B949E"/>
      <text x="18" y="22" style="font-weight:700;font-size:13px;fill:#161B22;font-family:monospace;">in</text>
      <text x="42" y="22" class="muted">LinkedIn</text>
    </g>

    <g transform="translate(270 314)">
      <rect width="82" height="34" rx="6" fill="#161B22" stroke="#21262D"/>
      <path d="M14 12h16v12H14z" fill="none" stroke="#8B949E" stroke-width="1.3"/>
      <path d="M14 13l8 6 8-6" fill="none" stroke="#8B949E" stroke-width="1.3"/>
      <text x="42" y="22" class="muted">Email</text>
    </g>

    <text x="32" y="392" class="section">// METRICS</text>

    <g transform="translate(32 414)" class="metricCard">
      <rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/>
      <text x="126" y="37" text-anchor="middle" class="metricNum" fill="#58A6FF">__CONTRIBUTIONS__</text>
      <text x="126" y="58" text-anchor="middle" class="metricLabel">contributions</text>
    </g>

    <g transform="translate(304 414)" class="metricCard">
      <rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/>
      <text x="126" y="37" text-anchor="middle" class="metricNum" fill="#A371F7">__PROJECTS__</text>
      <text x="126" y="58" text-anchor="middle" class="metricLabel">projects</text>
    </g>

    <g transform="translate(576 414)" class="metricCard">
      <rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/>
      <text x="126" y="37" text-anchor="middle" class="metricNum" fill="#3FB950">__TECH_COUNT__</text>
      <text x="126" y="58" text-anchor="middle" class="metricLabel">detected tech</text>
    </g>

    <text x="32" y="536" class="section">// CONTRIBUTION GRAPH</text>

    <g transform="translate(32 556)">
      <rect width="796" height="142" rx="8" fill="#161B22" stroke="#21262D"/>
      <text x="22" y="31" class="muted">live activity from GitHub</text>
    </g>

    __CONTRIBUTION_GRID__

    <g transform="translate(32 732)">
      <rect width="388" height="124" rx="8" fill="#161B22" stroke="#21262D"/>
      <circle cx="20" cy="22" r="3" fill="#58A6FF"/>
      <text x="34" y="26" class="muted">top languages</text>
      __LANGUAGE_BARS__
    </g>

    <g transform="translate(440 732)">
      <rect width="388" height="124" rx="8" fill="#161B22" stroke="#21262D"/>
      <circle cx="20" cy="22" r="3" fill="#A371F7"/>
      <text x="34" y="26" class="muted">latest projects</text>
      __PROJECT_ROWS__
    </g>

    <text x="32" y="902" class="section">// TECH STACK</text>

    __TECH_PILLS__

    <line x1="32" y1="1010" x2="828" y2="1010" stroke="#21262D"/>

    <g transform="translate(32 1024)">
      <rect x="0" y="0" width="796" height="42" rx="0 6 6 0" fill="#161B22"/>
      <rect x="0" y="0" width="3" height="42" fill="#A371F7"/>

      <g>
        <text x="16" y="18" class="quoteText">"Code is like humor. When you have to explain it, it's bad."</text>
        <text x="16" y="35" class="quoteAttr">— Cory House</text>
        <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.34;0.44;0.90;1" dur="12s" repeatCount="indefinite"/>
      </g>

      <g opacity="0">
        <text x="16" y="18" class="quoteText">"First, solve the problem. Then, write the code."</text>
        <text x="16" y="35" class="quoteAttr">— John Johnson</text>
        <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.28;0.38;0.66;0.76" dur="12s" repeatCount="indefinite"/>
      </g>

      <rect x="-820" y="0" width="820" height="42" fill="#161B22" opacity="0.92" class="wipeBlock"/>
    </g>

    <g transform="translate(32 1092)">
      <text class="muted typingText">building the future, one commit at a time...</text>
      <rect x="304" y="-13" width="2" height="17" fill="#58A6FF" class="cursor"/>
      <circle cx="650" cy="-7" r="4" fill="#3FB950"/>
      <text x="664" y="-3" class="muted">__OPEN_STATUS__</text>
    </g>
  </g>
</svg>"""


def generate_svg(user: Dict[str, Any], config: Dict[str, Any]) -> str:
    username = user.get("login") or config["profile"].get("fallback_username")
    full_name = user.get("name") or config["profile"].get("fallback_name") or username

    name_parts = full_name.split()
    first_line = " ".join(name_parts[:2]) if len(name_parts) >= 2 else full_name
    second_line = " ".join(name_parts[2:]) if len(name_parts) > 2 else username

    repo_total = len(get_repos(user))
    contribution_total = int(
        (((user.get("contributionsCollection") or {}).get("contributionCalendar") or {}).get("totalContributions"))
        or 0
    )

    found_stack = detected_stack(user)
    tech_count = len(found_stack)

    if tech_count == 0:
        tech_count = sum(len(items) for items in (config.get("tech_groups") or {}).values())

    replacements = {
        "__FULL_NAME__": esc(full_name),
        "__FIRST_LINE__": esc(short(first_line, 28)),
        "__SECOND_LINE__": esc(short(second_line, 28)),
        "__HEADLINE__": esc(short(config["profile"].get("headline"), 64)),
        "__HIGHLIGHT__": esc(config["profile"].get("highlight")),
        "__TAGLINE__": esc(short(config["profile"].get("tagline_suffix"), 50)),
        "__CONTRIBUTIONS__": esc(metric_number(contribution_total)),
        "__PROJECTS__": esc(metric_number(repo_total)),
        "__TECH_COUNT__": esc(metric_number(tech_count)),
        "__CONTRIBUTION_GRID__": contribution_grid_svg(user),
        "__LANGUAGE_BARS__": bar_rows_svg(language_stats(user), 18, 46),
        "__PROJECT_ROWS__": projects_svg(user),
        "__TECH_PILLS__": tech_pills_svg(user, config),
        "__OPEN_STATUS__": esc(short(config["profile"].get("open_status"), 30)),
    }

    svg = SVG_TEMPLATE
    for key, value in replacements.items():
        svg = svg.replace(key, value)

    return svg


def generate_readme(config: Dict[str, Any]) -> str:
    badge_map = {
        "Instagram": "Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white",
        "LinkedIn": "LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white",
        "Email": "Email-D14836?style=for-the-badge&logo=gmail&logoColor=white",
    }

    links = []

    for item in config.get("socials", DEFAULT_CONFIG["socials"]):
        label = item.get("label", "Link")
        url = item.get("url", "#")
        badge = badge_map.get(label, f"{label}-161B22?style=for-the-badge")

        links.append(
            f'<a href="{url}"><img src="https://img.shields.io/badge/{badge}" alt="{esc(label)}" /></a>'
        )

    return (
        '<div align="center">\n\n'
        '<img src="./assets/profile-card.svg" width="100%" alt="Ujjwal Kumar Kannojiya GitHub profile" />\n\n'
        '<br/>\n<br/>\n\n'
        + " ".join(links)
        + "\n\n</div>\n"
    )


def main() -> int:
    config = load_config()

    username = (
        os.getenv("PROFILE_USERNAME")
        or os.getenv("GITHUB_REPOSITORY_OWNER")
        or config["profile"].get("fallback_username")
    )

    token = os.getenv("GITHUB_TOKEN", "")

    try:
        if not token:
            raise RuntimeError("GITHUB_TOKEN not found. Using local preview fallback.")
        user = request_github(username, token)
    except Exception as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        user = fallback_user(config, username)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    SVG_PATH.write_text(generate_svg(user, config), encoding="utf-8")
    README_PATH.write_text(generate_readme(config), encoding="utf-8")

    print("Profile card updated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
