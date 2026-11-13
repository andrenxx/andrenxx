"""Gera o gráfico de atividade do GitHub dos últimos ~4 meses (tema escuro e claro).

Uso:
  GITHUB_TOKEN=... python3 activity.py            # busca os dados na API do GitHub
  python3 activity.py --data contribs.json        # usa um JSON já baixado (resposta do GraphQL)
Saída: dist/activity-dark.svg e dist/activity-light.svg
"""
import base64
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "andrenxx")
WEEKS = 18  # ~4 meses
ROOT = Path(__file__).parent
OUT = ROOT / "dist"

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

THEMES = {
    "dark": dict(bg="#0a0c11", line="#232836", ink="#eceef4", ink3="#8a91a3",
                 ramp=["#151924", "#1e2b4a", "#253c6d", "#4a64a3", "#8ca5dd"]),
    "light": dict(bg="#f5f6f9", line="#dfe2ea", ink="#0d1120", ink3="#596074",
                  ramp=["#e6e9f0", "#c9d3ec", "#8ea2d6", "#4a64a3", "#253c6d"]),
}


def fetch():
    token = os.environ["GITHUB_TOKEN"]
    to = dt.datetime.now(dt.timezone.utc)
    frm = to - dt.timedelta(weeks=WEEKS + 1)
    body = json.dumps({"query": QUERY, "variables": {"login": USER, "from": frm.isoformat(), "to": to.isoformat()}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def font(name):
    return base64.b64encode((ROOT / "fonts" / f"{name}.ttf").read_bytes()).decode()


def level(n, cuts):
    # níveis por quartil dos dias com atividade, como o GitHub faz
    if n == 0:
        return 0
    return 1 + sum(n > c for c in cuts)


def render(weeks, total, t):
    cell, gap = 28, 6
    step = cell + gap
    left, top = 48, 104
    grid_w = len(weeks) * step - gap
    width = 1200
    days = [d for w in weeks for d in w]
    vals = sorted(d["contributionCount"] for d in days if d["contributionCount"] > 0) or [1]
    cuts = [vals[int(len(vals) * q)] for q in (0.25, 0.5, 0.75)]

    rects, labels = [], []
    last_month = None
    for i, w in enumerate(weeks):
        x = left + i * step
        first = dt.date.fromisoformat(w[0]["date"])
        if first.month != last_month and (i == 0 or first.day <= 7):
            labels.append(f'<text class="t" x="{x}" y="{top - 16}" font-size="14" fill="{t["ink3"]}">{MONTHS[first.month - 1]}</text>')
            last_month = first.month
        for d in w:
            row = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            c = t["ramp"][level(d["contributionCount"], cuts)]
            rects.append(
                f'<rect x="{x}" y="{top + row * step}" width="{cell}" height="{cell}" rx="6" fill="{c}" '
                f'style="animation-delay:{i * 0.035:.3f}s,{1.6 + i * 0.06 + row * 0.02:.3f}s"/>'
            )

    # escala e total à direita do grid
    sx = left + grid_w + 72
    legend = "".join(
        f'<rect x="{sx + 62 + k * 24}" y="{top + 6 * step + 6}" width="18" height="18" rx="4" fill="{c}"/>'
        for k, c in enumerate(t["ramp"])
    )
    css = (
        f"@font-face{{font-family:'t';src:url(data:font/ttf;base64,{font('text')}) format('truetype');}}"
        f"@font-face{{font-family:'b';src:url(data:font/ttf;base64,{font('text-bold')}) format('truetype');}}"
        f"@font-face{{font-family:'d';src:url(data:font/ttf;base64,{font('display')}) format('truetype');}}"
        ".t{font-family:'t'}.b{font-family:'b'}.d{font-family:'d'}"
        "rect[style]{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.16,1,.3,1) both,wave 5s ease-in-out infinite}"
        "@keyframes wave{0%,9%,100%{transform:none;filter:none}4%{transform:translateY(-5px) scale(1.08);filter:brightness(1.7)}}"
        "@keyframes pop{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
        "@media (prefers-reduced-motion:reduce){rect{animation:none!important}}"
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="380" viewBox="0 0 {width} 380" role="img" aria-label="{total} contribuições no GitHub nos últimos 4 meses">
<style>{css}</style>
<rect width="{width}" height="380" rx="18" fill="{t['bg']}"/>
<rect x=".5" y=".5" width="{width - 1}" height="379" rx="17.5" fill="none" stroke="{t['line']}"/>
<text class="b" x="{left}" y="54" font-size="17" fill="{t['ink3']}">Atividade · últimos 4 meses</text>
{''.join(labels)}
{''.join(rects)}
<text class="d" x="{sx}" y="{top + 110}" font-size="132" fill="{t['ink']}">{total}</text>
<text class="t" x="{sx + 4}" y="{top + 146}" font-size="20" fill="{t['ink3']}">contribuições</text>
</svg>"""


def main():
    if "--data" in sys.argv:
        data = json.loads(Path(sys.argv[sys.argv.index("--data") + 1]).read_text())
    else:
        data = fetch()
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]][-WEEKS:]
    total = sum(d["contributionCount"] for w in weeks for d in w)
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"activity-{name}.svg").write_text(render(weeks, total, t))
    print(f"ok: {total} contribuições em {len(weeks)} semanas")


if __name__ == "__main__":
    main()
