"""Gera os SVGs do README do perfil do GitHub (tema escuro e claro).

Rode: python3 build.py
As fontes (Archivo) vão embutidas em cada SVG, porque o GitHub não carrega fontes externas.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)


def font(name):
    return base64.b64encode((ROOT / "fonts" / f"{name}.ttf").read_bytes()).decode()


FONTS = {k: font(k) for k in ("display", "text", "text-bold")}

THEMES = {
    "dark": dict(bg="#0a0c11", raise_="#10131a", raise2="#151924", ink="#eceef4", ink2="#b0b6c6",
                 ink3="#8a91a3", line="#232836", accent="#253c6d", accent_text="#6880bb", dot="#6880bb"),
    "light": dict(bg="#f5f6f9", raise_="#ffffff", raise2="#eceff5", ink="#0d1120", ink2="#3b4254",
                  ink3="#596074", line="#dfe2ea", accent="#253c6d", accent_text="#253c6d", dot="#253c6d"),
}


def style(t, used):
    faces = "".join(
        f"@font-face{{font-family:'{n}';src:url(data:font/ttf;base64,{FONTS[n]}) format('truetype');}}" for n in used
    )
    return f"""<style>{faces}
.d{{font-family:'display';text-transform:uppercase}}
.t{{font-family:'text'}}
.b{{font-family:'text-bold'}}
@keyframes up{{from{{transform:translateY(26px);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@keyframes flow{{to{{stroke-dashoffset:-20}}}}
@keyframes drop{{0%,8%{{opacity:0;transform:translateY(-8px)}}16%,88%{{opacity:1;transform:none}}100%{{opacity:0}}}}
.in1{{animation:up .9s cubic-bezier(.16,1,.3,1) both}}
.in2{{animation:up .9s .09s cubic-bezier(.16,1,.3,1) both}}
.in3{{animation:fade .8s .35s both}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
.flow{{animation:flow 1.2s linear infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def header(name, t):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="André Natividade, desenvolvedor full stack no Rio de Janeiro">
{style(t, ["display", "text", "text-bold"])}
<rect width="1200" height="320" rx="18" fill="{t['bg']}"/>
<rect x=".5" y=".5" width="1199" height="319" rx="17.5" fill="none" stroke="{t['line']}"/>
<g clip-path="url(#c)">
  <text class="d in1" x="56" y="158" font-size="118" fill="{t['ink']}" letter-spacing="-1">André</text>
  <text class="d in2" x="56" y="262" font-size="118" fill="{t['accent_text']}" letter-spacing="-1">Natividade</text>
</g>
<clipPath id="c"><rect x="0" y="40" width="760" height="250"/></clipPath>
<line x1="780" y1="64" x2="780" y2="256" stroke="{t['line']}"/>
<g class="in3">
  <text class="b" x="812" y="124" font-size="26" fill="{t['ink']}">Desenvolvedor full stack</text>
  <text class="t" x="812" y="158" font-size="20" fill="{t['ink3']}">Rio de Janeiro, Brasil</text>
  <circle class="pulse" cx="818" cy="211" r="5" fill="{t['dot']}"/>
  <text class="b" x="832" y="217" font-size="17" fill="{t['accent_text']}">andrenatividade.is-a.dev</text>
</g>
</svg>"""
    (OUT / f"header-{name}.svg").write_text(svg)


def card(slug, title, line1, line2, tags, visual, name, t):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="590" height="230" viewBox="0 0 590 230" role="img" aria-label="{title}: {line1} {line2}">
{style(t, ["display", "text", "text-bold"])}
<rect width="590" height="230" rx="16" fill="{t['raise_']}"/>
<rect x=".5" y=".5" width="589" height="229" rx="15.5" fill="none" stroke="{t['line']}"/>
<text class="d" x="30" y="70" font-size="46" fill="{t['ink']}">{title}</text>
<text class="t" x="30" y="108" font-size="17" fill="{t['ink2']}">{line1}</text>
<text class="t" x="30" y="132" font-size="17" fill="{t['ink2']}">{line2}</text>
<text class="t" x="30" y="196" font-size="15" fill="{t['ink3']}">{tags}</text>
<text class="b" x="560" y="196" font-size="15" fill="{t['accent_text']}" text-anchor="end">→</text>
{visual(t)}
</svg>"""
    (OUT / f"{slug}-{name}.svg").write_text(svg)


def kanban(t):
    cols = ["A fazer", "Fazendo", "Feito"]
    parts = []
    x0 = 330
    for i, c in enumerate(cols):
        x = x0 + i * 78
        parts.append(f'<text class="t" x="{x}" y="44" font-size="12" fill="{t["ink3"]}">{c}</text>')
        if i:
            parts.append(f'<line x1="{x - 8}" y1="30" x2="{x - 8}" y2="150" stroke="{t["line"]}"/>')
        n = [2, 1, 2][i]
        for j in range(n):
            delay = (i * 2 + j) * 0.35
            fill = t["accent"] if i == 1 else t["raise2"]
            parts.append(
                f'<rect x="{x}" y="{56 + j * 30}" width="66" height="22" rx="5" fill="{fill}" stroke="{t["line"]}" '
                f'style="animation:drop 6s {delay:.2f}s infinite both"/>'
            )
    return "".join(parts)


def network(t):
    a, b, s = (360, 52), (520, 52), (440, 130)
    return f"""
<path class="flow" d="M{a[0] + 26} {a[1]} H{b[0] - 26}" stroke="{t['accent_text']}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>
<path class="flow" d="M{a[0]} {a[1] + 18} V100 Q{a[0]} 130 {s[0] - 40} 130" stroke="{t['ink3']}" stroke-width="1.5" stroke-dasharray="3 7" fill="none" opacity=".7"/>
<path class="flow" d="M{b[0]} {b[1] + 18} V100 Q{b[0]} 130 {s[0] + 40} 130" stroke="{t['ink3']}" stroke-width="1.5" stroke-dasharray="3 7" fill="none" opacity=".7"/>
<rect x="{a[0] - 30}" y="{a[1] - 18}" width="60" height="36" rx="8" fill="{t['raise2']}" stroke="{t['line']}"/>
<rect x="{b[0] - 30}" y="{b[1] - 18}" width="60" height="36" rx="8" fill="{t['raise2']}" stroke="{t['line']}"/>
<rect x="{s[0] - 40}" y="{s[1] - 18}" width="80" height="36" rx="8" fill="{t['raise2']}" stroke="{t['accent_text']}"/>
<text class="t" x="{a[0]}" y="{a[1] + 5}" font-size="12" fill="{t['ink2']}" text-anchor="middle">jogador</text>
<text class="t" x="{b[0]}" y="{b[1] + 5}" font-size="12" fill="{t['ink2']}" text-anchor="middle">jogador</text>
<text class="t" x="{s[0]}" y="{s[1] + 5}" font-size="12" fill="{t['ink']}" text-anchor="middle">servidor</text>
<text class="t" x="440" y="40" font-size="11" fill="{t['accent_text']}" text-anchor="middle">WebRTC</text>"""


for name, t in THEMES.items():
    header(name, t)
    card("dumpit", "DumpIt", "Texto livre vira Kanban com IA.", "",
         "React · TypeScript · Supabase", kanban, name, t)
    card("clover", "Clover MMO", "RPG online no navegador.", "",
         "Phaser 4 · Cloudflare · WebRTC", network, name, t)

print("ok:", sorted(p.name for p in OUT.iterdir()))
