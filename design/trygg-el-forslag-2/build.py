"""Tio kompakta förslag på Trygg el. Kör: python3 design/trygg-el-forslag-2/build.py"""
from pathlib import Path

OUT = Path(__file__).parent
LEAD = "Den bästa försäkringen mot elolyckor är att anlita en riktig elektriker."
BODY = "Alla våra montörer har ABL- eller BB1-behörighet. Arbetena omfattas av garanti, vi är ansvarsförsäkrade och använder bara CE-märkt material."
ASK = "Känner du oro för elsäkerheten hemma eller på jobbet? Vi gör en sakkunnig bedömning."
FACTS = [("Behörighet", "ABL / BB1"), ("Registrering", "Elsäkerhetsverket"), ("Garanti", "På alla arbeten"), ("Material", "CE-märkt")]
KOLLA = '<a class="kolla" href="https://www.elsakerhetsverket.se/" target="_blank" rel="noopener">Kolla elföretaget hos Elsäkerhetsverket ↗</a>'
CTA = '<div class="btns"><a class="btn btn-red" href="#">Ring oss</a><a class="btn btn-line arrow" href="#">Boka bedömning </a></div>'

V = {}
V[1] = ("Faktablad", f'''<section class="t1"><div class="wrap">
<div><span class="eyebrow">Trygg el</span><h2>{LEAD}</h2><p>{ASK}</p>{CTA}</div>
<dl>{"".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in FACTS)}</dl></div></section>''')

V[2] = ("Mätprotokoll", f'''<section class="t2"><div class="wrap">
<div class="txt"><span class="eyebrow">Trygg el</span><h2>Kontrollerat innan det slås på</h2><p>{BODY}</p>{KOLLA}</div>
<table><caption>Bloms El &amp; Data · egenkontroll</caption><thead><tr><th>Kontrollpunkt</th><th>Resultat</th></tr></thead><tbody>
<tr><td>Montörens behörighet</td><td>ABL / BB1</td></tr><tr><td>Registrerat elinstallationsföretag</td><td>Ja</td></tr>
<tr><td>Ansvarsförsäkring</td><td>Ja</td></tr><tr><td>Garanti på utfört arbete</td><td>Ja</td></tr><tr><td>Material</td><td>CE-märkt</td></tr></tbody></table></div></section>''')

V[3] = ("En mening", f'''<section class="t3"><div class="wrap"><p class="big">{LEAD}</p><div class="side"><p>{ASK}</p><a class="btn btn-red arrow" href="#">Boka bedömning </a></div></div></section>''')

V[4] = ("Röd faktarad", f'''<section class="t4"><div class="wrap"><b>Trygg el</b><ul>{"".join(f"<li><small>{a}</small>{b}</li>" for a, b in FACTS)}</ul><a href="#" class="lnk">Boka bedömning →</a></div></section>''')

V[5] = ("Porträtt i ruta", f'''<section class="t5"><div class="wrap"><div class="box"><img src="../../site/img/portratt.jpg" alt="">
<div><span class="eyebrow">Trygg el</span><h2>{LEAD}</h2><p>{BODY}</p>{CTA}</div></div></div></section>''')

V[6] = ("Gruppförteckning", f'''<section class="t6"><div class="wrap"><div class="head"><span class="eyebrow">Trygg el</span><h2>Det här står vi för, varje gång</h2></div>
<div class="panel">{"".join(f'<div class="fuse"><span class="no">{i + 1:02d}</span><b>{b}</b><small>{a}</small></div>' for i, (a, b) in enumerate(FACTS))}</div>
<p class="t6-note">{ASK} <a href="#">Boka bedömning →</a></p></div></section>''')

V[7] = ("Fyra fakta på linje", f'''<section class="t7"><div class="wrap"><h2>Trygg el</h2><div class="row">{"".join(f"<div><b>{b}</b><small>{a}</small></div>" for a, b in [("Sedan", "2008")] + FACTS[:3])}</div></div></section>''')

V[8] = ("Checklista i kort", f'''<section class="t8"><div class="wrap"><div class="card"><div><span class="eyebrow">Trygg el</span><h2>Riktig elektriker, riktig trygghet</h2><p>{ASK}</p></div>
<ul>{"".join(f'<li class="chk">{b} <span>{a.lower()}</span></li>' for a, b in FACTS)}</ul><a class="btn btn-red arrow" href="#">Boka bedömning </a></div></div></section>''')

V[9] = ("Redaktionell text", f'''<section class="t9"><div class="wrap"><span class="eyebrow">Trygg el</span><h2>{LEAD}</h2>
<div class="cols"><p>I Sverige har elolyckorna blivit färre, mycket tack vare Elsäkerhetsverkets arbete. Men varje år händer det fortfarande olyckor, och de flesta går att undvika.</p><p>{BODY} {ASK}</p></div>
<p class="sign">Bloms El &amp; Data, certifierade elektriker sedan 2008 · {KOLLA}</p></div></section>''')

V[10] = ("Mörk kompakt", f'''<section class="t10"><div class="wrap"><div><h2>Trygg el</h2><p>{LEAD} {ASK}</p><a class="btn btn-white arrow" href="#">Boka bedömning </a></div>
<ul>{"".join(f"<li><small>{a}</small>{b}</li>" for a, b in FACTS)}</ul></div></section>''')

CSS = """
body{margin:0;background:#fff}
section{font-family:var(--font)}
section h2{font-size:30px;line-height:1.2;letter-spacing:-.01em;color:var(--ink);font-weight:600}
section p{color:var(--muted);line-height:1.7}
.kolla{font-size:14px;font-weight:600;color:var(--red);text-decoration:underline;text-underline-offset:3px}
/* 1 */
.t1{padding-block:72px}.t1 .wrap{display:grid;grid-template-columns:1.1fr 1fr;gap:80px;align-items:center}
.t1 .wrap>div{display:flex;flex-direction:column;gap:16px}
.t1 dl{margin:0;border-top:1px solid var(--line)}.t1 dl div{display:flex;justify-content:space-between;padding:16px 0;border-bottom:1px solid var(--line)}
.t1 dt{color:var(--muted);font-size:14px}.t1 dd{margin:0;font-weight:600;color:var(--ink)}
/* 2 */
.t2{padding-block:72px;background:var(--light)}.t2 .wrap{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center}
.t2 .txt{display:flex;flex-direction:column;gap:14px;align-items:flex-start}
.t2 table{width:100%;border-collapse:collapse;background:#fff;font-size:14px;font-variant-numeric:tabular-nums;box-shadow:0 1px 0 var(--line)}
.t2 caption{text-align:left;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-bottom:10px}
.t2 th{text-align:left;font-weight:600;font-size:12px;color:var(--muted);padding:12px 18px;border-bottom:2px solid var(--ink)}
.t2 td{padding:13px 18px;border-bottom:1px solid var(--line);color:var(--ink)}.t2 td:last-child{text-align:right;font-weight:600}
/* 3 */
.t3{padding-block:64px;border-block:1px solid var(--line)}.t3 .wrap{display:grid;grid-template-columns:1.6fr 1fr;gap:80px;align-items:end}
.t3 .big{font-size:38px;line-height:1.2;font-weight:600;color:var(--ink);letter-spacing:-.02em;margin:0}
.t3 .side{display:flex;flex-direction:column;gap:16px;align-items:flex-start}
/* 4 */
.t4{background:var(--red);color:#fff;padding-block:30px}.t4 .wrap{display:flex;align-items:center;gap:40px}
.t4 b{font-size:20px;white-space:nowrap}.t4 ul{list-style:none;margin:0;padding:0;display:flex;flex:1}
.t4 li{flex:1;padding:0 24px;border-left:1px solid rgba(255,255,255,.25);font-weight:600;display:flex;flex-direction:column}
.t4 small{font-weight:400;font-size:12px;opacity:.75}.t4 .lnk{font-weight:600;white-space:nowrap}
/* 5 */
.t5{padding-block:64px}.t5 .box{display:grid;grid-template-columns:260px 1fr;gap:48px;align-items:center;background:var(--light);border-radius:var(--radius);padding:28px}
.t5 img{width:260px;height:260px;object-fit:cover;border-radius:12px;filter:grayscale(1)}
.t5 .box>div{display:flex;flex-direction:column;gap:14px;max-width:620px}
/* 6 */
.t6{padding-block:72px}.t6 .head{margin-bottom:28px}
.t6 .panel{display:grid;grid-template-columns:repeat(4,1fr);border:1.5px solid var(--ink);border-radius:6px;overflow:hidden}
.t6 .fuse{padding:20px 22px;display:flex;flex-direction:column;gap:4px;border-right:1px solid var(--line);background:#fff}
.t6 .fuse:last-child{border-right:0}
.t6 .no{font-size:11px;font-weight:600;letter-spacing:.1em;color:var(--red)}
.t6 .fuse b{font-size:17px;color:var(--ink)}.t6 .fuse small{color:var(--muted);font-size:13px}
.t6 .t6-note{margin-top:18px;font-size:15px}.t6 .t6-note a{color:var(--red);font-weight:600}
/* 7 */
.t7{padding-block:56px}.t7 .wrap{display:grid;grid-template-columns:220px 1fr;gap:40px;align-items:center}
.t7 .row{display:grid;grid-template-columns:repeat(4,auto);justify-content:space-between}.t7 .row div{padding:0 26px;border-left:1px solid var(--line);display:flex;flex-direction:column;gap:2px}
.t7 b{font-size:22px;color:var(--ink);font-weight:600;white-space:nowrap}.t7 small{color:var(--muted);font-size:13px}
/* 8 */
.t8{padding-block:56px;background:var(--light)}.t8 .card{background:#fff;border-radius:var(--radius);padding:36px 40px;display:grid;grid-template-columns:1.2fr 1fr auto;gap:48px;align-items:center}
.t8 .card>div{display:flex;flex-direction:column;gap:10px}.t8 h2{font-size:26px}
.t8 ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}.t8 li span{color:var(--muted);font-weight:400;font-size:13px}
/* 9 */
.t9{padding-block:80px}.t9 .wrap{max-width:calc(980px + 8vw)}.t9 h2{font-size:34px;max-width:22ch;margin:6px 0 24px}
.t9 .cols{display:grid;grid-template-columns:1fr 1fr;gap:48px}.t9 .cols p{margin:0}
.t9 .sign{margin-top:28px;padding-top:18px;border-top:1px solid var(--line);font-size:14px}
/* 10 */
.t10{background:var(--ink);color:#fff;padding-block:56px}.t10 .wrap{display:grid;grid-template-columns:1.2fr 1fr;gap:80px;align-items:center}
.t10 h2{color:#fff}.t10 p{color:rgba(255,255,255,.75);margin:12px 0 22px}
.t10 ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:22px 32px}
.t10 li{display:flex;flex-direction:column;font-weight:600;padding-left:14px;border-left:2px solid var(--red)}.t10 small{font-weight:400;color:rgba(255,255,255,.6);font-size:12px}
"""
for n, (name, html) in V.items():
    (OUT / f"trygg-el-{n}.html").write_text(f"""<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trygg el – förslag {n}: {name}</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="../../site/assets/style.css"><style>{CSS}</style></head><body>{html}</body></html>""", encoding="utf-8")
print("10 förslag")
