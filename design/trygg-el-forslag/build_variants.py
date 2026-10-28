"""Fem förslag på Trygg el-sektionen. Kör: python3 design/trygg-el-forslag/build_variants.py"""
from pathlib import Path

OUT = Path(__file__).parent
P = [
    "Att kunna känna sig trygg och säker i sitt hem och i andra miljöer där vi vistas är nog en självklarhet för de flesta av oss. I Sverige har vi i många år arbetat intensivt med att begränsa olyckor och andra skador orsakade av el, bland annat genom Elsäkerhetsverkets arbete. Och även om vi varit framgångsrika jämfört med många andra länder händer det dessvärre varje år ett antal elolyckor.",
    "Idag vet nog de flesta att den bästa försäkringen mot elolyckor är att anlita en elyrkesman, en riktig elektriker kort sagt.",
    "Samtliga våra montörer är elyrkesmän och har ABL- eller BB1-behörighet. Alla av oss utförda arbeten, nyinstallationer och reparationsarbeten, åtföljs av garanti och Bloms El & Data är naturligtvis ansvarsförsäkrade för din skull. Allt elmaterial som används i installationer utförda av oss är CE-märkt och i övrigt av högsta kvalité.",
    "Är du tveksam eller känner oro över din elsäkerhet, låt oss hjälpa dig göra en sakkunnig och kompetent bedömning.",
]
USPS = [("ABL / BB1-behörighet", "Alla montörer är certifierade elektriker."),
        ("Registrerad hos Elsäkerhetsverket", "För lågspänningsarbeten i alla relevanta kategorier."),
        ("Garanti på alla arbeten", "Nyinstallationer och reparationer omfattas."),
        ("CE-märkt material", "Allt elmaterial håller högsta kvalité.")]
ICONS = [
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="9" r="6"/><path d="M8.5 14l-1.5 8 5-3 5 3-1.5-8"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M10 9.5a3 3 0 1 0 0 5M17 9.5h-3v5h3M14 12h2.5"/></svg>',
]
ps = lambda *x: "".join(f"<p>{t.replace('&', '&amp;')}</p>" for t in x)
BTNS = '<div class="btns"><a class="btn btn-red" href="#">Ring oss</a><a class="btn {g} arrow" href="#">Kontakta oss </a></div>'

V = {}
# 1 Mörk delad med checklista (dagens, utan foto ovanför)
V[1] = ("Mörk, två kolumner", f'''<section class="sec dark"><div class="wrap split" style="align-items:start">
<div class="prose"><span class="eyebrow">El och säkerhet</span><h2 class="h2">Trygg el</h2>{ps(*P[:2])}{BTNS.format(g="btn-ghost")}</div>
<div class="prose">{ps(*P[2:])}<div class="usps" style="flex-direction:column;gap:12px;margin-top:8px">{"".join(f'<span class="chk">{u}</span>' for u, _ in USPS)}</div></div></div></section>''')
# 2 Ljus med fyra ikonkort
V[2] = ("Ljus med ikonkort", f'''<section class="sec" style="background:#fff"><div class="wrap">
<div class="split" style="align-items:end;margin-bottom:48px"><div class="prose"><span class="eyebrow">El och säkerhet</span><h2 class="h2" style="font-size:56px">Trygg el, gjord av riktiga elektriker</h2></div>
<div class="prose">{ps(P[0])}</div></div>
<div class="grid g4">{"".join(f'<div class="tcard"><span class="ic">{i}</span><b>{u}</b><small>{d}</small></div>' for (u, d), i in zip(USPS, ICONS))}</div>
<div class="split" style="margin-top:48px;align-items:center"><div class="prose"><p class="big">{P[1]}</p></div><div class="prose">{ps(P[3])}{BTNS.format(g="btn-line")}</div></div>
</div></section>''')
# 3 Helbild bakom med glaskort
V[3] = ("Foto i bakgrunden med glaskort", f'''<section class="band" style="padding-block:120px"><img src="../../site/img/elskap.jpg" alt=""><div class="wrap split" style="align-items:center">
<div class="prose"><span class="eyebrow">El och säkerhet</span><h2 class="h2" style="font-size:56px">Trygg el</h2>{ps(*P[:2])}{BTNS.format(g="btn-ghost")}</div>
<div class="glass">{"".join(f'<div class="gl"><span class="ic">{i}</span><span><b>{u}</b><small>{d}</small></span></div>' for (u, d), i in zip(USPS, ICONS))}</div></div></section>''')
# 4 Röd med stort citat
V[4] = ("Röd med stort citat", f'''<section class="sec red"><div class="wrap">
<span class="eyebrow">Trygg el</span>
<p class="quote-big">”Den bästa försäkringen mot elolyckor är att anlita en elyrkesman, en riktig elektriker kort sagt.”</p>
<div class="grid g3" style="margin-top:56px">
<div class="prose">{ps(P[0])}</div><div class="prose">{ps(P[2])}</div>
<div class="prose">{ps(P[3])}<div class="usps" style="flex-direction:column;gap:10px">{"".join(f'<span class="chk">{u}</span>' for u, _ in USPS)}</div>{BTNS.format(g="btn-ghost").replace("btn-red", "btn-white")}</div></div>
</div></section>''')
# 5 Porträtt och siffror
V[5] = ("Porträtt med fakta", f'''<section class="sec gray" style="padding:0"><div class="pf">
<div class="pf-img"><img src="../../site/img/portratt.jpg" alt=""><div class="pf-tag"><b>Sedan 2008</b>Certifierade elektriker i Göteborg</div></div>
<div class="pf-text prose"><span class="eyebrow">El och säkerhet</span><h2 class="h2">Trygg el i hemmet och på jobbet</h2>{ps(P[0], P[2])}
<div class="facts"><div><b>ABL/BB1</b><small>Behöriga montörer</small></div><div><b>Garanti</b><small>På alla arbeten</small></div><div><b>CE</b><small>Märkt material</small></div></div>
{ps(P[3])}{BTNS.format(g="btn-line")}</div></div></section>''')

CSS = """
body{margin:0}
.tcard{background:var(--light);border-radius:18px;padding:28px;display:flex;flex-direction:column;gap:8px}
.tcard .ic,.gl .ic{width:52px;height:52px;border-radius:14px;background:var(--red);color:#fff;display:grid;place-items:center;margin-bottom:10px;flex:none}
.tcard .ic svg,.gl .ic svg{width:26px;height:26px}
.tcard b{font-size:18px}.tcard small{color:var(--muted);font-size:14.5px;line-height:1.6}
.big{font-size:28px!important;font-weight:600;color:var(--ink)!important;line-height:1.35}
.band::after{background:linear-gradient(90deg,rgba(20,8,8,.88),rgba(20,8,8,.55))!important}
.glass{display:grid;gap:14px}
.gl{display:flex;gap:16px;align-items:center;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);backdrop-filter:blur(10px);border-radius:16px;padding:18px 20px}
.gl b{display:block;font-size:17px}.gl small{color:rgba(255,255,255,.75);font-size:14px}
.quote-big{font-size:52px;font-weight:700;line-height:1.15;letter-spacing:-.02em;max-width:20ch;text-wrap:balance}
.pf{display:grid;grid-template-columns:1fr 1.1fr;min-height:760px}
.pf-img{position:relative}.pf-img img{width:100%;height:100%;object-fit:cover;filter:grayscale(1)}
.pf-img::after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(139,0,0,.6),transparent 55%)}
.pf-tag{position:absolute;z-index:2;left:48px;bottom:44px;color:#fff;font-size:14px}.pf-tag b{display:block;font-size:30px}
.pf-text{padding:90px 120px 90px 80px;justify-content:center}
.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:8px 0}
.facts div{background:#fff;border-radius:14px;padding:18px;box-shadow:var(--shadow-sm)}
.facts b{display:block;font-size:24px;color:var(--red)}.facts small{color:var(--muted)}
"""
for n, (name, html) in V.items():
    (OUT / f"trygg-el-{n}.html").write_text(f"""<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trygg el – förslag {n}</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="../../site/assets/style.css"><style>{CSS}</style></head><body>{html.replace('src="img/', 'src="../../site/img/')}</body></html>""", encoding="utf-8")
print("klart")
