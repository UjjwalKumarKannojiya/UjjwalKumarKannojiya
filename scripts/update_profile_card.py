#!/usr/bin/env python3
import html, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
SVG_PATH = ASSETS_DIR / "profile-card.svg"
README_PATH = ROOT / "README.md"
CONFIG_PATH = ROOT / "profile_config.json"

DEFAULT_CONFIG = {
    "profile": {"fallback_name":"Ujjwal Kumar Kannojiya","fallback_username":"UjjwalKumarKannojiya","headline":"Full-stack developer & UI/UX enthusiast crafting","highlight":"scalable products","tagline_suffix":"at the intersection of code and design.","open_status":"open to opportunities"},
    "socials": [{"label":"Instagram","url":"https://instagram.com/ni.mi.sh.___"},{"label":"LinkedIn","url":"https://www.linkedin.com/in/ujjwal-kannojiya-78744723a/"},{"label":"Email","url":"mailto:nk875002@gmail.com"}],
    "tech_groups": {"blue":["Python","JavaScript","TypeScript","Java","C","R"],"purple":["React","Next.js","Node.js","TailwindCSS","Bootstrap","Vite"],"green":["TensorFlow","PyTorch","scikit-learn","NumPy","Pandas"],"orange":["MongoDB","MySQL","AWS","Azure","Apache Hadoop"],"red":["Figma","Adobe PS","Premiere Pro","Power BI"]}
}

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    followers { totalCount }
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name
        isFork
        primaryLanguage { name color }
        repositoryTopics(first: 20) { nodes { topic { name } } }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
"""

NORMALIZE = {"javascript":"JavaScript","typescript":"TypeScript","python":"Python","java":"Java","c":"C","r":"R","react":"React","nextjs":"Next.js","next.js":"Next.js","node":"Node.js","nodejs":"Node.js","node.js":"Node.js","tailwind":"TailwindCSS","tailwindcss":"TailwindCSS","bootstrap":"Bootstrap","vite":"Vite","tensorflow":"TensorFlow","pytorch":"PyTorch","sklearn":"scikit-learn","scikit-learn":"scikit-learn","numpy":"NumPy","pandas":"Pandas","mongodb":"MongoDB","mysql":"MySQL","aws":"AWS","azure":"Azure","hadoop":"Apache Hadoop"}

def esc(v): return html.escape(str(v if v is not None else ""), quote=True)
def short(v, n):
    s = re.sub(r"\s+", " ", str(v or "")).strip()
    return s if len(s) <= n else s[:max(0, n-1)].rstrip() + "…"
def load_config(): return json.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else DEFAULT_CONFIG
def metric_number(v): return (f"{v/1000:.1f}k".replace(".0k","k")) if v >= 1000 else str(v)

def request_github(username, token):
    body = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": username}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","User-Agent":"dynamic-html-style-profile"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode())
    if data.get("errors"): raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data["data"]["user"]

def fallback_user(config, username):
    levels = [0,0,1,1,2,2,1,3,3,2,1,0,1,2,3,4,4,3,2,1,2,3,4,3,2,1,0,1,2,3,3,4,2,1,0,1,2,3,2,1,2,3,4,3,2,1,2,3,3,2,1,0,1,2]
    days = [{"contributionCount": levels[i % len(levels)]} for i in range(371)]
    weeks = [{"contributionDays": days[i:i+7]} for i in range(0, 371, 7)]
    return {"login":username,"name":config["profile"].get("fallback_name",username),"followers":{"totalCount":0},"repositories":{"totalCount":0,"nodes":[]},"contributionsCollection":{"contributionCalendar":{"totalContributions":0,"weeks":weeks}}}

def repos(user):
    login = user.get("login","")
    all_repos = ((user.get("repositories") or {}).get("nodes")) or []
    visible = [r for r in all_repos if not r.get("isFork") and r.get("name") != login]
    return visible or [r for r in all_repos if not r.get("isFork")] or all_repos

def normalize(s): return NORMALIZE.get(str(s or "").strip().lower(), str(s or "").strip())
def detected_stack(user):
    found = set()
    for r in repos(user):
        lang = normalize(((r.get("primaryLanguage") or {}).get("name")) or "")
        if lang: found.add(lang)
        for node in ((r.get("repositoryTopics") or {}).get("nodes") or []):
            topic = normalize((((node or {}).get("topic") or {}).get("name")) or "")
            if topic: found.add(topic)
    return found

def ordered_tech(user, config):
    found = detected_stack(user); groups = config.get("tech_groups") or DEFAULT_CONFIG["tech_groups"]
    return {k: sorted(v, key=lambda x: (x not in found, v.index(x))) for k,v in groups.items()}

def language_stats(user):
    counts, colors = {}, {}
    for r in repos(user):
        lang = ((r.get("primaryLanguage") or {}).get("name")) or ""
        if not lang: continue
        counts[lang] = counts.get(lang, 0) + 1
        colors[lang] = ((r.get("primaryLanguage") or {}).get("color")) or "#58A6FF"
    fallback = [("Python",72,"#3572A5"),("JavaScript",60,"#F1E05A"),("TypeScript",45,"#2B7489"),("Java",30,"#B07219")]
    if not counts: return fallback
    mx = max(counts.values()) or 1
    out = [(lang, max(20, round(count/mx*100)), colors[lang]) for lang,count in sorted(counts.items(), key=lambda x:x[1], reverse=True)[:4]]
    while len(out) < 4: out.append(fallback[len(out)])
    return out

def focus_stats(user):
    found = detected_stack(user)
    return [("Frontend",min(55+(25 if found & {"React","Next.js","TailwindCSS","JavaScript","TypeScript"} else 0),95),"#58A6FF"),("ML/AI",min(45+(20 if found & {"Python","TensorFlow","PyTorch","scikit-learn","NumPy","Pandas"} else 0),95),"#A371F7"),("Backend",min(45+(20 if found & {"Node.js","MongoDB","MySQL"} else 0),95),"#3FB950"),("UI/UX",70,"#D2992A")]

def contribution_levels(user):
    weeks = (((user.get("contributionsCollection") or {}).get("contributionCalendar") or {}).get("weeks")) or []
    levels = []
    for w in weeks[-53:]:
        for d in (w.get("contributionDays") or [])[:7]:
            c = int(d.get("contributionCount") or 0)
            levels.append(0 if c == 0 else 1 if c < 3 else 2 if c < 7 else 3 if c < 12 else 4)
    if not levels: levels = [0,0,1,1,2,2,1,3,3,2,1,0,1,2,3,4,4,3,2,1,2,3,4,3,2,1,0,1,2,3,3,4,2,1,0,1,2,3,2,1,2,3,4,3,2,1,2,3,3,2,1,0,1,2] * 7
    return levels

def cell_grid(user):
    colors = {0:("#161B22","#21262D"),1:("#0E4429","#26A641"),2:("#006D32","#26A641"),3:("#26A641","#39D353"),4:("#39D353","#39D353")}
    lv = contribution_levels(user); parts = []
    for w in range(53):
        for d in range(7):
            idx = w*7+d; fill, stroke = colors[lv[idx] if idx < len(lv) else 0]
            parts.append(f'<rect x="{54+w*14}" y="{610+d*14}" width="11" height="11" rx="2" fill="{fill}" stroke="{stroke}"/>')
    return "\n".join(parts)

def bar_rows(stats, x, y):
    out = []
    for i, (label,pct,color) in enumerate(stats[:4]):
        yy = y + i*22
        out.append(f'<text x="{x}" y="{yy+8}" class="barLabel">{esc(short(label,10))}</text><rect x="{x+86}" y="{yy}" width="204" height="6" rx="3" fill="#21262D"/><rect x="{x+86}" y="{yy}" width="{round(204*pct/100)}" height="6" rx="3" fill="{esc(color)}"/><text x="{x+322}" y="{yy+8}" class="barPct">{pct}%</text>')
    return "\n".join(out)

def pill(label, group, x, y):
    palette = {"blue":"#58A6FF","purple":"#A371F7","green":"#3FB950","orange":"#D2992A","red":"#F85149"}
    color = palette.get(group, "#58A6FF"); w = max(54, len(label)*7+24)
    return f'<g transform="translate({x} {y})"><rect width="{w}" height="24" rx="12" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.30"/><text x="{w/2:.1f}" y="16" text-anchor="middle" class="pill" fill="{color}">{esc(label)}</text></g>', w

def tech_pills(user, config):
    groups = ordered_tech(user, config); x,y=32,924; out=[]
    for g in ["blue","purple","green","orange","red"]:
        for label in groups.get(g, []):
            item,w = pill(label,g,x,y)
            if x+w > 828:
                x,y=32,y+34; item,w = pill(label,g,x,y)
            out.append(item); x += w + 8
    return "\n".join(out)

SVG_TEMPLATE = """<svg width="860" height="1140" viewBox="0 0 860 1140" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{full_name} GitHub profile card">
  <defs>
    <linearGradient id="avatarGrad" x1="55" y1="52" x2="145" y2="142" gradientUnits="userSpaceOnUse"><stop stop-color="#58A6FF"/><stop offset="1" stop-color="#A371F7"/></linearGradient>
    <radialGradient id="blueGlow" cx="50%" cy="50%" r="50%"><stop stop-color="#58A6FF" stop-opacity="0.12"/><stop offset="1" stop-color="#58A6FF" stop-opacity="0"/></radialGradient>
    <radialGradient id="purpleGlow" cx="50%" cy="50%" r="50%"><stop stop-color="#A371F7" stop-opacity="0.11"/><stop offset="1" stop-color="#A371F7" stop-opacity="0"/></radialGradient>
    <clipPath id="cardClip"><rect x="0" y="0" width="860" height="1140" rx="12"/></clipPath>
    <style>
      .section {{ font: 700 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #58A6FF; letter-spacing: 2.2px; }}
      .muted {{ font: 400 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }}
      .body {{ font: 500 14px Inter, Segoe UI, Arial, sans-serif; fill: #8B949E; }}
      .metricNum {{ font: 800 25px Inter, Segoe UI, Arial, sans-serif; }}
      .metricLabel {{ font: 400 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }}
      .pill {{ font: 700 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: .3px; }}
      .barLabel {{ font: 400 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }}
      .barPct {{ font: 400 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #8B949E; }}
      .quoteText {{ font: italic 13px Inter, Segoe UI, Arial, sans-serif; fill: #8B949E; }}
      .quoteAttr {{ font: 700 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; fill: #A371F7; }}
      @keyframes typing {{ 0% {{ clip-path: inset(0 100% 0 0); }} 50% {{ clip-path: inset(0 0 0 0); }} 70% {{ clip-path: inset(0 0 0 0); }} 100% {{ clip-path: inset(0 100% 0 0); }} }}
      @keyframes blink {{ 0%,49% {{ opacity: 1; }} 50%,100% {{ opacity: 0; }} }}
      .typingText {{ animation: typing 3s steps(30) infinite; }}
      .cursor {{ animation: blink .7s step-end infinite; }}
    </style>
  </defs>
  <g clip-path="url(#cardClip)">
    <rect width="860" height="1140" rx="12" fill="#0D1117"/><rect x="0.5" y="0.5" width="859" height="1139" rx="11.5" stroke="#21262D"/>
    <circle cx="825" cy="-20" r="150" fill="url(#blueGlow)"/><circle cx="-18" cy="1040" r="125" fill="url(#purpleGlow)"/>
    <g transform="translate(32 40)"><circle cx="45" cy="45" r="45" fill="url(#avatarGrad)"/><circle cx="45" cy="45" r="43.5" stroke="#21262D" stroke-width="3"/><text x="45" y="58" text-anchor="middle" style="font-weight:800;font-size:32px;fill:#0D1117;font-family:Inter,Segoe UI,Arial,sans-serif;">UK</text><text x="122" y="13" class="muted"><tspan fill="#58A6FF">const</tspan> dev = &#123;</text><text x="122" y="52" style="font-weight:800;font-size:32px;fill:#E6EDF3;font-family:Inter,Segoe UI,Arial,sans-serif;">{first_line}</text><text x="122" y="88" style="font-weight:800;font-size:32px;fill:#A371F7;font-family:Inter,Segoe UI,Arial,sans-serif;">{second_line}</text><text x="122" y="116" class="muted">&#125;</text><text x="122" y="150" class="body">{headline}</text><text x="122" y="172" class="body"><tspan fill="#58A6FF" font-weight="700">{highlight}</tspan> {tagline_suffix}</text></g>
    <line x1="32" y1="250" x2="828" y2="250" stroke="#21262D"/>
    <text x="32" y="292" class="section">// SOCIALS</text>
    <g transform="translate(32 314)"><rect width="114" height="34" rx="6" fill="#161B22" stroke="#21262D"/><circle cx="18" cy="17" r="7" fill="none" stroke="#8B949E" stroke-width="1.5"/><circle cx="18" cy="17" r="2.8" fill="none" stroke="#8B949E" stroke-width="1.4"/><circle cx="24" cy="11" r="1.6" fill="#8B949E"/><text x="38" y="22" class="muted">Instagram</text></g>
    <g transform="translate(156 314)"><rect width="104" height="34" rx="6" fill="#161B22" stroke="#21262D"/><rect x="14" y="10" width="16" height="16" rx="2" fill="#8B949E"/><text x="18" y="22" style="font-weight:700;font-size:13px;fill:#161B22;font-family:monospace;">in</text><text x="42" y="22" class="muted">LinkedIn</text></g>
    <g transform="translate(270 314)"><rect width="82" height="34" rx="6" fill="#161B22" stroke="#21262D"/><path d="M14 12h16v12H14z" fill="none" stroke="#8B949E" stroke-width="1.3"/><path d="M14 13l8 6 8-6" fill="none" stroke="#8B949E" stroke-width="1.3"/><text x="42" y="22" class="muted">Email</text></g>
    <text x="32" y="392" class="section">// METRICS</text>
    <g transform="translate(32 414)"><rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/><text x="126" y="37" text-anchor="middle" class="metricNum" fill="#58A6FF">{contrib_total}</text><text x="126" y="58" text-anchor="middle" class="metricLabel">contributions</text></g>
    <g transform="translate(304 414)"><rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/><text x="126" y="37" text-anchor="middle" class="metricNum" fill="#A371F7">{repo_total}</text><text x="126" y="58" text-anchor="middle" class="metricLabel">projects</text></g>
    <g transform="translate(576 414)"><rect width="252" height="76" rx="8" fill="#161B22" stroke="#21262D"/><text x="126" y="37" text-anchor="middle" class="metricNum" fill="#3FB950">{tech_count}</text><text x="126" y="58" text-anchor="middle" class="metricLabel">tech stacks</text></g>
    <text x="32" y="536" class="section">// CONTRIBUTION GRAPH</text>
    <g transform="translate(32 556)"><rect width="796" height="142" rx="8" fill="#161B22" stroke="#21262D"/><text x="22" y="31" class="muted">streak &amp; activity</text></g>{grid}
    <g transform="translate(32 732)"><rect width="388" height="124" rx="8" fill="#161B22" stroke="#21262D"/><circle cx="20" cy="22" r="3" fill="#58A6FF"/><text x="34" y="26" class="muted">top languages</text>{language_bars}</g>
    <g transform="translate(440 732)"><rect width="388" height="124" rx="8" fill="#161B22" stroke="#21262D"/><circle cx="20" cy="22" r="3" fill="#58A6FF"/><text x="34" y="26" class="muted">focus areas</text>{focus_bars}</g>
    <text x="32" y="902" class="section">// TECH STACK</text>{tech_pills}
    <line x1="32" y1="1010" x2="828" y2="1010" stroke="#21262D"/>
    <g transform="translate(32 1024)"><rect x="0" y="0" width="796" height="42" rx="0 6 6 0" fill="#161B22"/><rect x="0" y="0" width="3" height="42" fill="#A371F7"/><text x="16" y="18" class="quoteText">"Code is like humor. When you have to explain it, it's bad."</text><text x="16" y="35" class="quoteAttr">— Cory House</text></g>
    <g transform="translate(32 1092)"><text class="muted typingText">building the future, one commit at a time...</text><rect x="304" y="-13" width="2" height="17" fill="#58A6FF" class="cursor"/><circle cx="650" cy="-7" r="4" fill="#3FB950"/><text x="664" y="-3" class="muted">{open_status}</text></g>
  </g>
</svg>"""

def generate_svg(user, config):
    full_name = user.get("name") or config["profile"].get("fallback_name")
    parts = full_name.split()
    first_line = " ".join(parts[:2]) if len(parts) >= 2 else full_name
    second_line = " ".join(parts[2:]) if len(parts) > 2 else "Kannojiya"
    repo_total = int((user.get("repositories") or {}).get("totalCount") or 0)
    contrib_total = int((((user.get("contributionsCollection") or {}).get("contributionCalendar") or {}).get("totalContributions")) or 0)
    tech_count = sum(len(v) for v in (config.get("tech_groups") or {}).values())
    return SVG_TEMPLATE.format(
        full_name=esc(full_name),
        first_line=esc(short(first_line,28)),
        second_line=esc(short(second_line,28)),
        headline=esc(short(config["profile"].get("headline"),64)),
        highlight=esc(config["profile"].get("highlight")),
        tagline_suffix=esc(short(config["profile"].get("tagline_suffix"),50)),
        contrib_total=esc(metric_number(contrib_total)),
        repo_total=esc(metric_number(repo_total)),
        tech_count=esc(metric_number(tech_count)),
        grid=cell_grid(user),
        language_bars=bar_rows(language_stats(user),18,46),
        focus_bars=bar_rows(focus_stats(user),18,46),
        tech_pills=tech_pills(user, config),
        open_status=esc(config["profile"].get("open_status")),
    )

def generate_readme(config):
    badges = {"Instagram":"Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white","LinkedIn":"LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white","Email":"Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"}
    links=[]
    for item in config.get("socials", DEFAULT_CONFIG["socials"]):
        label=item.get("label","Link"); url=item.get("url","#")
        links.append(f'<a href="{url}"><img src="https://img.shields.io/badge/{badges.get(label,label)}" alt="{esc(label)}" /></a>')
    return '<div align="center">\n\n<img src="./assets/profile-card.svg" width="100%" alt="Ujjwal Kumar Kannojiya GitHub profile" />\n\n<br/>\n<br/>\n\n' + " ".join(links) + '\n\n</div>\n'

def main():
    config=load_config()
    username=os.getenv("PROFILE_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER") or config["profile"].get("fallback_username")
    token=os.getenv("GITHUB_TOKEN","")
    try:
        if not token: raise RuntimeError("No token")
        user=request_github(username, token)
    except Exception as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        user=fallback_user(config, username)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(generate_svg(user, config), encoding="utf-8")
    README_PATH.write_text(generate_readme(config), encoding="utf-8")
    print("Profile card updated")

if __name__=="__main__":
    main()
