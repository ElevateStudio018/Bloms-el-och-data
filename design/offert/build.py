"""Bygger säljmaterialet till Bloms El & Data: info-PDF (med offerten i slutet) och separat offert-PDF.

Kör:  python3 design/offert/build.py   (läser tester.json, skriver info.html och offert.html)
      node design/offert/render.js     (gör PDF:er av HTML-filerna)
"""
import json
from pathlib import Path

OUT = Path(__file__).parent
T = json.loads((OUT / "tester.json").read_text(encoding="utf-8"))

MARK = ('<svg class="mark" viewBox="0 0 1884.3 1353.9" aria-hidden="true"><path d="M0.0 1353.9 L1218.7 0.0 L1218.7 329.1 L479.7 1136.4 '
        'L786.7 1132.4 L1215.5 687.4 L1884.3 1349.9 L1590.1 1349.9 L1218.6 994.7 L865.4 1349.9Z" fill="currentColor"/></svg>')
OLD_C, NEW_C, ONE_C = "#b3aa9c", "#2f6f4a", "#2f6f4a"

OFFER_NO = "2026-1028-BLOMS"
DATE = "28 oktober 2026"
VALID = "10 december 2026"


def nf(x, d=0):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s


# ------------------------------------------------------------------ test-sammanfattning
def seo_summary(rows):
    n = len(rows)
    imgs = sum(r["imgs"] for r in rows)
    alt = sum(r["alt"] for r in rows)
    return {
        "pages": n,
        "ld": sum(1 for r in rows if r["ld"]),
        "faq": sum(1 for r in rows if r["faq"]),
        "canon": sum(1 for r in rows if r["canonical"]),
        "desc": sum(1 for r in rows if 70 <= len(r["desc"]) <= 160 and len(r["title"]) <= 60),
        "og": sum(1 for r in rows if r["og"]),
        "h1": sum(1 for r in rows if r["h1"] == 1),
        "alt": round(alt / imgs * 100) if imgs else 0,
        "words": sum(r["words"] for r in rows),
    }


SO, SN = seo_summary(T["seo"]["old"]), seo_summary(T["seo"]["new"])
P = {p["page"]: p for p in T["perf"]}


# ------------------------------------------------------------------ diagram (SVG)
def hbars(items, unit="", maxv=None, w=640, row=34, label_w=230, color=ONE_C, fmt=None):
    """Liggande staplar, en serie. items = [(etikett, värde)]."""
    maxv = maxv or max(v for _, v in items)
    fmt = fmt or (lambda v: nf(v, 1 if v % 1 else 0) + unit)
    h = row * len(items)
    bw = w - label_w - 70
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img">']
    for i, (lab, v) in enumerate(items):
        y = i * row
        L = max(2, bw * v / maxv)
        out.append(f'<text x="0" y="{y + row / 2 + 4}" class="lab">{lab}</text>')
        out.append(f'<rect x="{label_w}" y="{y + 7}" width="{bw}" height="{row - 14}" rx="4" class="track"/>')
        out.append(f'<rect x="{label_w}" y="{y + 7}" width="{L:.1f}" height="{row - 14}" rx="4" fill="{color}"/>')
        out.append(f'<text x="{label_w + L + 8:.1f}" y="{y + row / 2 + 4}" class="val">{fmt(v)}</text>')
    out.append("</svg>")
    return "".join(out)


def pair_bars(items, w=300, h=170, unit="", fmt=None, better="lower"):
    """Före/efter för ett mått: två staplar med värden direkt på."""
    fmt = fmt or (lambda v: nf(v) + unit)
    (lo, vo), (ln, vn) = items
    m = max(vo, vn) or 1
    base = h - 26
    bw = 74
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img">', f'<line x1="20" x2="{w - 20}" y1="{base}" y2="{base}" class="axis"/>']
    for i, (lab, v, c) in enumerate([(lo, vo, OLD_C), (ln, vn, NEW_C)]):
        x = 50 + i * 120
        bh = max(3, (base - 26) * v / m)
        out.append(f'<path d="M{x},{base} V{base - bh + 4} q0,-4 4,-4 h{bw - 8} q4,0 4,4 V{base} Z" fill="{c}"/>')
        out.append(f'<text x="{x + bw / 2}" y="{base - bh - 8}" class="val mid">{fmt(v)}</text>')
        out.append(f'<text x="{x + bw / 2}" y="{h - 6}" class="lab mid">{lab}</text>')
    out.append("</svg>")
    return "".join(out)


def range_bars(items, w=640, row=46, label_w=170, maxv=None):
    """Spann (min–max) per scenario."""
    maxv = maxv or max(b for _, a, b, _ in items)
    bw = w - label_w - 20
    h = row * len(items) + 24
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img">']
    ticks = [0, 250000, 500000, 750000, 1000000, 1250000]
    for t in ticks:
        if t > maxv:
            break
        x = label_w + bw * t / maxv
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="0" y2="{h - 22}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{h - 6}" class="tick mid">{"0" if not t else nf(t / 1000) + " tkr"}</text>')
    for i, (lab, a, b, note) in enumerate(items):
        y = i * row
        x1, x2 = label_w + bw * a / maxv, label_w + bw * b / maxv
        out.append(f'<text x="0" y="{y + 20}" class="lab b">{lab}</text><text x="0" y="{y + 36}" class="tick">{note}</text>')
        out.append(f'<rect x="{x1:.1f}" y="{y + 12}" width="{x2 - x1:.1f}" height="16" rx="4" fill="{ONE_C}"/>')
        tx = x2 + 8 if x2 < label_w + bw - 150 else x1 - 8
        anchor = "start" if x2 < label_w + bw - 150 else "end"
        out.append(f'<text x="{tx:.1f}" y="{y + 25}" class="val" text-anchor="{anchor}">{nf(a / 1000)}–{nf(b / 1000)} tkr</text>')
    out.append("</svg>")
    return "".join(out)


# ------------------------------------------------------------------ gemensamma bitar
def sheet(body, cls="", foot="BLOMS EL &amp; DATA  |  FÖRSLAG FRÅN ELEVATE STUDIO", num=None):
    f = f'<footer class="pfoot"><span>{foot}</span><span>{num or ""}</span></footer>' if foot else ""
    return f'<section class="page {cls}">{body}{f}</section>'


def head_block(eyebrow, title, lead=""):
    return f'<header class="ph"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{f"<p class=lead>{lead}</p>" if lead else ""}</header>'


def stat(v, txt, src):
    return f'<div class="stat"><b>{v}</b><p>{txt}</p><small>{src}</small></div>'


SIGN = ('<div class="sign"><p>Med vänliga hälsningar</p><p class="script">Isak Mattsson</p>'
        '<p><b>Isak Mattsson</b><br>Elevate Studio<br>info@elevatestudio.nu · elevatestudio.nu</p></div>')

# ------------------------------------------------------------------ offerten (två blad, samma mall som elevatestudio.nu/avtal)
def offer_sheets(page_from=1, total=2):
    top = lambda sub: f'<header class="agr__top">{MARK}<div><p class="agr__brand">ELEVATE STUDIO</p><p class="agr__sub">{sub}</p></div></header>'
    foot = lambda n: f'<footer class="agr__foot"><span>ELEVATE STUDIO&nbsp; | &nbsp;OFFERT</span><span>Sida {n} av {total}</span></footer>'
    s1 = f'''<section class="agr__sheet">{top("WEBBUTVECKLING / OFFERT")}<div class="agr__body">
<div class="agr__meta"><p class="agr__no">OFFERT NR {OFFER_NO}</p><p>Datum: {DATE}&nbsp; | &nbsp;Giltig till: {VALID}</p></div>
<h2>1. Parter</h2>
<p>Producent: Elevate Studio (PJM Projekteffektivitet AB, org.nr 556969-4358)</p>
<p>Producentens företrädare: Isak Mattsson</p>
<p>Beställare: Bloms El &amp; Data AB, org.nr 556754-3656, Blomstergatan 5, 411 04 Göteborg</p>
<p>Beställarens företrädare: Rustan Blom</p>
<h2>2. Uppdragets omfattning (specifikation)</h2>
<p>Utveckling och leverans av en ny, modern och mobilanpassad webbplats för Beställaren på blomsel.se.</p>
<p class="agr__lead">Grundpaket, i uppdraget ingår:</p>
<ul><li>Webbplats med 29 sidor: startsida, en egen sida per tjänst, områdessidor, om oss, vanliga frågor och kontakt, enligt den design som visats.</li>
<li>Adminpanel med inloggning där Beställaren själv ändrar texter, bilder, SEO, kontaktuppgifter, färger och typsnitt och publicerar direkt.</li>
<li>Förfrågningsinkorg: kontaktformulärets förfrågningar samlas i adminpanelen med status, ordervärde och anteckningar, och aviseras via e-post.</li>
<li>AI-assistent i adminpanelen som kan göra ändringar på sajten och skriva texter och kundsvar.</li>
<li>Grundläggande sökmotoroptimering (SEO): titlar och beskrivningar, strukturerad data, sitemap, alt-texter och vidarekoppling från de gamla adresserna.</li>
<li>Enkel AI-optimering (AIO): llms.txt, faktasidor och vanliga frågor som AI-tjänster kan läsa.</li>
<li>Två korrekturvändor före leverans.</li></ul>
<p class="agr__lead">Tillval A: Avancerad SEO och AIO</p>
<ul><li>Sökordsanalys och finjustering av alla sidor, Google-företagsprofil, enhetliga uppgifter i kataloger (Hitta, Eniro, Reco, Bing, Apple), flöde för kundomdömen, Search Console, AI-synlighetstest före och efter samt rapport efter tre månader.</li>
<li>Förutsätter att Beställaren ger åtkomst till Google Företagsprofil och domän samt själv ber kunder om omdömen. Resultatet beror till stor del på Beställarens medverkan.</li></ul>
<p class="agr__lead">Tillval B: Löpande underhåll</p>
<ul><li>Uppdateringar av webbplatsen, nya sektioner och omfattande ombyggnationer av webbplatsen.</li></ul>
<h2>3. Driftmiljö</h2>
<p>Beställaren äger sin domän och sitt webbhotell, och betalar webbhotellets avgifter. Elevate Studio driftsätter webbplatsen där. Adminpanelen och inkorgen kräver PHP, som ingår hos de flesta webbhotell. AI-assistenten använder en API-nyckel från Anthropic, och användningen debiteras av Anthropic.</p>
<h2>4. Leverans</h2>
<p>Webbplatsen driftsätts efter godkännande och när åtkomst till webbhotellet finns, så att bytet hinner ske innan bindningstiden för det nuvarande abonnemanget löper ut 7 december 2026.</p>
</div>{foot(page_from)}</section>'''
    s2 = f'''<section class="agr__sheet">{top("OFFERT / VILLKOR OCH GODKÄNNANDE")}<div class="agr__body">
<h2>5. Fast pris och betalning</h2>
<table><thead><tr><th>Post</th><th>Pris (exkl. moms)</th></tr></thead><tbody>
<tr><td>Grundpaket: webbplats med adminpanel, förfrågningsinkorg, AI-assistent, grundläggande SEO och enkel AIO – fast pris</td><td>3 000 kr</td></tr>
<tr><td>Tillval A: Avancerad SEO och AIO</td><td>+ 4 000 kr</td></tr>
<tr><td>Tillval B: Löpande underhåll</td><td>99 kr/mån</td></tr>
</tbody><tfoot><tr><td>Totalt grundpaket med Tillval A</td><td>7 000 kr</td></tr></tfoot></table>
<p>Grundpaketet och Tillval A är engångsbelopp. Tillval B gäller uppdateringar av webbplatsen, nya sektioner och omfattande ombyggnationer av webbplatsen, och löper per månad tills det sägs upp.</p>
<p>Fast pris och tillval faktureras vid driftsättning. Löpande underhåll faktureras från och med driftsättningen. Betalningsvillkor: 30 dagar. Samtliga priser anges exklusive moms.</p>
<h2>6. Godkännande av offert</h2>
<p>Beställaren kan acceptera denna offert genom att svara på mejlet med följande text och stryka det som inte ska ingå:</p>
<blockquote>Jag godkänner offert nr {OFFER_NO} och beställer grundpaketet / grundpaketet med Tillval A, med / utan Tillval B, enligt offertens villkor.</blockquote>
<p>Genom godkännandet accepterar Beställaren uppdragets omfattning, priser, betalningsvillkor och övriga villkor i denna offert.</p>
<div class="agr__sig"><div><p class="script">Isak Mattsson</p><p>Isak Mattsson, Elevate Studio<br>Uppsala, {DATE}</p></div><div><p class="line"></p><p>Rustan Blom, Bloms El &amp; Data AB<br>Ort och datum</p></div></div>
</div>{foot(page_from + 1)}</section>'''
    return s1 + s2


# ------------------------------------------------------------------ info-PDF
def info():
    o, n = P["start"]["old"], P["start"]["new"]
    pages = []

    # 1. omslag
    pages.append(f'''<section class="page cover">
<div class="cv-top">{MARK}<span>ELEVATE STUDIO</span></div>
<div class="cv-main"><p class="eyebrow light">Förslag till Bloms El &amp; Data AB</p>
<h1>En ny hemsida som syns på Google och i AI-svar, och som får fler att höra av sig.</h1>
<p class="lead">29 sidor, egen adminpanel, förfrågningsinkorg och AI-assistent. Byggd för sökmotorer och AI från grunden.</p>
<div class="cv-price"><b>3 000 kr</b><span>allt ovan, fast pris exkl. moms</span></div></div>
<div class="cv-shots"><img class="d" src="img/ny-desktop.png" alt=""><img class="m" src="img/ny-mobil.png" alt=""></div>
<div class="cv-foot"><div><small>Till</small>Rustan Blom, Bloms El &amp; Data AB</div><div><small>Från</small>Isak Mattsson, Elevate Studio</div><div><small>Datum</small>{DATE}</div><div><small>Giltigt till</small>{VALID}</div></div>
</section>''')

    # 2. sammanfattning
    pages.append(sheet(head_block("Sammanfattning", "Det här är förslaget på en sida")
        + f'''<div class="cols2"><div>
<h3>Vad vi har sett</h3>
<ul class="chk neg"><li>Sidorna om elbilsladdare och smart teknik är dolda för Google (noindex) och kan inte hittas i sökresultaten.</li>
<li>blomsel.se syntes inte i någon av fem typiska kundsökningar vi testade, inte ens på företagsnamnet.</li>
<li>Startsidan laddar {nf(o["kb"] / 1024, 1)} MB och {o["reqs"]} filer på mobilen. Det tar {nf(o["lcp"] / 1000, 1)} sekunder innan huvudinnehållet syns och {nf(o["load"] / 1000, 1)} sekunder innan sidan är färdigladdad.</li>
<li>Sajten har {SO["pages"]} sidor och saknar egna sidor för de flesta tjänsterna. Google rankar lokala företag högre när varje tjänst har en egen sida.</li>
<li>Filen som AI-tjänster läser presenterar företaget som "bloms2".</li></ul>
<h3>Vad ni får</h3>
<ul class="chk"><li>Ny webbplats med {SN["pages"]} sidor, en per tjänst och område, i Bloms färger och typsnitt.</li>
<li>Nya startsidan i samma test: huvudinnehållet syns efter {nf(n["lcp"] / 1000, 1)} sekunder och sidan är färdigladdad efter {nf(n["load"] / 1000, 1)} sekunder. Den väger {nf(n["kb"] / 1024, 1)} MB.</li>
<li>Adminpanel där ni själva ändrar allt och publicerar direkt.</li>
<li>Inkorg för förfrågningar och en AI som kan fixa ändringar åt er.</li>
<li>SEO och AI-optimering inbyggt från start.</li></ul>
</div><div class="pricebox">
<p class="eyebrow">Pris, exkl. moms</p>
<div class="pb-row"><b>3 000 kr</b><span>Ny webbplats, adminpanel, inkorg, AI-assistent, grundläggande SEO och enkel AIO</span></div>
<div class="pb-row"><b>+4 000 kr</b><span>Tillval: avancerad SEO och AIO (7 000 kr totalt)</span></div>
<div class="pb-row"><b>99 kr/mån</b><span>Tillval: löpande underhåll, nya sektioner och ombyggnationer</span></div>
<p class="pb-note">Ni behåller domänen och webbhotellet. Vi driftsätter före 7 december, när bindningstiden för nuvarande abonnemang går ut. Erbjudandet gäller till {VALID}.</p>
<p class="pb-big">En enda extra laddbox- eller elcentralsorder betalar hela paketet, ofta flera gånger om.</p>
<p class="pb-note"><b>Er del:</b> resultatet avgörs till stor del av att ni ber kunder om omdömen och ger oss åtkomst till Google-profilen. Se sidan "Er del av jobbet".</p>
</div></div>
<h3>Så går bytet till</h3><ol class="steps"><li><b>Ni godkänner offerten</b>senast {VALID}, genom att svara på mejlet</li><li><b>Vi får åtkomst</b>till webbhotellet och domänen</li><li><b>Vi driftsätter</b>och kopplar om. Gamla adresser vidarekopplas så att Google-länkar fungerar</li><li><b>Ni säger upp Wix</b>innan bindningstiden går ut 7 december</li></ol>''', num=2))

    # 3. så letar kunderna
    pages.append(sheet(head_block("Hur kunderna letar 2026", "Kunderna frågar Google, och allt oftare en AI",
        "Den som behöver en elektriker googlar, läser omdömen och frågar i allt högre grad ChatGPT eller Googles AI-översikt. Siffrorna nedan är från de senaste mätningarna.")
        + '<div class="stats">'
        + stat("62 %", "av svenska internetanvändare använder AI-tjänster. 52 % använder ChatGPT.", "Internetstiftelsen, Svenskarna och internet 2026")
        + stat("71 %", "använder Googles AI-översikter, alltså de AI-svar som visas överst i Google.", "Internetstiftelsen, Svenskarna och internet 2026")
        + stat("97 %", "läser omdömen innan de väljer ett lokalt företag. 68 % väljer bara företag med minst 4 stjärnor.", "BrightLocal, Local Consumer Review Survey 2026")
        + stat("57 %", "av trafiken på svenska webbplatser kommer från mobilen.", "StatCounter, september 2026")
        + '</div><div class="cols2"><div><h3>Bara toppen får klicken</h3><p class="cap">Andel av klicken i Googles sökresultat</p>'
        + hbars([("Plats 1", 27.6), ("Plats 1–3 tillsammans", 54.4), ("Hela sida 2", 0.63)], unit=" %", w=420, label_w=150, maxv=60)
        + '<p class="src">Backlinko, 4 miljoner sökresultat (uppdaterad 2025)</p></div><div><h3>AI-svaret blir nya förstaplatsen</h3>'
        '<p>När Google visar en AI-översikt klickar folk på ett vanligt resultat i 8 % av fallen, mot 15 % utan. Företag som nämns i AI-svaret får 35 % fler klick.</p>'
        '<p>Det betyder att det inte räcker att finnas med. Man måste vara det svar Google och AI-tjänsterna väljer att visa.</p>'
        '<p class="src">Pew Research Center 2025 · Seer Interactive 2025</p></div></div>'
        '<div class="callout"><b>Google om lokal ranking:</b> resultaten bygger på relevans, avstånd och hur framträdande företaget är. "Fler omdömen och positiva betyg kan hjälpa företagets lokala ranking." <span class="src">Google Företagsprofil, hjälpcenter</span></div>', num=3))

    # 4. läget i dag: synlighet och SEO
    rows = [("elektriker Göteborg", "Reco, Eniro, jobbannonser"), ("installera laddbox villa Göteborg", "Göteborg Laddbox (258 omdömen), El-Fast (435 omdömen)"),
            ("byta elcentral Göteborg pris", "Byggahus forum, Offerta"), ("elektriker Mölndal", "Trustpilot, Reco, Fässbergs El"), ("Bloms El &amp; Data Göteborg", "Andra företag med liknande namn")]
    tbl = "".join(f"<tr><td>{q}</td><td class='no'>Nej</td><td>{w}</td></tr>" for q, w in rows)
    of = lambda k: f'{SO[k]} av {SO["pages"]}'
    nw = lambda k: f'{SN[k]} av {SN["pages"]}'
    cmp_rows = [("Antal sidor", SO["pages"], SN["pages"]), ("Egna sidor per tjänst", 3, 15), ("Egna sidor per område", 6, 7),
                ("Sidor med strukturerad data (schema)", of("ld"), nw("ld")), ("Sidor med vanliga frågor som Google kan läsa", of("faq"), nw("faq")),
                ("Rätt längd på titel och beskrivning", of("desc"), nw("desc")), ("Bilder med alt-text", f'{SO["alt"]} %', f'{SN["alt"]} %'),
                ("Ord text totalt (det Google och AI läser)", nf(SO["words"]), nf(SN["words"])), ("llms.txt för AI-tjänster", '"bloms2", 1 länk', "Bloms El &amp; Data, alla sidor")]
    ctbl = "".join(f"<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>" for a, b, c in cmp_rows)
    pages.append(sheet(head_block("Test 1 och 2: synlighet och SEO", "Så syns blomsel.se i dag",
        "Vi testade fem sökningar som kunder gör och gick igenom alla sidor på nuvarande och nya sajten med samma verktyg.")
        + f'''<h3>Syns blomsel.se när kunden söker?</h3><table class="t"><thead><tr><th>Sökning</th><th>Syns</th><th>Vad som syns i stället</th></tr></thead><tbody>{tbl}</tbody></table>
<p class="src">Test 28 oktober 2026 i ett webbsökindex (inte Google.se, så det är en indikation). Sajterna som syns har gemensamt många omdömen och en egen sida per tjänst.</p>
<h3>Teknisk SEO, sida för sida</h3><table class="t cmp"><thead><tr><th>Mått</th><th>Nuvarande</th><th>Nya sajten</th></tr></thead><tbody>{ctbl}</tbody></table>
<p class="src">Uppmätt med Chromium på alla {SO["pages"]} sidor på blomsel.se och alla {SN["pages"]} sidor på nya sajten, 28 oktober 2026. Wix sköter en del teknisk SEO bra, till exempel kanoniska adresser. Den stora skillnaden är innehållet: dubbelt så mycket text, en sida per tjänst och vanliga frågor.</p>''', num=4))

    # 5. hastighet
    lab = ("Nuvarande", "Nya")
    names = {"start": "Startsida", "elbilsladdare": "Elbilsladdare", "kontakt": "Kontakt"}
    sec = lambda v: nf(v / 1000, 1) + " s"
    perf_rows = "".join(
        f'<tr><td>{names[k]}</td><td>{sec(P[k]["old"]["lcp"])}</td><td><b>{sec(P[k]["new"]["lcp"])}</b></td>'
        f'<td>{sec(P[k]["old"]["load"])}</td><td><b>{sec(P[k]["new"]["load"])}</b></td><td>{nf(P[k]["old"]["kb"])} kB</td><td><b>{nf(P[k]["new"]["kb"])} kB</b></td></tr>'
        for k in names)
    pages.append(sheet(head_block("Test 3: hastighet på mobilen", "Nya sajten laddar mycket snabbare än i dag",
        "Vi mätte tre sidor på nuvarande och nya sajten i samma test: en vanlig mobil med långsam 4G-uppkoppling, tre mätningar per sida. Diagrammen visar startsidan.")
        + '<div class="cols3">'
        + f'<div><h3>Laddtid för hela sidan</h3>{pair_bars([(lab[0], o["load"] / 1000), (lab[1], n["load"] / 1000)], fmt=lambda v: nf(v, 1) + " s")}</div>'
        + f'<div><h3>Data som laddas</h3>{pair_bars([(lab[0], o["kb"] / 1024), (lab[1], n["kb"] / 1024)], fmt=lambda v: nf(v, 1) + " MB")}</div>'
        + f'<div><h3>Tid då mobilen inte svarar</h3>{pair_bars([(lab[0], o["tbt"] / 1000), (lab[1], n["tbt"] / 1000)], fmt=lambda v: nf(v, 1) + " s")}</div></div>'
        + '<div class="legend"><span><i style="background:' + OLD_C + '"></i>Nuvarande blomsel.se</span><span><i style="background:' + NEW_C + '"></i>Nya sajten</span></div>'
        + f'<table class="t"><thead><tr><th>Sida</th><th>Innehållet syns, nu</th><th>Syns, ny</th><th>Laddad, nu</th><th>Laddad, ny</th><th>Data, nu</th><th>Data, ny</th></tr></thead><tbody>{perf_rows}</tbody></table>'
        + f'<p class="small">Ärligt sagt: på undersidorna visar Wix första texten något snabbare ({sec(P["elbilsladdare"]["old"]["lcp"])} mot {sec(P["elbilsladdare"]["new"]["lcp"])}), men sidan laddar sedan vidare i över 10 sekunder och mobilen svarar trögt under tiden. På startsidan syns innehållet {nf(o["lcp"] / n["lcp"], 0)} gånger snabbare på nya sajten.</p>'
        + f'<p class="src">{T["method"]}. Nuvarande sajt mätt live på blomsel.se. Nya sajten mätt på en testserver med komprimering och cache som webbhotellet, med samma nätverksbegränsning. "Innehållet syns" är Largest Contentful Paint, Googles mått, där under 2,5 s räknas som bra. "Mobilen svarar inte" är Total Blocking Time.</p>', num=5))

    # 6. Googles egna testverktyg
    L = T["lighthouse"]
    def avg(side, k): return round(sum(r[k] for r in L[side]) / len(L[side]))
    cats = [("Prestanda", "perf"), ("Tillgänglighet", "a11y"), ("Bästa praxis", "bp"), ("SEO", "seo")]
    score_rows = "".join(f'<tr><td>{lab}</td><td>{avg("old", k)}</td><td><b>{avg("new", k)}</b></td></tr>' for lab, k in cats)
    bars = "".join(f'<div><h3>{lab}</h3>{pair_bars([("Nuvarande", avg("old", k)), ("Nya", avg("new", k))], w=300, h=150)}</div>' for lab, k in cats)
    pages.append(sheet(head_block("Test 4: Googles egna testverktyg", "Bättre betyg i Googles test, och alla sidor kan indexeras",
        f"Vi körde Lighthouse, samma test som Googles PageSpeed Insights bygger på, på {len(L['old'])} sidor på nuvarande sajt och alla {len(L['new'])} sidor på nya sajten. Strukturerad data kontrollerades med validator.schema.org.")
        + f'<div class="cols4">{bars}</div>'
        + '<div class="legend"><span><i style="background:' + OLD_C + '"></i>Nuvarande blomsel.se</span><span><i style="background:' + NEW_C + '"></i>Nya sajten</span><span>Medelbetyg 0–100, högre är bättre</span></div>'
        + f'''<div class="cols2"><div><h3>Fynd: två sidor är dolda för Google i dag</h3>
<p>Sidorna <b>Elbilsladdare</b> och <b>Smart teknik</b> på nuvarande blomsel.se har en instruktion till Google om att inte visas i sökresultaten (noindex) och saknas i sajtens sitemap. Laddboxar är en av de mest efterfrågade tjänsterna, men sidan kan i dag inte hittas på Google.</p>
<p>På nya sajten kan alla {len(L['new'])} sidor indexeras och alla finns i sitemapen.</p></div>
<div><h3>Strukturerad data</h3><table class="t"><thead><tr><th>Kontroll</th><th>Nuvarande</th><th>Nya</th></tr></thead><tbody>
<tr><td>Sidor med företagsdata (Electrician)</td><td>{SO["ld"]} av {SO["pages"]}</td><td><b>{SN["ld"]} av {SN["pages"]}</b></td></tr>
<tr><td>Sidor med tjänstebeskrivning (Service)</td><td>0</td><td><b>{T["schema"]["service"]}</b></td></tr>
<tr><td>Sidor med vanliga frågor (FAQPage)</td><td>0</td><td><b>{T["schema"]["faq"]}</b></td></tr>
<tr><td>Fel i validator.schema.org</td><td>–</td><td><b>0</b></td></tr></tbody></table></div></div>'''
        + '<p class="src">Lighthouse 13.5, mobil, samma inställningar som PageSpeed Insights. Nuvarande sajt testad live på blomsel.se, nya sajten på en testserver med komprimering och cache som webbhotellet. Google visar inte längre vanliga frågor som extra rader i sökresultaten för de flesta företag, men frågorna hjälper Google och AI-tjänster att förstå vad ni gör.</p>', num=6))

    # 7. vad ni får
    pages.append(sheet(head_block("Det här ingår för 3 000 kr", "En komplett hemsida, inte bara en mall")
        + '''<div class="feat"><img src="img/ny-desktop.png" alt=""><div><h3>Ny webbplats med 29 sidor</h3><p>Startsida, en egen sida för varje tjänst (laddbox, solceller, elcentral, belysning, datanät, kraft, golvvärme, kök och badrum, batterilager med flera), sidor för varje område från Mölndal till Borås, om oss, vanliga frågor och kontakt. Samma röda färg och Poppins som i dag, i en modernare form.</p></div></div>
<div class="feat"><img src="img/admin-inkorg.png" alt=""><div><h3>Förfrågningsinkorg</h3><p>Allt som kommer in via kontaktformuläret hamnar i adminpanelen och mejlas till er. Markera som kontaktad, offert skickad, vunnen eller förlorad, skriv anteckningar och se ordervärdet. Ring eller svara med ett klick.</p></div></div>
<div class="feat"><img src="img/admin-ai.png" alt=""><div><h3>AI som fixar saker</h3><p>Skriv "byt telefonnummer på hela sajten" eller "gör texten om laddboxar mer säljande". AI:n läser sidorna, gör ändringen och visar vad den gjort. Ni granskar och publicerar med ett klick, eller ångrar.</p></div></div>
<div class="feat"><img src="img/admin-publicera.png" alt=""><div><h3>Adminpanel som sparar direkt</h3><p>Klicka på en text på sajten och skriv. Byt bilder, SEO-texter, telefonnummer, färger och typsnitt. Publicera direkt, utan filer att ladda upp. Alla tidigare versioner sparas och kan återställas.</p></div></div>''', num=7))

    # 8. paket
    yes, no = '<td class="y">✓</td>', '<td class="n">–</td>'
    feat_rows = [("Ny webbplats, 29 sidor, mobilanpassad", 1, 1), ("Adminpanel, förfrågningsinkorg och AI-assistent", 1, 1),
                 ("Titlar, beskrivningar, sitemap och alt-texter", 1, 1), ("Strukturerad data: företag, tjänster, vanliga frågor", 1, 1),
                 ("Vidarekoppling från gamla adresser, så att Google-länkar fungerar", 1, 1), ("llms.txt och faktasidor för AI-tjänster", 1, 1),
                 ("Sökordsanalys och finjustering av varje sida", 0, 1), ("Google Företagsprofil: kategori, tjänster, bilder och områden", 0, 1),
                 ("Samma uppgifter i Hitta, Eniro, Reco, Bing och Apple Kartor", 0, 1), ("Enkelt flöde för att be kunder om omdömen", 0, 1),
                 ("Google Search Console och Bing Webmaster", 0, 1), ("AI-synlighetstest före och efter, rapport efter tre månader", 0, 1)]
    ftbl = "".join(f"<tr><td>{a}</td>{yes if b else no}{yes if c else no}</tr>" for a, b, c in feat_rows)
    pages.append(sheet(head_block("Paketen", "Välj nivå",
        "Grundpaketet ger en sajt som är tekniskt rätt byggd för Google och AI. Det avancerade paketet gör jobbet utanför sajten som avgör den lokala rankingen.")
        + f'''<table class="t pk"><thead><tr><th></th><th>Grund<br><b>3 000 kr</b></th><th>Avancerad<br><b>7 000 kr</b></th></tr></thead><tbody>{ftbl}</tbody></table>
<div class="cols2"><div class="box"><h3>Löpande underhåll, 99 kr/mån</h3><p>Uppdateringar av hemsidan, nya sektioner och omfattande ombyggnationer när ni behöver dem. Tillval till båda paketen.</p></div>
<div class="box"><h3>Jämfört med marknaden</h3><p>Grundläggande SEO kostar normalt 3 000–5 000 kr i månaden och löpande optimering 5 000–15 000 kr i månaden. Det avancerade paketet är en engångskostnad på 4 000 kr.</p><p class="src">Offerta, Vad kostar sökmotoroptimering, 2025</p></div></div>
<p class="small">Alla priser exklusive moms.</p>''', num=8))

    # 9. är det värt det
    sc = [("Försiktigt", 60000, 180000, "+1–2 förfrågningar/mån"), ("Medel", 160000, 540000, "+3–6 förfrågningar/mån"), ("Bra", 430000, 1350000, "+8–15 förfrågningar/mån")]
    pages.append(sheet(head_block("Ärligt svar", "Är avancerat värt 4 000 kr?",
        "Ja, för ett lokalt elföretag är det de här åtgärderna som påverkar rankingen mest, och priset motsvarar ungefär en månads billigaste SEO-abonnemang. Men det finns saker ingen kan lova.")
        + '''<div class="cols2"><div><h3>Det som påverkar lokal ranking mest</h3><ol class="rank"><li><b>Google Företagsprofil</b>rätt kategori, komplett, bilder</li><li><b>Kundomdömen</b>antal, hur nya de är och att ni svarar</li><li><b>En sida per tjänst och område</b>den viktigaste faktorn på själva sajten</li><li><b>Samma uppgifter i alla kataloger</b>namn, adress, telefon</li><li><b>Snabb mobilsajt</b>finns redan i grundpaketet</li></ol><p class="src">Google Företagsprofil hjälpcenter · Whitespark, Local Search Ranking Factors 2026</p></div>
<div><h3>Det vi inte lovar</h3><ul class="chk neg"><li>En viss placering. Ingen kan garantera plats 1 hos Google.</li><li>Ett visst antal förfrågningar.</li><li>Att ChatGPT eller Google nämner er. Det går att påverka men inte styra.</li><li>Resultat utan er medverkan. Hur mycket det ger avgörs till stor del av er, se nästa sida.</li></ul>
<h3>När det märks</h3><p>Google Företagsprofil och omdömen brukar ge effekt inom några veckor. Placeringen i vanliga sökresultat tar normalt 3–6 månader.</p></div></div>
<h3>Räkneexempel: vad fler förfrågningar kan vara värda per år</h3><p class="cap">Extra omsättning per år med 30–50 % av förfrågningarna till order och ett snittjobb på 15 000 kr</p>'''
        + range_bars(sc, maxv=1400000)
        + '''<p class="src">Exempel, inte prognos. Omsättning, inte vinst. Effekten kommer från nya sajten och SEO tillsammans. Jobbvärden: laddbox 10 000–20 000 kr, byte av elcentral 8 000–20 000 kr (Offerta 2026).</p>
<div class="callout big"><b>En order räcker.</b> En enda extra laddbox eller elcentral är värd 10 000–20 000 kr, alltså 2,5–5 gånger uppgraderingen och 1,4–2,9 gånger hela paketet på 7 000 kr.</div>''', num=9))

    # 10. så bidrar ni
    pages.append(sheet(head_block("Er del av jobbet", "Resultatet avgörs till stor del av er",
        "Vi bygger sajten och gör den tekniska SEO:n. Det gör att ni kan synas. Hur mycket ni syns, och hur många som väljer er, avgörs av saker bara ni kan göra. Konkurrenterna som syns i dag har 258 och 435 kundomdömen.")
        + '''<div class="cols2"><div class="box"><h3>Det gör vi</h3><ul class="chk">
<li>Bygger och driftsätter sajten med en sida per tjänst och ort.</li>
<li>Teknisk SEO, strukturerad data och AI-optimering.</li>
<li>Sätter upp och optimerar Google Företagsprofil (avancerat paket).</li>
<li>Lägger in samma uppgifter i Hitta, Eniro, Reco, Bing och Apple Kartor (avancerat paket).</li>
<li>Kopplar Search Console, mäter och rapporterar efter tre månader (avancerat paket).</li>
<li>Ger er färdig SMS-text och QR-kod för att be om omdömen.</li></ul></div>
<div class="box mine"><h3>Det gör ni</h3><ol class="rank">
<li><b>Ger oss åtkomst</b>till Google Företagsprofil och domänen, så att vi kan sätta upp och verifiera allt.</li>
<li><b>Ber varje nöjd kund om ett omdöme</b>med ett SMS direkt efter jobbet. Det här väger tyngst av allt.</li>
<li><b>Svarar på omdömena</b>både bra och dåliga. Google räknar med det och kunderna läser svaren.</li>
<li><b>Svarar snabbt på förfrågningar</b>helst samma dag. Den som svarar först får ofta jobbet.</li>
<li><b>Skickar bilder från avslutade jobb</b>med några rader om vad som gjordes och var. Ett i månaden räcker för att bygga referenser som Google och AI-tjänster värderar.</li>
<li><b>Håller uppgifterna lika överallt</b>samma namn, adress och telefon i alla kanaler.</li></ol></div></div>
<div class="callout big"><b>Tidsåtgång:</b> uppskattningsvis 15–30 minuter i veckan, mest att skicka SMS efter avslutade jobb och svara på omdömen. Med löpande underhåll lägger vi in referensjobben åt er.</div>
<p class="small">Utan omdömen och åtkomst till Google Företagsprofil blir effekten av SEO-arbetet betydligt mindre, oavsett paket.</p>''', num=10))

    # 11–12. offerten
    pages.append(f'<div class="offer">{offer_sheets(1, 2)}</div>')

    # 13. källor och signatur
    src = [("Internetstiftelsen, Svenskarna och internet 2026: AI", "svenskarnaochinternet.se/rapporter/svenskarna-och-internet-2026"),
           ("BrightLocal, Local Consumer Review Survey 2026", "brightlocal.com/research/local-consumer-review-survey"),
           ("StatCounter, Desktop vs Mobile vs Tablet, Sverige, september 2026", "gs.statcounter.com/platform-market-share/desktop-mobile-tablet/sweden"),
           ("Backlinko, Google CTR stats", "backlinko.com/google-ctr-stats"),
           ("Pew Research Center, 22 juli 2025: klick när AI-sammanfattning visas", "pewresearch.org"),
           ("Seer Interactive, AIO impact on Google CTR, november 2025", "seerinteractive.com/insights"),
           ("Google Företagsprofil hjälpcenter: lokal ranking", "support.google.com/business/answer/7091"),
           ("Whitespark, Local Search Ranking Factors 2026", "whitespark.ca/local-search-ranking-factors"),
           ("Offerta, Vad kostar sökmotoroptimering (2025)", "offerta.se/guider/ovrigt/vad-kostar-sokmotoroptimering"),
           ("Offerta, Vad kostar det att installera en laddbox (2026)", "offerta.se"),
           ("Offerta, Byta el i ett gammalt hus (2026)", "offerta.se"),
           ("Google Lighthouse 13.5, samma motor som PageSpeed Insights", "developer.chrome.com/docs/lighthouse"),
           ("validator.schema.org, validering av strukturerad data", "validator.schema.org"),
           ("Skatteverket, skattereduktion för grön teknik", "skatteverket.se"),
           ("Egna tester av blomsel.se och nya sajten, 28–29 oktober 2026", "Mätdata finns hos Elevate Studio")]
    li = "".join(f"<li>{a}<small>{b}</small></li>" for a, b in src)
    pages.append(sheet(head_block("Källor", "Varifrån siffrorna kommer") + f'<ol class="sources">{li}</ol>'
        + '<p class="small">Där källorna är amerikanska har vi angett det i underlaget. Svenska siffror är från Internetstiftelsen och StatCounter.</p>'
        + '<div class="end"><p>Tack för att ni tar er tid. Hör av er om något är oklart, så går vi igenom förslaget tillsammans.</p>' + SIGN + '</div>', num=13))
    return pages


CSS = (OUT / "style.css").read_text(encoding="utf-8")


def doc(title, body):
    return f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Hanken+Grotesk:wght@400;500;600;700&family=Mrs+Saint+Delafield&display=swap">
<style>{CSS}</style></head><body>{body}</body></html>'''


(OUT / "info.html").write_text(doc("Bloms El & Data – förslag från Elevate Studio", "".join(info())), encoding="utf-8")
(OUT / "offert.html").write_text(doc(f"Offert {OFFER_NO} – Elevate Studio", f'<div class="offer">{offer_sheets(1, 2)}</div>'), encoding="utf-8")
print("info.html och offert.html skrivna")
