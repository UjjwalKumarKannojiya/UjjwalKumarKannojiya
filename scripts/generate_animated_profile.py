#!/usr/bin/env python3
'''
Fresh animated GitHub profile UI generator.

No external Python packages required.
It creates assets/animated-profile.svg from live GitHub data.

Data sources:
- GitHub REST API: profile, repos, languages, topics
- GitHub GraphQL API: contribution calendar
- GitHub Actions repo variables for optional socials/tagline
'''

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any

API = "https://api.github.com"
GQL = "https://api.github.com/graphql"

USERNAME = os.getenv("PROFILE_USERNAME", "").strip() or "UjjwalKumarKannojiya"
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

SOCIAL_INSTAGRAM = os.getenv("SOCIAL_INSTAGRAM", "").strip()
SOCIAL_LINKEDIN = os.getenv("SOCIAL_LINKEDIN", "").strip()
SOCIAL_EMAIL = os.getenv("SOCIAL_EMAIL", "").strip()
PROFILE_ROLE = os.getenv("PROFILE_ROLE", "").strip() or "Full-stack Developer · UI/UX Enthusiast · AI Explorer"
PROFILE_TAGLINE = os.getenv("PROFILE_TAGLINE", "").strip() or "Building clean, scalable and human-friendly digital products."

OUT = "assets/animated-profile.svg"


def request_json(url: str, *, graphql_body: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-animated-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = None
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    if graphql_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(graphql_body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_get(url: str, fallback: Any) -> Any:
    try:
        return request_json(url)
    except Exception as e:
        print(f"[warn] request failed: {url} -> {e}", file=sys.stderr)
        return fallback


def get_all_repos(username: str) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    for page in range(1, 6):
        url = f"{API}/users/{urllib.parse.quote(username)}/repos?per_page=100&page={page}&sort=pushed&type=owner"
        chunk = safe_get(url, [])
        if not isinstance(chunk, list) or not chunk:
            break
        repos.extend(chunk)
    return [r for r in repos if not r.get("fork")]


def get_languages(username: str, repos: list[dict[str, Any]]) -> Counter:
    counter: Counter = Counter()
    for repo in repos[:35]:
        name = repo.get("name")
        if not name:
            continue
        url = f"{API}/repos/{urllib.parse.quote(username)}/{urllib.parse.quote(name)}/languages"
        langs = safe_get(url, {})
        if isinstance(langs, dict):
            for k, v in langs.items():
                try:
                    counter[k] += int(v)
                except Exception:
                    pass
    return counter


def normalize_tech(label: str) -> str:
    mapping = {
        "JavaScript": "JAVASCRIPT",
        "TypeScript": "TYPESCRIPT",
        "Python": "PYTHON",
        "Java": "JAVA",
        "HTML": "HTML5",
        "CSS": "CSS3",
        "C++": "C++",
        "C#": "C#",
        "Shell": "SHELL",
        "Jupyter Notebook": "NOTEBOOK",
    }
    return mapping.get(label, label.upper())


def detect_stack(repos: list[dict[str, Any]], lang_counter: Counter) -> list[str]:
    tech: list[str] = []
    for lang, _ in lang_counter.most_common(8):
        tech.append(normalize_tech(lang))

    topics = Counter()
    for repo in repos[:50]:
        for topic in repo.get("topics") or []:
            topics[topic.lower()] += 1

    topic_map = {
        "react": "REACT",
        "nextjs": "NEXT.JS",
        "next-js": "NEXT.JS",
        "tailwindcss": "TAILWIND",
        "tailwind": "TAILWIND",
        "nodejs": "NODE.JS",
        "node": "NODE.JS",
        "mongodb": "MONGODB",
        "mysql": "MYSQL",
        "firebase": "FIREBASE",
        "supabase": "SUPABASE",
        "machine-learning": "ML",
        "data-science": "DATA SCIENCE",
        "figma": "FIGMA",
        "ui-ux": "UI/UX",
        "web-development": "WEB DEV",
    }
    for topic, _ in topics.most_common(30):
        if topic in topic_map:
            tech.append(topic_map[topic])

    present = set(tech)
    if "JAVASCRIPT" in present or "TYPESCRIPT" in present:
        tech += ["REACT", "NODE.JS"]
    if "HTML5" in present or "CSS3" in present:
        tech += ["FRONTEND"]
    if "PYTHON" in present:
        tech += ["DATA", "AUTOMATION"]

    result = []
    seen = set()
    for t in tech:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result[:12] or ["GITHUB", "OPEN SOURCE", "CODE"]


def get_contribution_days(username: str) -> list[dict[str, Any]]:
    query = '''
    query($login: String!) {
      user(login: $login) {
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
    '''
    try:
        data = request_json(GQL, graphql_body={"query": query, "variables": {"login": username}})
        weeks = (
            data.get("data", {})
            .get("user", {})
            .get("contributionsCollection", {})
            .get("contributionCalendar", {})
            .get("weeks", [])
        )
        days: list[dict[str, Any]] = []
        for w in weeks:
            days.extend(w.get("contributionDays", []))
        return days[-371:] if days else []
    except Exception as e:
        print(f"[warn] GraphQL contribution calendar failed -> {e}", file=sys.stderr)
        return []


def esc(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def truncate(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: max(0, n - 1)].rstrip() + "…"


def repo_display(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered = [r for r in repos if not r.get("archived")]
    filtered.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return filtered[:4]


def lang_percentages(counter: Counter) -> list[tuple[str, int]]:
    total = sum(counter.values()) or 1
    out: list[tuple[str, int]] = []
    for k, v in counter.most_common(6):
        pct = max(1, round((v / total) * 100))
        out.append((normalize_tech(k), pct))
    return out or [("CODE", 100)]


def heat_color(count: int, color: str | None = None) -> str:
    if color and color != "#ebedf0":
        return color
    if count <= 0:
        return "#143125"
    if count == 1:
        return "#0e4429"
    if count <= 3:
        return "#006d32"
    if count <= 6:
        return "#26a641"
    return "#39d353"


def build_heatmap(days: list[dict[str, Any]], x: int, y: int, cell: int = 8, gap: int = 3) -> str:
    if not days:
        rects = []
        for c in range(53):
            for r in range(7):
                opacity = 0.22 + ((c * 3 + r * 5) % 7) * 0.07
                rects.append(
                    f'<rect x="{x + c * (cell + gap)}" y="{y + r * (cell + gap)}" width="{cell}" height="{cell}" rx="2" fill="#22c55e" opacity="{opacity:.2f}">'
                    f'<animate attributeName="opacity" values="{opacity:.2f};0.8;{opacity:.2f}" dur="{3 + (c % 5)}s" begin="{(c+r)%10/10}s" repeatCount="indefinite"/></rect>'
                )
        return "\n".join(rects)

    days = days[-371:]
    rects = []
    for i, d in enumerate(days):
        col = i // 7
        row = i % 7
        if col >= 53:
            break
        count = int(d.get("contributionCount") or 0)
        fill = heat_color(count, d.get("color"))
        pulse = ""
        if count > 0:
            pulse = f'<animate attributeName="opacity" values="0.75;1;0.75" dur="{2 + (count % 4)}s" begin="{(col+row)%8/10}s" repeatCount="indefinite"/>'
        rects.append(
            f'<rect x="{x + col * (cell + gap)}" y="{y + row * (cell + gap)}" width="{cell}" height="{cell}" rx="2" fill="{fill}" opacity="{0.62 if count == 0 else 0.95}">{pulse}</rect>'
        )
    return "\n".join(rects)


def pill(x: int, y: int, label: str, idx: int) -> str:
    colors = ["#38bdf8", "#8b5cf6", "#22c55e", "#f59e0b", "#ec4899", "#14b8a6", "#6366f1", "#f97316"]
    color = colors[idx % len(colors)]
    width = max(76, min(150, 20 + len(label) * 9))
    return f'''
    <g transform="translate({x},{y})" class="float{idx % 4}">
      <rect width="{width}" height="28" rx="14" fill="{color}" opacity="0.16" stroke="{color}" stroke-opacity="0.65"/>
      <circle cx="16" cy="14" r="4" fill="{color}"/>
      <text x="28" y="18" class="pillText" fill="#e5f3ff">{esc(label)}</text>
    </g>'''


def metric_card(x: int, y: int, value: str, label: str, accent: str, delay: str) -> str:
    return f'''
    <g transform="translate({x},{y})" class="cardFloat">
      <rect width="178" height="86" rx="18" fill="#111827" stroke="#263244"/>
      <rect width="178" height="86" rx="18" fill="url(#glass)" opacity="0.5"/>
      <text x="89" y="39" text-anchor="middle" class="metric" fill="{accent}">{esc(value)}</text>
      <text x="89" y="63" text-anchor="middle" class="muted">{esc(label)}</text>
      <animateTransform attributeName="transform" type="translate" values="{x},{y};{x},{y-3};{x},{y}" dur="5s" begin="{delay}" repeatCount="indefinite"/>
    </g>'''


def repo_card(x: int, y: int, repo: dict[str, Any], idx: int) -> str:
    name = truncate(repo.get("name") or "repository", 24)
    desc = truncate(repo.get("description") or "Recently updated repository", 58)
    lang = repo.get("language") or "Code"
    stars = repo.get("stargazers_count") or 0
    forks = repo.get("forks_count") or 0
    return f'''
    <g transform="translate({x},{y})" class="repoCard">
      <rect width="280" height="96" rx="16" fill="#101923" stroke="#273346"/>
      <path d="M18 28 C18 18, 32 18, 32 28 C32 38, 18 38, 18 28" fill="none" stroke="#38bdf8" stroke-width="1.7"/>
      <text x="44" y="28" class="repoTitle" fill="#f8fafc">{esc(name)}</text>
      <text x="18" y="52" class="repoDesc" fill="#9ca3af">{esc(desc)}</text>
      <circle cx="22" cy="76" r="4" fill="#8b5cf6"/>
      <text x="34" y="80" class="mutedSmall">{esc(lang)}</text>
      <text x="188" y="80" class="mutedSmall">★ {stars}</text>
      <text x="232" y="80" class="mutedSmall">⑂ {forks}</text>
      <animate attributeName="opacity" values="0.76;1;0.76" dur="{5+idx}s" begin="{idx/2}s" repeatCount="indefinite"/>
    </g>'''


def progress_bar(x: int, y: int, label: str, pct: int, idx: int) -> str:
    colors = ["#38bdf8", "#8b5cf6", "#22c55e", "#f59e0b", "#ec4899", "#14b8a6"]
    color = colors[idx % len(colors)]
    w = 310
    fill_w = max(12, min(w, int(w * pct / 100)))
    return f'''
    <g transform="translate({x},{y})">
      <text x="0" y="0" class="barLabel" fill="#e5e7eb">{esc(label)}</text>
      <text x="{w}" y="0" text-anchor="end" class="barLabel" fill="#94a3b8">{pct}%</text>
      <rect x="0" y="10" width="{w}" height="10" rx="5" fill="#1f2937"/>
      <rect x="0" y="10" width="{fill_w}" height="10" rx="5" fill="{color}">
        <animate attributeName="width" values="0;{fill_w}" dur="1.6s" begin="{0.2 + idx*0.12}s" fill="freeze"/>
      </rect>
    </g>'''


def generate_svg() -> str:
    user = safe_get(f"{API}/users/{urllib.parse.quote(USERNAME)}", {}) or {}
    repos = get_all_repos(USERNAME)
    langs = get_languages(USERNAME, repos)
    contrib_days = get_contribution_days(USERNAME)

    display_name = user.get("name") or USERNAME
    bio = user.get("bio") or PROFILE_TAGLINE
    location = user.get("location") or "GitHub"
    followers = int(user.get("followers") or 0)
    following = int(user.get("following") or 0)
    public_repos = int(user.get("public_repos") or len(repos))
    total_stars = sum(int(r.get("stargazers_count") or 0) for r in repos)
    total_forks = sum(int(r.get("forks_count") or 0) for r in repos)
    total_contrib = sum(int(d.get("contributionCount") or 0) for d in contrib_days) if contrib_days else 0
    latest = repo_display(repos)
    tech = detect_stack(repos, langs)
    lang_pcts = lang_percentages(langs)

    parts = display_name.split()
    initials = "".join([p[0] for p in parts[:2]]).upper() if parts else USERNAME[:2].upper()
    first_name = parts[0] if parts else display_name
    last_name = " ".join(parts[1:]) if len(parts) > 1 else USERNAME
    now = dt.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    socials = []
    if SOCIAL_INSTAGRAM:
        socials.append(("Instagram", SOCIAL_INSTAGRAM))
    if SOCIAL_LINKEDIN:
        socials.append(("LinkedIn", SOCIAL_LINKEDIN))
    if SOCIAL_EMAIL:
        socials.append(("Email", "mailto:" + SOCIAL_EMAIL if "@" in SOCIAL_EMAIL and not SOCIAL_EMAIL.startswith("mailto:") else SOCIAL_EMAIL))
    if user.get("blog"):
        socials.append(("Website", user.get("blog")))
    if not socials:
        socials = [("GitHub", f"https://github.com/{USERNAME}")]

    pill_svg = []
    px, py = 72, 580
    for i, t in enumerate(tech):
        pill_svg.append(pill(px, py, t, i))
        px += max(86, min(160, 32 + len(t) * 10))
        if px > 680:
            px = 72
            py += 38

    repo_svgs = []
    positions = [(72, 740), (376, 740), (72, 856), (376, 856)]
    for i, r in enumerate(latest[:4]):
        repo_svgs.append(repo_card(positions[i][0], positions[i][1], r, i))
    if not repo_svgs:
        repo_svgs.append(repo_card(72, 740, {"name": "create-your-first-repo", "description": "Your latest repositories will appear here automatically.", "language": "GitHub", "stargazers_count": 0, "forks_count": 0}, 0))

    bars = []
    for i, (label, pct) in enumerate(lang_pcts[:6]):
        bars.append(progress_bar(746, 274 + i * 58, label, pct, i))

    social_links = []
    sx = 72
    for i, (label, url) in enumerate(socials[:4]):
        w = 116 if label != "Email" else 98
        social_links.append(f'''
        <a href="{esc(url)}" target="_blank">
          <g transform="translate({sx},208)" class="social">
            <rect width="{w}" height="34" rx="12" fill="#101923" stroke="#2d3b51"/>
            <text x="{w/2}" y="22" text-anchor="middle" class="socialText" fill="#dbeafe">{esc(label)}</text>
          </g>
        </a>''')
        sx += w + 14

    heatmap = build_heatmap(contrib_days, 72, 444)

    return f'''<svg width="1100" height="1080" viewBox="0 0 1100 1080" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>{esc(display_name)} - animated GitHub profile</title>
  <desc>Auto-updating GitHub profile card generated from live GitHub data.</desc>

  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1100" y2="1080">
      <stop offset="0%" stop-color="#030712"/>
      <stop offset="45%" stop-color="#071323"/>
      <stop offset="100%" stop-color="#0b1020"/>
    </linearGradient>
    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#8b5cf6"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.2 0 0 0 0 0.7 0 0 0 0 1 0 0 0 0.75 0"/>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="24" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
      .sans {{ font-family: Inter, Segoe UI, Arial, sans-serif; }}
      .tiny {{ font: 500 12px ui-monospace, monospace; letter-spacing: 3px; }}
      .muted {{ font: 500 13px ui-monospace, monospace; fill: #94a3b8; }}
      .mutedSmall {{ font: 500 12px ui-monospace, monospace; fill: #94a3b8; }}
      .metric {{ font: 900 32px Inter, Segoe UI, Arial, sans-serif; }}
      .pillText {{ font: 800 12px ui-monospace, monospace; letter-spacing: .7px; }}
      .repoTitle {{ font: 800 15px Inter, Segoe UI, Arial, sans-serif; }}
      .repoDesc {{ font: 500 12px Inter, Segoe UI, Arial, sans-serif; }}
      .barLabel {{ font: 700 13px ui-monospace, monospace; }}
      .socialText {{ font: 700 12px ui-monospace, monospace; }}
      .name {{ font: 900 54px Inter, Segoe UI, Arial, sans-serif; }}
      .role {{ font: 700 18px Inter, Segoe UI, Arial, sans-serif; }}
      .body {{ font: 500 16px Inter, Segoe UI, Arial, sans-serif; }}
      .scan {{ animation: scan 4.8s ease-in-out infinite; }}
      .orb {{ animation: orb 8s ease-in-out infinite; transform-origin: center; }}
      .pulse {{ animation: pulse 2.5s ease-in-out infinite; }}
      .dash {{ stroke-dasharray: 12 18; animation: dash 18s linear infinite; }}
      .float0 {{ animation: float 6s ease-in-out infinite; }}
      .float1 {{ animation: float 7s ease-in-out infinite reverse; }}
      .float2 {{ animation: float 5.5s ease-in-out infinite; }}
      .float3 {{ animation: float 8s ease-in-out infinite reverse; }}
      .social:hover rect, .repoCard:hover rect {{ stroke: #38bdf8; }}
      @keyframes dash {{ to {{ stroke-dashoffset: -900; }} }}
      @keyframes pulse {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
      @keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-5px); }} }}
      @keyframes scan {{ 0%,100% {{ transform: translateY(-25px); opacity: .15; }} 50% {{ transform: translateY(560px); opacity: .55; }} }}
      @keyframes orb {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(22px,-18px) scale(1.06); }} }}
    </style>
  </defs>

  <rect width="1100" height="1080" rx="34" fill="url(#bg)"/>
  <rect x="28" y="28" width="1044" height="1024" rx="30" fill="#08111f" stroke="#1f2a44" filter="url(#softShadow)"/>

  <g opacity="0.45">
    <circle cx="980" cy="110" r="170" fill="#38bdf8" opacity="0.09" class="orb"/>
    <circle cx="870" cy="910" r="210" fill="#8b5cf6" opacity="0.08" class="orb"/>
    <circle cx="120" cy="940" r="190" fill="#22c55e" opacity="0.06" class="orb"/>
    <path d="M44 170 C240 60, 420 280, 620 150 S920 100, 1056 230" stroke="url(#neon)" stroke-width="2" class="dash" opacity="0.55"/>
    <path d="M40 1000 C260 850, 450 1060, 640 900 S925 860, 1060 995" stroke="url(#neon)" stroke-width="2" class="dash" opacity="0.35"/>
  </g>

  <rect x="52" y="54" width="996" height="560" rx="28" fill="#0b1422" stroke="#233047"/>
  <rect x="52" y="54" width="996" height="560" rx="28" fill="url(#glass)"/>
  <rect x="62" y="92" width="976" height="3" fill="url(#neon)" opacity="0.85" class="pulse"/>
  <rect x="62" y="95" width="976" height="34" fill="#38bdf8" opacity="0.06" class="scan"/>

  <g transform="translate(86,95)">
    <circle cx="68" cy="68" r="58" fill="#0f172a" stroke="url(#neon)" stroke-width="3" filter="url(#glow)"/>
    <circle cx="68" cy="68" r="42" fill="#111827"/>
    <text x="68" y="82" text-anchor="middle" class="name" font-size="34" fill="#f8fafc">{esc(initials)}</text>
    <circle cx="26" cy="24" r="5" fill="#22c55e"><animate attributeName="r" values="4;8;4" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="116" cy="112" r="4" fill="#38bdf8"><animate attributeName="r" values="3;7;3" dur="2.8s" repeatCount="indefinite"/></circle>
  </g>

  <text x="230" y="112" class="tiny mono" fill="#38bdf8">const profile = &#123;</text>
  <text x="230" y="178" class="name sans" fill="#f8fafc">{esc(first_name)}</text>
  <text x="230" y="234" class="name sans" fill="#a78bfa">{esc(last_name)}</text>
  <text x="230" y="275" class="tiny mono" fill="#38bdf8">&#125;</text>
  <text x="230" y="314" class="role sans" fill="#dbeafe">{esc(PROFILE_ROLE)}</text>
  <text x="230" y="344" class="body sans" fill="#94a3b8">{esc(truncate(bio, 88))}</text>
  <text x="230" y="382" class="muted mono">📍 {esc(location)}  ·  @{esc(USERNAME)}  ·  {followers} followers  ·  {following} following</text>

  {''.join(social_links)}

  <text x="72" y="666" class="tiny mono" fill="#38bdf8">// LIVE METRICS</text>
  {metric_card(72, 686, str(public_repos), "public repos", "#38bdf8", "0s")}
  {metric_card(278, 686, str(total_stars), "total stars", "#a78bfa", ".4s")}
  {metric_card(484, 686, str(total_forks), "forks", "#22c55e", ".8s")}
  {metric_card(690, 686, str(total_contrib), "year contributions", "#f59e0b", "1.2s")}

  <text x="72" y="418" class="tiny mono" fill="#38bdf8">// CONTRIBUTION FIELD</text>
  <rect x="62" y="430" width="620" height="126" rx="18" fill="#101923" stroke="#273346"/>
  {heatmap}

  <text x="746" y="228" class="tiny mono" fill="#38bdf8">// LANGUAGE SIGNAL</text>
  <rect x="724" y="246" width="326" height="376" rx="22" fill="#101923" stroke="#273346"/>
  {''.join(bars)}

  <text x="72" y="556" class="tiny mono" fill="#38bdf8">// AUTO DETECTED STACK</text>
  {''.join(pill_svg)}

  <text x="72" y="718" class="tiny mono" fill="#38bdf8">// LATEST PROJECTS</text>
  {''.join(repo_svgs)}

  <g transform="translate(724,665)">
    <rect width="326" height="307" rx="22" fill="#101923" stroke="#273346"/>
    <text x="26" y="44" class="tiny mono" fill="#38bdf8">// SYSTEM STATUS</text>
    <text x="26" y="88" class="body sans" fill="#e5e7eb">README engine</text>
    <text x="270" y="88" text-anchor="end" class="body sans" fill="#22c55e">ACTIVE</text>
    <text x="26" y="128" class="body sans" fill="#e5e7eb">Automation</text>
    <text x="270" y="128" text-anchor="end" class="body sans" fill="#38bdf8">6 HOURS</text>
    <text x="26" y="168" class="body sans" fill="#e5e7eb">Data source</text>
    <text x="270" y="168" text-anchor="end" class="body sans" fill="#a78bfa">GITHUB API</text>
    <rect x="26" y="202" width="274" height="42" rx="12" fill="#0b1422" stroke="#263244"/>
    <text x="42" y="228" class="mutedSmall">last sync: {esc(now)}</text>
    <circle cx="286" cy="223" r="6" fill="#22c55e">
      <animate attributeName="opacity" values=".35;1;.35" dur="1.5s" repeatCount="indefinite"/>
    </circle>
  </g>

  <text x="550" y="1030" text-anchor="middle" class="mutedSmall">animated profile generated automatically from GitHub data · no manual stats editing</text>
</svg>'''


def main() -> None:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    svg = generate_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
