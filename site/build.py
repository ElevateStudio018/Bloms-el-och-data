"""Bygger blomsel.se i stil med heroförslag 15.

Kör:  python3 site/build.py
Skriver en statisk HTML-fil per sida till site/ (samma URL-namn som originalet, med .html).
"""
from html import escape
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from pages_extra import PAGES as EXTRA, STEPS_STANDARD

OUT = Path(__file__).parent
PHONE = "0705-15 02 11"
TEL = "tel:0705150211"
MAIL = "info@blomsel.se"

NAV = [
    ("index.html", "Hem"),
    ("tjanster.html", "Tjänster"),
    ("smart-teknik.html", "Smart Teknik"),
    ("kontakt.html", "Kontakt"),
    ("skattereduktion.html", "Rot"),
    ("solceller.html", "Solceller"),
    ("elbilsladdare.html", "Elbilsladdare"),
]
AREAS = [
    ("elektriker-hisingen.html", "Hisingen"),
    ("elektriker-i-partille.html", "Partille"),
    ("elektriker-molndal.html", "Mölndal"),
    ("elektriker-kungalv.html", "Kungälv"),
    ("elektriker-vastra-frolunda.html", "Västra Frölunda"),
    ("elektriker-kungsbacka.html", "Kungsbacka"),
]

ICON = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "form": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}


def e(s):
    return escape(s, quote=False)


def ps(*paras):
    return "".join(f"<p>{e(x)}</p>" for x in paras)


# ---------------------------------------------------------------- byggblock
def btns(call=True, contact=True, ghost=True, extra=""):
    out = []
    if call:
        out.append(f'<a class="btn btn-red" href="{TEL}">Ring oss</a>')
    if contact:
        cls = "btn-ghost" if ghost else "btn-line"
        out.append(f'<a class="btn {cls} arrow" href="kontakt.html">Kontakta oss </a>')
    return f'<div class="btns">{"".join(out)}{extra}</div>'


def img_card(img, title, href, alt=""):
    return (f'<a class="card" href="{href}"><div class="img"><img src="img/{img}" alt="{e(alt)}" loading="lazy"></div>'
            f'<div class="row">{e(title)}<span aria-hidden="true">→</span></div></a>')


def stat_card(num, title, href):
    return f'<a class="card stat" href="{href}"><div class="num">{e(num)}</div><div class="row">{e(title)}<span aria-hidden="true">→</span></div></a>'


def icon_card(icon, title, small, href):
    return (f'<a class="card icon" href="{href}"><div class="ic">{ICON[icon]}</div>'
            f'<div class="row">{e(title)}<small>{e(small)}</small></div></a>')


HOME_CARDS = [
    img_card("dokumentation.jpg", "Elservice", "elservice-felsokning.html", "Elektriker mäter i ett elskåp"),
    img_card("laddbox.jpg", "Elbilsladdare", "elbilsladdare.html", "Elbil som laddar vid en laddbox"),
    img_card("solceller.jpg", "Solceller", "solceller.html", "Montör installerar solpaneler"),
    img_card("smart-hem.jpg", "Smart Teknik", "smart-teknik.html", "Smart hem styrs från mobilen"),
]


def hero(img, h1, lead, cards=None, eyebrow=None, buttons=None, pos="center", extra=""):
    cls = "hero" if cards else "hero no-cards"
    eb = f'<span class="eyebrow">{e(eyebrow)}</span>' if eyebrow else ""
    b = btns() if buttons is None else buttons
    lead_html = f'<p class="lead">{e(lead)}</p>' if lead else ""
    cards_html = f'<div class="hero-cards">{"".join(cards)}</div>' if cards else ""
    return (f'<section class="{cls}"><div class="hero-bg"><img src="img/{img}" alt="" style="object-position:{pos}" fetchpriority="high"></div>'
            f'<div class="wrap"><div class="hero-text">{eb}<h1>{e(h1)}</h1>{lead_html}{b}{extra}</div>{cards_html}</div></section>')


def split(img, inner, rev=False, bg="", alt="", media_cls="", badge=""):
    return (f'<section class="sec {bg}"><div class="wrap split{" rev" if rev else ""}">'
            f'<div class="media {media_cls}"><img src="img/{img}" alt="{e(alt)}" loading="lazy">{badge}</div>'
            f'<div class="prose">{inner}</div></div></section>')


def head(eyebrow, title, tag="h2"):
    eb = f'<span class="eyebrow">{e(eyebrow)}</span>' if eyebrow else ""
    return f'{eb}<{tag} class="h2">{e(title)}</{tag}>'


USPS = ["ABL / BB1-behörighet", "Registrerad hos Elsäkerhetsverket", "Garanti på alla arbeten", "CE-märkt material"]


def usp_section(title):
    imgs = [("kabel.jpg", "Montör bär en kabelrulle"), ("servicebil-liseberg.jpg", "Servicebil vid Liseberg"),
            ("servicebil-gang.jpg", "Montör går mot servicebilen"), ("gata-servicebil.jpg", "Montörer vid servicebilen på stan")]
    cards = "".join(
        f'<div class="card"><div class="img"><img src="img/{i}" alt="{e(a)}" loading="lazy"></div><div class="row">{e(t)}</div></div>'
        for (i, a), t in zip(imgs, USPS))
    jump = ('<ul class="pills" aria-label="Hoppa till">'
            '<li><a href="#hur-vi-ser">Vår idé</a></li><li><a href="#trygg-el">El och säkerhet</a></li><li><a href="#tjanster">Tjänster</a></li></ul>')
    return (f'<section class="sec"><div class="wrap"><div class="sec-head"><div class="prose">{head("Bloms El & Data", title)}</div>{jump}</div>'
            f'<div class="grid g4">{cards}</div></div></section>')


SERVICES9 = [
    ("kok.jpg", "Kök & Badrum", "kok-och-badrum.html"),
    ("kabel.jpg", "Nybyggnation", "nybyggnation-renovering.html"),
    ("servicebil-liseberg.jpg", "Elservice", "elservice-felsokning.html"),
    ("kraft.jpg", "Kraft", "kraft.html"),
    ("datanat.jpg", "Datanät", "datanat.html"),
    ("dokumentation.jpg", "Dokumentation", "dokumentation.html"),
    ("laddbox.jpg", "Laddboxar", "elbilsladdare.html"),
    ("solceller.jpg", "Solceller", "solceller.html"),
    ("varme.jpg", "Värme", "golvvarme.html"),
]


def services_section(place):
    cards = "".join(img_card(i, t, h) for i, t, h in SERVICES9)
    return (f'<section class="sec gray" id="tjanster"><div class="wrap">'
            f'<div class="sec-head"><div class="prose">{head("Tjänster", f"Tjänster vi kan erbjuda inom el i {place}")}</div>'
            f'<a class="btn btn-red" href="{TEL}">Ring oss</a></div>'
            f'<div class="grid g3">{cards}</div></div></section>')


ROT_BADGE = '<div class="rot" style="right:-18px;top:-30px"><div>Rot?<small>Avdrag direkt<br>på fakturan</small></div></div>'


def rot_text(extra_intro=None):
    t = ("Elarbeten i privatbostad berättigar normalt till ROT-avdrag som ger skattereduktion på arbetskostnaden. "
         "Vi hanterar administrationen mot Skatteverket och drar av beloppet direkt på fakturan. "
         "Kontakta oss för att bekräfta att just ditt arbete kvalificerar.")
    return t


TRYGG = [
    "Att kunna känna sig trygg och säker i sitt hem och i andra miljöer där vi vistas är nog en självklarhet för de flesta av oss. I Sverige har vi i många år arbetat intensivt med att begränsa olyckor och andra skador orsakade av el, bland annat genom Elsäkerhetsverkets arbete. Och även om vi varit framgångsrika jämfört med många andra länder händer det dessvärre varje år ett antal elolyckor.",
    "Idag vet nog de flesta att den bästa försäkringen mot elolyckor är att anlita en elyrkesman, en riktig elektriker kort sagt.",
    "Samtliga våra montörer är elyrkesmän och har ABL- eller BB1-behörighet. Alla av oss utförda arbeten, nyinstallationer och reparationsarbeten, åtföljs av garanti och Bloms El & Data är naturligtvis ansvarsförsäkrade för din skull. Allt elmaterial som används i installationer utförda av oss är CE-märkt och i övrigt av högsta kvalité.",
    "Är du tveksam eller känner oro över din elsäkerhet, låt oss hjälpa dig göra en sakkunnig och kompetent bedömning.",
]


def trygg_section():
    """Trygg el: kompakt ruta med porträtt (förslag 5 i design/trygg-el-forslag-2)."""
    return ('<section class="trygg" id="trygg-el"><div class="wrap"><div class="trygg-box">'
            '<img src="img/portratt.jpg" alt="Montör från Bloms El &amp; Data" loading="lazy">'
            f'<div class="prose">{head("Trygg el", "Den bästa försäkringen mot elolyckor är att anlita en riktig elektriker.")}'
            + ps("Alla våra montörer har ABL- eller BB1-behörighet. Arbetena omfattas av garanti, vi är ansvarsförsäkrade och använder bara CE-märkt material.")
            + f'<div class="btns"><a class="btn btn-red" href="{TEL}">Ring oss</a><a class="btn btn-line arrow" href="kontakt.html">Boka bedömning </a></div>'
            '</div></div></div></section>')


def smart_band():
    return ('<section class="band"><img src="img/team-bro-upscaled.jpg" alt="Tre montörer från Bloms El &amp; Data går med verktyg" loading="lazy" style="object-position:center 35%"><div class="wrap"><div class="prose">'
            f'{head("Smart Teknik", "Smarta lösningar för vardagen")}'
            + ps("Det finns massor av roliga, smarta lösningar som underlättar din vardag. Som gör ditt hem eller kontor säkrare, enklare och bekvämare. Som låter dig styra värmen i sommarstugan, musiken i hela huset utan att du lämnar soffan eller belysningen i verkstan fast du redan stämplat ut och åkt hem. Vi berättar mer om några smarta prylar på länken nedan.")
            + '<div class="btns"><a class="btn btn-white arrow" href="smart-teknik.html">Läs mer </a></div></div></div></section>')


def trust_section():
    return ('<section class="sec gray" style="padding-block:48px"><div class="wrap"><div class="trust">'
            '<div><img src="img/uc.png" alt="UC"><span><b>HÖGSTA KREDITVÄRDIGHET</b><small>Bloms El &amp; Data · 556754-3656</small></span></div>'
            '<a href="https://www.elsakerhetsverket.se/" target="_blank" rel="noopener"><img src="img/kolla.png" alt=""><span><b>KOLLA ELFÖRETAGET</b><small>Kontrollera att ditt elföretag är registrerat hos Elsäkerhetsverket</small></span></a>'
            '</div></div></section>')


def contact_cta(title, text):
    return (f'<section class="sec red"><div class="wrap split"><div class="prose">{head("Kontakt", title)}{ps(text)}</div>'
            f'<div class="prose" style="align-items:flex-start"><p style="font-size:clamp(26px,2.6vw,36px);font-weight:700;color:#fff;user-select:all">{PHONE}</p>'
            f'<p style="user-select:all">{MAIL}</p><div class="btns"><a class="btn btn-white" href="{TEL}">Ring oss</a>'
            '<a class="btn btn-ghost arrow" href="kontakt.html">Skicka förfrågan </a></div></div></div></section>')


def view_section(place_phrase):
    return (f'<section class="sec" id="hur-vi-ser"><div class="wrap split">'
            f'<div><span class="eyebrow">Hur vi ser på saken</span><p class="quote">Vi vill helt enkelt vara en elektriker {e(place_phrase)} du skall <em>känna förtroende för</em> och anlita igen.</p></div>'
            '<div class="prose">'
            + ps("Vi gör alltid vårt yttersta för att skapa goda och långvariga kundrelationer. Nöjda kunder är inte bara en hederssak utan en förutsättning för ett livskraftigt och långsiktigt företagande.",
                 "Vi strävar alltid efter att hitta bästa pris och kvalité i varje uppdrag.",
                 "Vi erbjuder snabb och professionell kompetens inom vårt verksamhetsområde. Vi gör det genom att alltid vara uppdaterade med den senaste kunskapen inom modern och smart elteknik. Och svårare än så är det inte.")
            + btns(ghost=False) + '</div></div></section>')


# ---------------------------------------------------------------- herokarusell (startsidan)
# De tio heroförslagen från design/hero-galleri visas på startsidan och bläddras i sidled.
GALLERY = OUT.parent / "design" / "hero-galleri" / "index.html"


def prefix_css(css, pre):
    """Prefixar alla selektorer med `pre`, även inne i @media-block."""
    out, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        if sel.startswith("@"):
            depth, k = 1, j + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(css[k], 0)
                k += 1
            out.append(f"{sel}{{{prefix_css(css[j + 1:k - 1], pre)}}}")
        else:
            k = css.find("}", j) + 1
            sels = ",".join(f"{pre} {s.strip()}" for s in sel.split(",") if s.strip())
            out.append(f"{sels}{css[j:k]}")
        i = k
    return "\n".join(out)


def gallery_parts():
    import re
    src = GALLERY.read_text(encoding="utf-8")
    style = src[src.index("<style>") + 7:src.index("</style>")]
    css = style[style.index("/* hero body */"):style.index("/* ---------- presenter controls")]
    css += style[style.index("/* ---------- phone ---------- */"):]
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    slides = re.findall(r'<section class="slide" id="(f\d+)" data-name="([^"]+)">(.*?)</section>', src, flags=re.S)
    unit = re.compile(r'(?<![\w.#-])(\d*\.?\d+)(s?)v([wh])\b')
    css = unit.sub(lambda m: f"calc(var(--v{m.group(3)},1{m.group(2)}v{m.group(3)})*{m.group(1)})", css)
    return prefix_css(css, ".heroes"), slides


def localize(html):
    import re
    html = html.replace('<nav class="nav"></nav>', "").replace('src="img/', 'src="img/hero/')
    html = html.replace('https://www.blomsel.se/kontakt', "kontakt.html")
    html = re.sub(r'https://www\.blomsel\.se/([a-z-]+)', r'\1.html', html)
    return html.replace(' target="_blank" rel="noopener"', "")


def hero_carousel():
    css, slides = gallery_parts()
    (OUT / "assets" / "heroes.css").write_text("/* Genereras av build.py från design/hero-galleri */\n" + css, encoding="utf-8")
    items = "".join(
        f'<div class="hx" id="{sid}" data-name="{name}" role="group" aria-roledescription="bild" aria-label="Förslag {sid[1:]}: {name}">{localize(body)}</div>'
        for sid, name, body in slides)
    return ('<section class="heroes" aria-roledescription="karusell" aria-label="Heroförslag">'
            f'<div class="hx-track" id="hx-track" tabindex="0">{items}</div>'
            '<button class="hx-arrow hx-prev" type="button" aria-label="Föregående förslag"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M15 18l-6-6 6-6"/></svg></button>'
            '<button class="hx-arrow hx-next" type="button" aria-label="Nästa förslag"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M9 6l6 6-6 6"/></svg></button>'
            '<div class="hx-bar"><div class="wrap"><span class="hx-lab" id="hx-lab" aria-live="polite"></span><div class="hx-dots" id="hx-dots"></div></div></div>'
            '</section>')


# ---------------------------------------------------------------- sidmall
def page(slug, title, desc, body, active=None):
    menu = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{e(t)}</a></li>' for h, t in NAV)
    areas = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in AREAS)
    pages = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in NAV[1:] + [("om-oss.html", "Om oss"), ("vanliga-fragor.html", "Vanliga frågor")])
    servs = "".join(f'<li><a href="{x["slug"]}.html">{e(x["name"])}</a></li>' for x in EXTRA if x.get("parent"))
    return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="claude:viewport-fit-sides" content="cover">
<script>(function(){{var d=document.documentElement;function f(){{var w=innerWidth,h=innerHeight,z=w<1100?1:Math.max(1,Math.min(w/1440,h/900));d.style.zoom=z>1.001?z:'';d.style.setProperty('--vw',w/z/100+'px');d.style.setProperty('--vh',h/z/100+'px')}}f();addEventListener('resize',f)}})()</script>
<link rel="icon" href="img/logo-symbol.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/style.css">
{'<link rel="stylesheet" href="assets/heroes.css">' if slug == "index" else ""}
</head>
<body data-page="{slug}">
<a class="skip" href="#innehall">Hoppa till innehållet</a>
<header class="nav"><div class="wrap">
<a class="logo" href="index.html"><img src="img/logo-white.png" alt="">BLOMS EL &amp; DATA</a>
<button class="burger" type="button" aria-expanded="false" aria-controls="meny">{ICON["menu"]}Meny</button>
<ul class="menu" id="meny">{menu}</ul>
</div></header>
<main id="innehall">
{body}
</main>
<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><a class="logo" href="index.html"><img src="img/logo-white.png" alt="">BLOMS EL &amp; DATA</a>
<p>Certifierad elektriker i Göteborg sedan 2008. Kontor och lager i Göteborg, materialdepåer i hela regionen.</p></div>
<div><h4>Kontakt</h4><ul><li><a href="{TEL}" class="copy">{PHONE}</a></li><li><a href="mailto:{MAIL}" class="copy">{MAIL}</a></li><li>Blomstergatan 5</li><li>411 04 Göteborg</li></ul></div>
<div><h4>Sidor</h4><ul>{pages}</ul></div>
<div><h4>Tjänster</h4><ul>{servs}</ul></div>
<div><h4>Göteborg med omnejd</h4><ul>{areas}<li><a href="elektriker-boras.html">Borås</a></li></ul></div>
</div>
<div class="foot-bottom"><span>© 2026 Bloms El &amp; Data AB · Org.nr 556754-3656</span><a href="cookiepolicy.html">Cookiepolicy</a></div>
</div></footer>
<div class="cookie" id="cookie" hidden><span>Vi använder cookies på vår webbplats för att ge dig en bättre upplevelse. <a href="cookiepolicy.html">Cookiepolicy</a></span><button class="btn btn-white" type="button">Ok</button></div>
<script src="assets/main.js"></script>
</body>
</html>
"""


PAGES = {}

# ================================================================ HEM
PAGES["index"] = page("index", "Elektriker Göteborg | Elfirma - Bloms El & Data",
    "Elservice i Göteborg. Nyinstallation, ombyggnation, service och rådgivning - kort sagt allt man förväntar sig av en elektriker och ofta lite till.",
    hero_carousel()
    + split("kraft-uttag.jpg", head("Hela kedjan", "Nyinstallation, ombyggnation, service, felsökning och rådgivning")
            + ps("Vi täcker hela kedjan från planering och ritning till installation, dokumentation och besiktning. Samtliga montörer är certifierade elektriker med ABL- eller BB1-behörighet och självklart är Bloms El & Data ansvarsförsäkrade för din skull."),
            alt="Röda kraftuttag på en vägg")
    + usp_section("Elfirma i Göteborg")
    + split("kraft-uttag.jpg", head("Privat och företag", "Elektriker i Göteborg för privat och företag")
            + ps("Bloms El & Data AB är registrerat hos Elsäkerhetsverket för lågspänningsarbeten inom samtliga relevanta kategorier: bostäder, allmänna och offentliga utrymmen, industri, och elproduktionsanläggningar som solceller och batterilager.",
                 "En behörig elektriker utfärdar elsäkerhetsintyg, dokumenterar utförda arbeten med elritningar och mätprotokoll, och kan göra en sakkunnig bedömning av befintlig anläggning. Den dokumentationen är också av praktiskt värde vid om- eller tillbyggnad längre fram.")
            + '<p><strong>Helt enkelt, vet man vad som finns bakom väggarna går arbetet snabbare och kostar mindre.</strong></p>'
            + btns(contact=False), bg="gray", rev=True, alt="Röda kraftuttag på en vägg").replace("kraft-uttag.jpg", "elskap.jpg", 1)
    + services_section("Göteborg")
    + split("servicebil-alvsborg.jpg", head("Hela regionen", "Vi täcker hela Göteborgsregionen")
            + ps("I Göteborg finns kontor och lager. Och därifrån åtar vi oss uppdrag från Falkenberg i söder till Uddevalla i norr; Ulricehamn, Göteborg, Borås och allt där emellan.",
                 "Våra materialdepåer finns i Mölndal, Partille, Hisingen, Västra Frölunda, Lindholmen, Kungsbacka, Kungälv och Borås. Så ditt elmaterial finns alltid nära.")
            + '<h3 class="h3" style="margin-top:12px">ROT-avdrag för privatpersoner</h3>'
            + ps("Elarbeten i privatbostad berättigar normalt till ROT-avdrag, som ger skattereduktion på arbetskostnaden. Bloms El & Data hanterar administrationen och drar av beloppet direkt på fakturan. Kontakta oss för att bekräfta om ditt specifika arbete kvalificerar.")
            + btns(call=False, ghost=False), alt="Montörer vid servicebilen nära Älvsborgsbron", media_cls="tall", badge=ROT_BADGE)
    + view_section("i Göteborg")
    + trygg_section()
    + smart_band()
    + trust_section(),
    active="index.html")


TJANSTER_OVERVIEW = ('<section class="sec"><div class="wrap"><div class="sec-head"><div class="prose">'
                     + head("Alla tjänster", "Välj tjänst") + '<p>Varje tjänst har en egen sida med mer information, vanliga frågor och hur det går till.</p></div></div><div class="grid g4">'
                     + "".join(img_card(x["hero"], x["name"], f'{x["slug"]}.html') for x in EXTRA if x.get("parent") == "tjanster")
                     + img_card("solceller.jpg", "Solceller", "solceller.html") + img_card("laddbox.jpg", "Elbilsladdare", "elbilsladdare.html")
                     + '</div></div></section>')

# ================================================================ TJÄNSTER
SV = [
    ("belysning", "belysning.jpg", "Belysning", "Belysning i ett skyltfönster",
     ["Det finns nästan ingen miljö som inte omfattas av belysning. Och de senaste åren har en mängd nya alternativ och tekniker sköljt över oss. Förutom planering och installation hjälper vi också dig att välja rätt, räkna på energibesparing och ljusberäkning så du får precis den ljusmiljö du önskar.",
      "Visste ni till exempel att man kan ljussätta en butiksmiljö så att denna triggar kundernas köpvilja?"]),
    ("datanat", "datanat.jpg", "Datanät", "Nätverkskablar i en switch",
     ["Idag är datanät lika självklart vid nybyggnation och kommersiella fastigheter som telefonjack var förr. Vi lever i en digitalt uppkopplad värld, där vi tar för givet att musiken skall höras i alla rum, att kylskåpet är uppkopplat och att belysningen skall kunna styras från telefonen.",
      "Vi arbetar allt mer med smarta digitala nät."]),
    ("kraft", "uttag-rott.jpg", "Kraft", "Röda kraftuttag",
     ["Idag finns många nya och intressanta alternativ för kraft och värmeförsörjning och det görs hela tiden tekniska framsteg i nya, mer miljövänliga och effektivare uppvärmning.",
      "Vi utför kompletta elinstallationer i de flesta miljöer och även där högt ställda krav på utseende och funktion ställs."]),
    ("varme", "termostat.jpg", "Värme", "Termostat för golvvärme",
     ["Elektrisk golvvärme är nästan alltid att föredra; effektivt, prisvärt och hållbart. Underhållsfritt när det väl är på plats. Och då har vi inte ens nämnt vilken skön och behaglig värme det blir.",
      "För att lägga golvvärme krävs behörig elektriker. För flytspackling och klinkerläggning anlitar vi fackman inom våtutrymme."]),
    ("dokumentation", "matning.jpg", "Dokumentation", "Elektriker mäter och dokumenterar",
     ["Låter tråkigt kanske? Men så oerhört viktigt och kostnadsbesparande den dagen ni vill bygga om, bygga ut eller lägga till något.",
      "Vi kan dokumentation; vi gör belysningsberäkningar, elritningar, mätprotokoll och utfärdar elsäkerhetsintyg."]),
    ("industri", "elskap.jpg", "Industrielektriker", "Elskåp i en industrimiljö",
     ["Ett nära samarbete med vår elektriker som skapar kontroll över el och automation i maskinparken är teknikföretagens bästa investering, där vår långsiktiga strävan är att minimera oförutsedda driftstopp."]),
]
body = hero("kanal.jpg", "Våra tjänster",
            "Installation, service, belysning, kraft, solceller, elbilsladdning, datanät och nybyggnation. Vi tar hand om hela kedjan från planering och ritning till installation och dokumentation.",
            [img_card(i, t, f"#{k}", a) for k, i, t, a, _ in SV[:4]], eyebrow="Elektriker Göteborg", pos="70% center")
SV_PAGE = {"belysning": "belysning", "datanat": "datanat", "kraft": "kraft", "varme": "golvvarme", "dokumentation": "dokumentation", "industri": "industrielektriker"}
body += TJANSTER_OVERVIEW
for n, (k, i, t, a, txt) in enumerate(SV):
    body += split(i, head("Tjänst", t) + ps(*txt) + f'<div class="btns"><a class="btn btn-line arrow" href="{SV_PAGE[k]}.html">Läs mer om {e(t.lower())} </a></div>',
                  rev=n % 2 == 1, bg="gray" if n % 2 == 1 else "", alt=a).replace('<section class="sec', f'<section id="{k}" class="sec', 1)
body += trust_section()
PAGES["tjanster"] = page("tjanster", "Elektriker Göteborg | Tjänster | Bloms El & Data",
    "Elektriker Göteborg, Installation, Service, Belysning, Kraft, Solceller, Elbilsladdning, Datanät, Nybyggnation", body, "tjanster.html")

# ================================================================ ELBILSLADDARE
LB = [
    ("abb", "abb-terra.jpg", "Laddbox 1", "ABB Terra 11kW",
     ["ABB Terra AC laddbox är en avancerad laddbox som ger säker laddning av elbilar med (3-fas) alt. uttag eller 5 m fast kabel med typ-2 handske. Alla modeller kan kommunicera med Bluetooth, Ethernet, Modbus via RS485 och OCPP 1.6 J. För mobil uppkoppling välj 4G-modell.",
      "Med inbyggda smarta lasthanteringsfunktioner minimeras risken för överbelastning av fastighetens huvudsäkring. Lasthantering kan styras av Terra AC-laddboxen lokalt med hänsyn till övrig elförbrukning i anläggningen, alternativt med hjälp av den tillhörande molntjänsten ChargerSync Portal."],
     False, "Måste kompletteras med jordfelsbrytare."),
    ("garo", "garo.jpg", "Laddbox 2", "Garo GLB 22kW",
     ["Garos laddbox är också den avancerad; skyddad mot DC-felströmmar och förberedd med en dynamisk lastbalansering. DC-felövervakning är en säkerhetsfunktion som krävs vid laddning av EV. Lastbalansering reducerar automatiskt fordonets laddström och minimerar risken att huvudsäkringen löser ut.",
      "Komplettera med GARO Modbus 1-fas/3-fas energimätare i elcentralen för aktivering av lastbalansering. Laddboxen kan kompletteras med RFID-läsare och/eller kommunikationskort för att aktivera många smarta extra funktioner. JFB-A med DC-övervakning och utan elmätare."],
     True, "Behöver inte kompletteras med jordfelsbrytare."),
    ("aura", "laddbox.jpg", "Laddbox 3", "Charge Amps Aura 2x22kW",
     ["Charge Amps Aura är en kraftfull avancerad laddbox för laddning av två bilar samtidigt. Designad av Joachim Nordwall, före detta chefsdesigner hos Koenigsegg.",
      "Jordfelsbrytare med överspänningsskydd. Separat DC-felströmsskydd och en RCBO typ A är integrerad i laddstationen för varje uttag.",
      "Kan kopplas mot valfri molntjänst kompatibel med OCPP, eller Charge Amps Cloud."],
     True, "Behöver inte kompletteras med jordfelsbrytare."),
]
body = hero("chargeamps-montage.jpg", "Elbilsladdare",
            "Vi monterar elbilsladdare till privatpersoner, bostadsrätts- och villaföreningar och företag i Göteborg, Partille, Mölndal och alla kringliggande kommuner.",
            [img_card(i, s, f"#{k}") for k, i, _, s, _, _, _ in LB] + [stat_card("50 %", "Grön teknik-avdrag", "#gron-teknik")],
            eyebrow="Laddbox och laddstation")
body += ('<section class="sec"><div class="wrap"><div class="callout"><p>Din elbil behöver laddas med en riktig elbilsladdare. Att ladda din bil i ditt vanliga uttag kan orsaka brand och rekommenderas inte! '
         'Det är på sin höjd en tillfällig lösning i absoluta undantagsfall och knappt det (och om du ändå måste, gör det under uppsikt). Elsystemet i ditt hem är helt enkelt inte avsett för, och klarar inte, den belastning det innebär att ladda en elbil. '
         'Använd alltid en riktig elbilsladdare eller laddbox för din säkerhets skull.</p></div></div></section>')
body += split("chargeamps-1.jpg", head("Rätt laddare", "Val av elbilsladdare?")
              + ps("Det finns många att välja mellan på marknaden. Alla är bäst om du frågar dem. Om du frågar oss är det viktigaste att laddaren ligger skyddad över en riktig jordfelsbrytare och installeras av behörig elektriker.",
                   "Vill du ha fler funktioner på din laddare, som att bilen skall ladda vid speciella tider eller att hushålla med elen, blir det mer att ta hänsyn till. Då skall en mer avancerad laddare installeras.",
                   "Det är inga stora prisskillnader mellan olika laddare på marknaden. Installationskostnaden kan däremot variera mer då förutsättningar skiljer mycket mellan olika fastigheter. Därför rekommenderar vi alltid att du köper din elbilsladdare av någon som också installerar laddare och som förstår helhetsbilden. Det lönar sig alltid i längden."),
              alt="Charge Amps-laddare monterad på vägg")
body += split("chargeamps-2.jpg", head("Laddning med egen el", "Drömmer du om en bil med minimal miljöpåverkan?")
              + ps("Det gör nog många idag. Men det är sannerligen inte lätt att veta varifrån elen i ens uttag kommer, eller hur mycket av den som är grön. När du installerar solceller på din fastighet kan du själv styra i vilken utsträckning du vill ladda bilen på egenproducerad el.")
              + '<div class="btns"><a class="btn btn-line arrow" href="solceller.html">Läs om helhetslösning med solceller </a></div>',
              rev=True, bg="gray", alt="Laddkabel kopplad till en elbil")
body += ('<section class="sec"><div class="wrap"><div class="sec-head"><div class="prose">' + head("Laddboxar vi installerar", "Tre laddboxar vi rekommenderar") + '</div></div><div class="grid g3">'
         + "".join(f'<article class="product" id="{k}"><div class="img"><img src="img/{i}" alt="{e(s)}" loading="lazy"></div><div class="in"><span class="tag">{e(n)}</span><h3>{e(s)}</h3>{ps(*txt)}'
                   f'<p class="note {"ok" if ok else "warn"}">{"✓" if ok else "!"} {e(note)}</p></div></article>' for k, i, n, s, txt, ok, note in LB)
         + '</div></div></section>')
body += ('<section class="sec gray" id="gron-teknik"><div class="wrap split"><div class="prose">' + head("Skatteavdrag", "Skatteavdrag för Grön Teknik")
         + ps("Som privatkund för grön teknik installerad efter 1 januari 2021 får du skatteavdrag med 50 % av kostnaden för installation och material upp till 50 000 kr. Skatteavdraget sker direkt på fakturan, på samma sätt som för ROT och RUT. Enkelt och mycket billigare för dig.",
              "Så du som går i tankar på att installera en egen laddbox: vänta inte för länge, vem vet hur länge skatteavdraget finns kvar.")
         + btns(ghost=False) + '</div><div class="grid g2"><div class="statbox"><span class="bignum">50 %</span><b>av installation och material</b><p>För elbilsladdare och batterilager.</p></div>'
         '<div class="statbox"><span class="bignum">50 000</span><b>kronor per person och år</b><p>Avdraget görs direkt på fakturan.</p></div></div></div></section>')
body += split("brf-laddare.jpg", head("BRF", "Bostadsrättsförening")
              + ps("Många bostadsrättsföreningar har allt fler innehavare som skaffar elbilar och elhybrider och installerar elbilsladdare just nu. Dessutom ökar det oftast föreningens attraktionskraft och därmed lägenheternas värde.",
                   "Vår lösning är underhållsfri och enkel för föreningen. Förbrukningen faktureras direkt till användaren månadsvis. Kontakta oss om du vill veta mer om hur du kan få elbilsladdning till din förening.")
              + '<div class="btns"><a class="btn btn-red arrow" href="laddbox-brf.html">Laddboxar för BRF och företag </a></div>', alt="Laddstationer i ett garage")
PAGES["elbilsladdare"] = page("elbilsladdare", "Elbilsladdare | Bloms El | Göteborg",
    "Vi monterar elbilsladdare till privatpersoner, bostadsrätts- och villaföreningar och företag. I Göteborg, Partille, Mölndal och alla andra kringliggande kommuner runt Göteborg", body, "elbilsladdare.html")

# ================================================================ SMART TEKNIK
body = hero("smart-hem.jpg", "Smart teknik",
            "Vi gillar verkligen när vi kan bidra med smarta idéer och lösningar som underlättar din vardag. Det finns massor, och det har blivit lite av vårt expertområde inom el och data.",
            [img_card("jordfelsbrytare.png", "Jordfelsbrytare", "#jordfelsbrytare"), img_card("wifi-app.png", "Wi-Fi och app", "#wifi"),
             img_card("utebelysning.jpg", "Smart belysning", "#belysning"), img_card("hogtalare.png", "Smart ljud", "#ljud")],
            eyebrow="El och data")
body += ('<section class="sec"><div class="wrap"><div class="prose" style="max-width:820px">'
         + ps("Mycket av denna nya smarta teknik är inte den enklaste att presentera bildmässigt då det mesta ofta gömmer sig bakom en lucka eller i en vägg. Men just att det inte syns är ofta en del av kvalitén.",
              "Men det finns också de som vill ha tekniken synlig, ibland för att kunna visa upp sina teknikburkar och mätarlådor på väggen för sina vänner. Detta är vad vi, inom skrået, kallar för infälld eller utanpåliggande installation.",
              "I båda fallen är det ändå helheten av idé, installation och funktion som skapar magin med smart teknik. Så håll utkik här för mer exempel på saker som gör livet både enklare och roligare.")
         + '</div></div></section>')
body += split("jordfelsbrytare.png", head("Smart säkerhet", "Självåterställande jordfelsbrytare")
              + ps("Med en självåterställande jordfelsbrytare kommer din jordfelsbrytare att återstartas när elfelet på din anläggning inte längre kvarstår.",
                   "Det är både smart och kan visa sig vara väldigt värdefullt; om en traditionell jordfelsbrytare bryter strömmen måste du manuellt återställa den innan du har fungerande el igen. Är du då inte på plats, kanske bortrest några dagar, kan mat i frysen vara förstörd när du kommer hem, rör frysa sönder under vintern eller bilen inte vara laddad på morgonen när du skall iväg.",
                   "Anledningen till att en jordfelsbrytare löser ut kan vara många; ett blixtnedslag eller en vanlig lampa när den går sönder är två orsaker. Jordfelsbrytare i sig är absolut nödvändigt och kan till och med vara en livförsäkring som skyddar mot elbränder, men det här är en ännu smartare variant.",
                   "Att en jordfelsbrytare skall testas var sjätte månad för att vara godkänd vet väl alla. Den här jordfelsbrytaren testar sig själv automatiskt och underhållet görs utan att strömmen bryts. Kravet på fastighetsägare att utföra dessa tester gör att bytet till den här jordfelsbrytaren blir en kostnadsbesparing, då underhållskostnader tas bort och störande strömbortfall inte längre uppstår."),
              alt="Självåterställande jordfelsbrytare", media_cls="contain").replace('<section class="sec', '<section id="jordfelsbrytare" class="sec', 1)
body += split("wifi-app.png", head("Övervakning", "Wi-Fi och app")
              + ps("Tack vare Wi-Fi ReStart-appen kan du övervaka systemstatusen i realtid och överallt. Korrekt funktion av jordfelsbrytaren kan testas hela tiden och du fjärrstyr självdiagnostik med din app: du får information om datum, tid och resultat för alla Autotest-operationer.",
                   "Du kan se värdena för den energi som produceras och förbrukas, den aktiva och reaktiva effekten, strömmen och spänningen i systemet.",
                   "En jättebra funktion för dig som har verksamhet och fastigheter där sexmånadersunderhåll av jordfelsbrytare skall testas och dokumenteras. Här görs testet i aktivt läge och inget strömbortfall under testet stör verksamheten."),
              rev=True, bg="gray", alt="Wi-Fi-modul för jordfelsbrytare", media_cls="contain").replace('<section class="sec', '<section id="wifi" class="sec', 1)
body += split("utebelysning.jpg", head("Ljus", "Smart belysning")
              + ps("Tänd utebelysningen automatiskt när det blir mörkt. Kom hem till en bostad som är upptänd, varm och inbjudande och som är nedsläckt för att spara el när ingen ändå är på plats.",
                   "Du kan styra din belysning via en app, din röst, eller i förväg schemalägga belysningen av ditt hem, företag eller jordbruk.",
                   "Vill du ha ett hem som är uppkopplat och åtkomligt från en annan plats, på resan eller från arbetet, kan du fjärrstyra belysning, värme och andra smarta enheter direkt från din telefon. Praktiskt, bekvämt och säkert. Tala med oss om vad du vill ha så installerar vi det."),
              alt="Utebelysning vid en entré").replace('<section class="sec', '<section id="belysning" class="sec', 1)
body += '<div class="photo-strip"><img src="img/smart-hem.jpg" alt="Smart hem styrs från mobilen" loading="lazy"></div>'
body += split("hogtalare.png", head("Ljud", "Smart ljud")
              + ps("Högtalare för infälld montering. Vi bygger en plats för dina högtalare i ditt tak eller din vägg och ansluter kraften. Endast en grill avslöjar att det är högtalare på 50 watt där bakom.",
                   "Vi installerar högtalare som levererar superb ljudkvalitet med knivskarp klarhet. Och du kan enkelt strömma ljud från din Wi-Fi-anslutna enhet till en zon, eller upp till 30 zoner samtidigt (med en eller två högtalare i varje zon). Appen sparar dina inställningar för individuella zoner eller Party Mode (alla högtalare samtidigt) nästa gång du öppnar appen."),
              rev=True, bg="gray", alt="Infälld takhögtalare", media_cls="contain").replace('<section class="sec', '<section id="ljud" class="sec', 1)
body += contact_cta("Vill du veta mer?", "Det här är ett urval av smarta saker för hem och företag. Utvecklingen går rasande fort och det presenteras nya innovativa lösningar nästan dagligen. Vill du veta mer om hur vi kan hjälpa dig till ett smartare, bekvämare och enklare hem, kontor eller jordbruk? Vi har med all säkerhet några ess i rockärmen som gör vardagen enklare, och några som bara gör den roligare.")
PAGES["smart-teknik"] = page("smart-teknik", "Smart Teknik | Bloms El & Data",
    "Smarta lösningar för hem, kontor och jordbruk: självåterställande jordfelsbrytare, smart belysning och smart ljud från Bloms El & Data i Göteborg.", body, "smart-teknik.html")

# ================================================================ SOLCELLER
body = hero("solceller-cover.jpg", "Vi installerar solceller",
            "Minska ditt klimatavtryck utan att göra avkall på din levnadsstandard. Solpaneler är 100 % förnybar energi och en investering för framtiden. Vi planerar, monterar och installerar. Tar hand om allt, kort sagt.",
            [img_card("sol-installation.jpg", "Vad är solceller?", "#vad"), img_card("sol-kungalv.jpg", "Var börjar man?", "#borja"),
             img_card("solpaneler.jpg", "Installation", "#installation"), img_card("sol-jordbruk.png", "Underhåll och service", "#underhall")],
            eyebrow="Solceller och solpaneler i Göteborg",
            buttons='<div class="btns"><a class="btn btn-red arrow" href="kontakt.html">Begär offert </a><a class="btn btn-ghost" href="' + TEL + '">Ring oss</a></div>')
body += ('<section class="sec"><div class="wrap split"><div class="prose">' + head("Allt ingår", "När du anlitar oss ingår")
         + ps("Anskaffningskostnaden betalar sig själv över tid och ökar värdet på din fastighet.") + '</div><ul class="checklist">'
         + "".join(f'<li class="chk">{e(x)}</li>' for x in ["Ritningar", "Beräkning på elproduktion och besparing", "Batterilagring som ytterligare sänker kostnaderna",
                                                          "Möjlighet att köra huset från batteri och solpaneler vid strömavbrott",
                                                          "Åskskydd / potentialutjämnat tak för att leda bort eventuella elchocker", "App för att följa produktion och elbilsladdning"])
         + '</ul></div></section>')
body += split("sol-installation.jpg", head("Grunderna", "Vad är solceller?")
              + ps("Solceller är ljuskänsliga halvledardioder som omvandlar ljus till elektrisk spänning; energi i form av likström. En växelriktare omvandlar sedan likströmmen till växelström som kan användas i din fastighet, ladda din elbil, lagras för att användas när solen inte lyser eller skickas ut på elnätet."),
              bg="gray", alt="Montörer installerar solpaneler på ett tak").replace('<section class="sec', '<section id="vad" class="sec', 1)
body += split("sol-kungalv.jpg", head("Första steget", "Var börjar man?")
              + ps("Vår bild är att de flesta börjar med att prata med grannar eller vänner, googla runt och skaffa sig en bild. Det är inget fel i det, men det finns en hel del fällor att gå i och all information är tyvärr inte seriös.",
                   "När dina solcellsfunderingar börjar bli allvarliga tycker vi att du tidigt i processen skall kontakta någon som verkligen vet, någon som kan. Som oss till exempel.",
                   "Alla våra solcellsprojekt startar med en bedömning av din fastighets förutsättningar; vad som är möjligt att göra och en realistisk kalkyl. Vi gör beräkningar av hållbarhet för vind, hur du skall få ut det mesta av din installation, och vi arbetar bara med handplockade, pålitliga produkter med lång livslängd och god ekonomi."),
              rev=True, alt="Solpaneler på ett villatak i Kungälv", media_cls="tall").replace('<section class="sec', '<section id="borja" class="sec', 1)
body += ('<section class="sec gray" id="installation"><div class="wrap"><div class="grid g2">'
         '<div class="statbox"><h3 class="h3">Installation</h3>' + ps("Alla projekt, alla solcellsinstallationer vi gör, planeras noga före installation. Och du får information om hela processen före start.",
                                                                       "Du får med dig vår kunskap som erfaret elinstallationsföretag in i varje projekt. Det ger dig en trygg och prisvärd installation över tid.") + '</div>'
         '<div class="statbox"><h3 class="h3">Solcellsenergi</h3>' + ps("När allt är på plats trimmar vi in och optimerar systemet och du börjar producera din egen gröna el. Överskott lagrar du i batterier eller säljer. Du kan även ladda batterierna med el från nätet när priset är lågt och spara till timmar när det är dyrare, och på så sätt sänka totalkostnaden för din elförbrukning ytterligare.",
                                                                          "Du har full kontroll från systemets app och kan i realtid se hela anläggningens förbrukning och produktion. Solcellsteknik är idag en etablerad och standardiserad produkt, men utveckling sker fortfarande och vi uppdaterar oss löpande kring nya lösningar, nya regelverk och innovationer.") + '<div class="btns"><a class="btn btn-line arrow" href="batterilager.html">Läs om batterilager </a></div></div>'
         '</div></div></section>')
body += '<div class="photo-strip"><img src="img/sol-hovas.jpg" alt="Solcellsanläggning i Hovås" loading="lazy"></div>'
body += split("sol-jordbruk.png", head("Efter installationen", "Underhåll och service")
              + ps("Solcellspaneler är i stort sett underhållsfria. Regn och snö hjälper till att hålla dem rena och fria från beläggningar. I Göteborg och på västkusten är tjocka snölager sällsynta, men sådana eller mycket löv kan naturligtvis minska effektiviteten tillfälligt. Vill man inte vänta in nästa regnskur kan man borsta bort det. Använd inte snöskyffel.",
                   "Solpaneler har mycket lång livslängd, men systemet och växelriktaren mår bra av en översyn och optimering efter några år. Då får du snabb hjälp och vi har alltid svensktalande support.")
              + '<h3 class="h3" style="margin-top:12px">Hur effektiva är solceller?</h3>'
              + ps("Det beror på en rad faktorer. Förutom antal soltimmar och verkningsgrad, det vill säga hur stor del av den infångade solenergin som omvandlas till nyttig energi, påverkas effektiviteten av solpanelernas lutning, hur stor solinstrålningen är, väderstreck och temperatur. Hur stora och många solpanelerna är naturligtvis, och om det är snö eller smuts på dem.",
                   "Kontakta oss så lämnar vi en offert utifrån just dina förutsättningar."),
              alt="Solpaneler på ett jordbruk").replace('<section class="sec', '<section id="underhall" class="sec', 1)
body += contact_cta("Premium kvalité", "Det finns många tillverkare av solceller i världen. En installation är en stor investering som skall hålla i många år och vi rekommenderar verkligen alla att välja kvalité med omsorg. Det lönar sig.")
PAGES["solceller"] = page("solceller", "Solceller | Solpaneler | Göteborg | Bloms El & Data",
    "Vi monterar och installerar solceller och solpaneler i och kring Göteborg. Kontakta oss för att veta mer om hur du kan sänka dina elkostnader och samtidigt göra ett klimatsmart val.", body, "solceller.html")

# ================================================================ SKATTEREDUKTION
body = hero("kabelrulle.jpg", "Rotavdrag och Grön Teknik",
            "Du som äger en fastighet eller bostadsrätt har ofta rätt till skattereduktion när du renoverar, bygger om eller installerar grön teknik. Vi tar hand om allt pappersarbete och avdraget syns direkt på fakturan.",
            [stat_card("30 %", "Rotavdrag på arbetskostnad", "#rot"), stat_card("20 %", "Grön teknik: solpaneler", "#gron"),
             stat_card("50 %", "Batterilager och laddbox", "#gron"), stat_card("50 000 kr", "Max per person och år", "#gron")],
            eyebrow="Skattereduktion")
body += split("gata-servicebil.jpg", head("Rotavdrag", "Så fungerar rotavdraget")
              + ps("Du som äger en fastighet eller bostadsrätt har ofta rätt till så kallat rotavdrag om du skall renovera, bygga om eller bygga till. Det innebär kort sagt att du kan få bidrag från staten för del av arbetskostnaden. Rotavdraget infördes 1993 för att främja renoveringar och underhåll av bostäder, samtidigt som det ger privatpersoner möjlighet att få skatteavdrag för arbetskostnader vid olika typer av hushållsarbete.",
                   "För att vara berättigad till rotavdrag måste arbetet utföras av ett godkänt företag, som vårt. Rotavdraget innebär att du som privatperson kan få skattereduktion med upp till 30 % av arbetskostnaderna för det godkända arbetet. Maxbeloppet för avdraget varierar årligen och kan ändras av Skatteverket.",
                   "Vi har arbetat med rotavdrag ända sedan starten och det är en självklar del av våra rutiner. Det gör att det är enkelt för dig, ingenting du behöver ansöka om eller egentligen alls fundera så mycket över. Vi tar hand om allt pappersarbete och skattereduktionen redovisas direkt på fakturan."),
              alt="Montörer vid servicebilen", badge=ROT_BADGE).replace('<section class="sec', '<section id="rot" class="sec', 1)
body += split("solceller.jpg", head("Grön teknik", "Skattereduktion för grön teknik")
              + ps("På liknande sätt finns en skattereduktion för dig som installerar grön teknik. Sedan 2021 kan du som ägare till en fastighet eller bostadsrätt få bidrag till hela arbetet, det vill säga både arbetskostnad och material, vid installation av solceller, batterilager eller elbilsladdare.",
                   "Skattereduktionen kallas just Grön teknik, och du kan få en reduktion om max 50 000 kr per person och år. Som kund får du 20 % för solpaneler och 50 % för batterilagring och elbilsladdare. Och precis som för rotavdraget tar vi hand om allt det där åt dig. Du behöver inte göra någon ansökan, vi tar hand om pappersarbetet och skattereduktionen redovisas direkt på fakturan.")
              + btns(ghost=False), rev=True, bg="gray", alt="Montör installerar solpaneler").replace('<section class="sec', '<section id="gron" class="sec', 1)
PAGES["skattereduktion"] = page("skattereduktion", "Rot och Grön Teknik | Bloms El & Data",
    "Rotavdrag och skattereduktion för grön teknik. Bloms El & Data sköter pappersarbetet och drar av beloppet direkt på fakturan.", body, "skattereduktion.html")

# ================================================================ KONTAKT
body = hero("utebelysning.jpg", "Kontakta oss",
            "Vad kan vi hjälpa dig med? Enklaste sättet att nå oss är att mejla. Gör gärna det. Ringa funkar också :)",
            [icon_card("phone", "Ring oss", PHONE, TEL), icon_card("mail", "Mejla oss", MAIL, f"mailto:{MAIL}"),
             icon_card("pin", "Besök oss", "Blomstergatan 5, 411 04 Göteborg", "#karta"), icon_card("form", "Skicka förfrågan", "Vi svarar normalt samma arbetsdag", "#formular")],
            eyebrow="Bloms El & Data", buttons="")
body += ('<section class="sec" id="formular"><div class="wrap split"><div class="prose">' + head("Vi vill höra av dig!", "Berätta vad du behöver hjälp med")
         + ps("Beskriv vad som ska göras och hur fastigheten eller verksamheten används, så återkommer vi normalt samma arbetsdag med bedömning och offert.")
         + f'<ul class="checklist" style="margin-top:8px"><li class="chk">{PHONE}</li><li class="chk">{MAIL}</li><li class="chk">Blomstergatan 5, 411 04 Göteborg</li></ul></div>'
         '<form class="form" id="kontaktform" novalidate>'
         '<div class="two"><label for="f-namn">Namn<input id="f-namn" name="namn" autocomplete="name" required></label>'
         '<label for="f-tel">Telefon<input id="f-tel" name="telefon" type="tel" autocomplete="tel"></label></div>'
         '<label for="f-epost">E-post<input id="f-epost" name="epost" type="email" autocomplete="email"></label>'
         '<label for="f-arende">Ärende<select id="f-arende" name="arende"><option>Elservice / felsökning</option><option>Nyinstallation / ombyggnation</option><option>Elbilsladdare</option><option>Solceller</option><option>Smart teknik</option><option>Annat</option></select></label>'
         '<label for="f-medd">Meddelande<textarea id="f-medd" name="meddelande" required></textarea></label>'
         '<button class="btn btn-red" type="submit">Skicka</button><p class="msg" role="status"></p></form></div></section>')
body += ('<section class="sec gray" id="karta"><div class="wrap split"><div class="prose">' + head("Kontor och lager", "Blomstergatan 5, Göteborg")
         + ps("Härifrån åtar vi oss uppdrag från Falkenberg i söder till Uddevalla i norr; Ulricehamn, Göteborg, Borås och allt där emellan.")
         + '<div class="btns"><a class="btn btn-line arrow" href="https://www.google.com/maps/search/?api=1&amp;query=Blomstergatan+5+411+04+G%C3%B6teborg" target="_blank" rel="noopener">Öppna i Google Maps </a></div></div>'
         '<div class="media"><img src="img/servicebil-liseberg.jpg" alt="Bloms El &amp; Datas servicebil" loading="lazy"></div></div></section>')
PAGES["kontakt"] = page("kontakt", "Kontakt | Göteborg | Bloms El Och Data", "Kontakt Bloms El & Data, Elektriker Göteborg", body, "kontakt.html")


# ================================================================ ORTSSIDOR (stora: Hisingen, Kungsbacka, Kungälv)
def big_area(slug, place, title, desc, h1, intro, sec2_title, sec2, sec3_title, sec3, near_title, near, cta_text, extra=""):
    b = hero("team-bro.jpg", h1, intro[0], HOME_CARDS, eyebrow=f"Elektriker {place}")
    b += split("kraft-uttag.jpg", head("Bloms El & Data", f"Elektriker i {place} sedan 2008") + ps(*intro[1:]) + btns(ghost=False), alt="Röda kraftuttag")
    b += usp_section(f"Elfirma nära {place}")
    b += split("elskap.jpg", head("Service och installation", sec2_title) + sec2, bg="gray", rev=True, alt="Elskåp")
    b += services_section(place)
    b += split("butik-servicebil.jpg", head("Verksamheter", sec3_title) + sec3, alt="Servicebil utanför butiker")
    b += split("servicebil-alvsborg.jpg", head("Lokal närvaro", near_title) + near
               + '<h3 class="h3" style="margin-top:12px">ROT-avdrag för privatpersoner</h3>' + ps(rot_text()) + btns(call=False, ghost=False),
               bg="gray", rev=True, alt="Montörer vid servicebilen", media_cls="tall", badge=ROT_BADGE)
    b += view_section(f"{'på' if place == 'Hisingen' else 'i'} {place}")
    b += extra
    b += contact_cta(f"Kontakta din elektriker {'på' if place == 'Hisingen' else 'i'} {place}", cta_text)
    b += smart_band() + trust_section()
    return page(slug, title, desc, b)


def lis(items):
    return '<ul class="checklist">' + "".join(f'<li class="chk">{e(x)}</li>' for x in items) + '</ul>'


PAGES["elektriker-hisingen"] = big_area(
    "elektriker-hisingen", "Hisingen", "Elektriker Hisingen | Elfirma - Bloms El & Data",
    "Elservice i Hisingen | Nyinstallation, ombyggnation, service och rådgivning - kort sagt allt man förväntar sig av en elektriker och ofta lite till.",
    "Elektriker på Hisingen för service och elinstallationer",
    ["Söker ni elektriker på Hisingen för en fastighet, verksamhetslokal eller bostad? Bloms El & Data utför nyinstallationer, ombyggnationer, elservice och felsökning i hela Göteborgsregionen.",
     "Vi arbetar med både el och data och har gjort det sedan 2008, och kan följa ett projekt från planering och ritning till färdig installation och dokumentation. För företag och fastighetsägare innebär det att flera delar av elanläggningen kan hanteras inom samma uppdrag."],
    "Elservice på Hisingen för befintliga anläggningar",
    ps("Många elarbeten börjar med att verksamhetens behov förändras. En lokal byggs om, ytterligare utrustning ska anslutas, belysningen ska förändras eller ett återkommande fel behöver lokaliseras.",
       "Att bara åtgärda det synliga problemet är inte alltid tillräckligt. Belastning, matning, befintlig central, kablage och dokumentation kan också behöva kontrolleras innan rätt åtgärd kan bestämmas.",
       "Bloms El hjälper till med elservice, kraft och elinstallationer, både som fristående uppdrag och i samband med större förändringar."),
    "El för industri, kontor, butik och fastighet",
    ps("Hisingen rymmer industriverksamheter, kontor, handel, restauranger, flerbostadshus och bostäder. Elbehovet ser därför mycket olika ut mellan olika fastigheter. Vi arbetar bland annat med:")
    + lis(["kraft och elförsörjning", "felsökning och elservice", "belysning och ljusplanering", "datanät", "styrsystem", "nyinstallation och ombyggnation",
           "elritningar och mätprotokoll", "installationer för värme", "laddboxar och elbilsladdning"])
    + ps("För industriföretag kan arbetet exempelvis omfatta el och automation kring maskinparken. I en kommersiell fastighet ligger fokus ofta på belysning, kraft, data och anpassningar när lokaler byggs om eller får nya hyresgäster."),
    "Lokal närvaro på Hisingen och Lindholmen",
    ps("Bloms El & Data har arbetat med elinstallationer sedan 2008 och utför uppdrag i hela Göteborgsregionen. Vi har tillgång till materialdepåer både på Hisingen och Lindholmen. Det ger bra förutsättningar för service och installationsarbeten i området.",
       "Bloms El & Data är registrerat hos Elsäkerhetsverket för lågspänningsarbeten inom bland annat industri, bostäder, offentliga miljöer och elproduktionsanläggningar. Företaget är ansvarsförsäkrat och lämnar garanti på utförda arbeten."),
    "Behöver ni felsöka en befintlig installation, bygga om en lokal eller planera el för ett nytt projekt? Beskriv vad som ska göras och hur fastigheten eller verksamheten används, så kan vi gå vidare med ett lämpligt upplägg. Ring eller skicka en förfrågan, så återkommer vi normalt samma arbetsdag med bedömning och offert.",
    extra=split("portratt.jpg", head("Felsökning", "Felsökning innan problemen växer")
                + ps("Återkommande driftproblem bör undersökas istället för att tillfälligt återställas gång på gång. Säkringar som löser ut, utrustning som påverkar andra delar av anläggningen eller fel som bara uppstår under hög belastning kan kräva systematisk felsökning.",
                     "Vi går igenom installationen och försöker identifiera orsaken innan åtgärden bestäms. Samma arbetssätt är användbart när äldre elanläggningar ska byggas om. Då går det att bedöma vad som kan behållas och vilka delar som behöver förändras för den nya användningen.")
                + ps(*TRYGG[2:]), bg="gray", alt="Rustan Blom, Bloms El & Data").replace('<section class="sec', '<section id="trygg-el" class="sec', 1))

PAGES["elektriker-kungsbacka"] = big_area(
    "elektriker-kungsbacka", "Kungsbacka", "Elektriker Kungsbacka | Elfirma - Bloms El & Data",
    "Elservice i Kungsbacka | Nyinstallation, ombyggnation, service och rådgivning - kort sagt allt man förväntar sig av en elektriker och ofta lite till.",
    "Elektriker Kungsbacka, certifierad elfirma med lokal närvaro",
    ["Bloms El & Data utför elarbeten åt privatpersoner, fastighetsägare, butiker och industriföretag i Kungsbacka sedan 2008.",
     "Vi är registrerade hos Elsäkerhetsverket för lågspänningsarbeten inom bostäder, allmänna utrymmen, industri samt elproduktionsanläggningar som solceller och batterilager. Samtliga montörer har ABL- eller BB1-behörighet, alla arbeten omfattas av garanti och företaget är ansvarsförsäkrat."],
    "Elektriker Kungsbacka för privat och företag",
    ps("En behörig elektriker utfärdar elsäkerhetsintyg, dokumenterar utförda arbeten med elritningar och mätprotokoll och gör en sakkunnig bedömning av befintlig anläggning.",
       "Dokumentationen har praktiskt värde vid om- eller tillbyggnad längre fram. Vet man vad som finns bakom väggarna går arbetet snabbare och kostar mindre.",
       "Vi tar uppdrag från villaägare, bostadsrättsföreningar, hyresvärdar, restauranger, butikskedjor och industriföretag i hela Kungsbacka kommun."),
    "Trygg el i hemmet och på arbetsplatsen",
    ps("Vi arbetar långsiktigt och lägger vikt vid kundrelationer som håller över tid. Det innebär att vi levererar rätt kvalitet till rätt pris i varje uppdrag och håller oss uppdaterade med modern elteknik. En återkommande kund är den bästa referensen vi kan få, och därför lägger vi lika stor omsorg på servicebesöket i lägenheten som på totalentreprenaden.",
       "Den bästa försäkringen mot elolyckor är att anlita en certifierad elektriker i Kungsbacka. Samtliga våra montörer har ABL- eller BB1-behörighet. Nyinstallationer och reparationer åtföljs av garanti och Bloms El & Data är ansvarsförsäkrat. Allt elmaterial som används i våra installationer är CE-märkt och i övrigt av hög kvalitet.",
       "Är du osäker på tillståndet i din anläggning gör vi en sakkunnig bedömning på plats."),
    "Lokal elektriker med kort inställelsetid i Kungsbacka",
    ps("Vi har elektriker och montörer samt material som når adressen snabbt, oavsett om det gäller ett akut fel i Onsala, en villarenovering i Kullavik eller nyinstallation i Åsa.")
    + '<ul class="pills">' + "".join(f"<li>{x}</li>" for x in ["Kungsbacka centrum", "Onsala", "Kullavik", "Åsa", "Särö", "Vallda", "Fjärås", "Frillesås", "Anneberg", "Gällinge"]) + '</ul>',
    "Ring eller skicka en förfrågan via kontaktformuläret. Vi återkommer normalt samma arbetsdag med bedömning och offert.",
    extra=trygg_section())

PAGES["elektriker-kungalv"] = big_area(
    "elektriker-kungalv", "Kungälv", "Elektriker Kungälv | Elfirma - Bloms El & Data",
    "Elservice i Kungälv | Nyinstallation, ombyggnation, service och rådgivning - kort sagt allt man förväntar sig av en elektriker och ofta lite till.",
    "Elektriker i Kungälv för företag, fastigheter och bostäder",
    ["Behöver ni en elektriker i Kungälv för service, ombyggnation eller en ny installation? Bloms El & Data hjälper företag, fastighetsägare, bostadsrättsföreningar och privatpersoner med elarbeten i Kungälv och övriga Göteborgsregionen.",
     "Vi har arbetat med elinstallationer sedan 2008 och kan ta hand om hela arbetet från planering och ritning till installation, felsökning, dokumentation och kontroll."],
    "Elektriker Kungälv för privat och företag",
    ps("Ett elfel behöver inte innebära ett totalt strömavbrott för att skapa problem. Återkommande säkringsproblem, fel i belysningen, bristande dokumentation eller en elanläggning som inte längre är anpassad efter verksamhetens belastning kan skapa störningar och försvåra framtida förändringar.",
       "Vi hjälper till med elservice och elinstallationer i både befintliga och nya anläggningar. Det kan handla om felsökning, komplettering av uttag och kraftmatning, ombyggnad av elanläggningen, belysning eller installation i samband med att en lokal får en ny användning."),
    "Certifierade elinstallationer för fastigheter och olika verksamheter",
    ps("Bloms El arbetar med el och data i flera typer av miljöer:")
    + '<ul class="checklist">' + "".join(f'<li class="chk"><span><strong>{e(a)}:</strong> {e(b)}</span></li>' for a, b in [
        ("Industri och verkstad", "kraft, elinstallationer, styrsystem, felsökning och anpassningar i befintliga anläggningar."),
        ("Fastigheter och BRF", "service, belysning, gemensamma utrymmen, dokumentation och modernisering."),
        ("Butik och restaurang", "kraft, belysning, uttag, data och installationer vid ombyggnad."),
        ("Kontor", "belysning, datanät, eluttag och tekniska installationer."),
        ("Nybyggnation och renovering", "planering, installation och dokumentation av elanläggningen."),
        ("Laddning", "installation av laddboxar och laddlösningar för fastigheter, verksamheter och privatbostäder.")]) + '</ul>'
    + ps("Behöver flera delar samordnas kan vi arbeta med elinstallationen som en sammanhängande helhet istället för att hantera varje åtgärd separat."),
    "Elfirma i Kungälv med lokal närvaro",
    ps("Bloms El & Data utgår från Göteborg och arbetar i hela regionen. Vi har också tillgång till materialdepå i Kungälv. Det underlättar vid både planerade installationer och servicearbeten där material behöver kompletteras under arbetets gång.",
       "Vi är registrerade hos Elsäkerhetsverket för lågspänningsarbeten inom bland annat bostäder, allmänna och offentliga utrymmen, industri och elproduktionsanläggningar. Vi är ansvarsförsäkrade och lämnar garanti på utförda arbeten.",
       "För den som beställer elarbete handlar tryggheten även om vad som finns kvar efter avslutat arbete. Därför lägger vi stor vikt vid kontroll och dokumentation."),
    "Ring eller skicka en förfrågan via kontaktformuläret. Vi återkommer normalt samma arbetsdag med bedömning och offert.",
    extra=trygg_section() + split("dokumentation.jpg", head("Dokumentation", "Från planering till dokumenterad installation")
                                  + ps("Ett bra installationsunderlag förenklar både själva arbetet och framtida service. Därför arbetar vi med mer än själva montaget.",
                                       "Vi kan hjälpa till med planering, elritningar, mätprotokoll och elsäkerhetsintyg. Dokumentationen gör det enklare att se hur anläggningen är uppbyggd när nästa ombyggnad, felsökning eller utökning ska genomföras.",
                                       "Vid större förändringar går vi igenom förutsättningarna innan arbetet startar. Det ger bättre kontroll över omfattning, material och de installationer som påverkas."),
                                  alt="Elektriker dokumenterar en installation"))


# ================================================================ ORTSSIDOR (små: Partille, Mölndal, Västra Frölunda)
SMALL_CARDS = [("varme.jpg", "Värme", "golvvarme.html"), ("servicebil-liseberg.jpg", "Elservice", "elservice-felsokning.html"),
               ("kraft.jpg", "Kraft", "kraft.html"), ("laddbox.jpg", "Elbilsladdare", "elbilsladdare.html"),
               ("dokumentation.jpg", "Dokumentation", "dokumentation.html"), ("solceller.jpg", "Solceller", "solceller.html")]


def small_area(slug, place, title, desc, hero_img, intro, services, doing, also, pos="center"):
    b = hero(hero_img, f"Elektriker i {place}", intro, HOME_CARDS, eyebrow="Bloms El & Data", pos=pos)
    b += ('<section class="sec"><div class="wrap split"><div class="prose">' + head("Våra tjänster", f"Det här gör vi i {place}")
          + '<div class="btns" style="margin-top:8px"><a class="btn btn-red arrow" href="kontakt.html">Kontakta oss </a></div></div>'
          + '<ul class="pills">' + "".join(f"<li>{e(s)}</li>" for s in services) + '</ul></div></section>')
    b += ('<section class="sec gray"><div class="wrap"><div class="sec-head"><div class="prose">' + head("En del av det vi gör", "Erfarenhet från villa till industri") + ps(doing) + '</div></div>'
          + '<div class="grid g3">' + "".join(img_card(i, t, h) for i, t, h in SMALL_CARDS) + '</div></div></section>')
    b += split("servicebil-alvsborg.jpg", head("Lokal närvaro", f"Vi finns i {place}")
               + ps(also, "Vi åtar oss uppdrag från Falkenberg i söder till Uddevalla i norr; Ulricehamn, Göteborg, Borås och allt där emellan.",
                    "Kontakta oss gärna så pratar vi mer om hur vi kan hjälpa er med smarta ellösningar. Och om hur du kan få trygg, säker el av erfarna elyrkesmän på hemmaplan.")
               + btns(ghost=False), alt="Montörer vid servicebilen", media_cls="tall", badge=ROT_BADGE)
    b += trust_section()
    return page(slug, title, desc, b)


PAGES["elektriker-i-partille"] = small_area(
    "elektriker-i-partille", "Partille", "Elektriker i Partille | Bloms El & Data", "Elektriker och elinstallatör i Partille med lång och gedigen erfarenhet.",
    "kabelrulle.jpg",
    "Vi erbjuder de allra flesta tjänster inom el och data, och är förmodligen en av de mest erfarna elfirmorna i Partille med omnejd. Med servicekänsla och helhetskänsla tar vi ansvar för ditt projekt och månar om att du som kund blir nöjd. Vi underhåller era fastigheter; industri, butik, restaurang eller hemmiljö.",
    ["Belysning", "Datanät", "Solceller", "Elsäkerhetsintyg", "Värme", "Ritning", "Styrsystem", "Laddboxar", "Industri"],
    "Vi gör och har gjort det mesta elektriker gör; nybyggnation, renovering och solceller. Vi gör villael, byter gamla system, dokumenterar och monterar elbilsladdare. Vi gör jobb för privata villaägare, bostadsrättsföreningar, småföretagare och stora byggbolag. Och allt där emellan.",
    "Men vi finns också i Göteborg och Borås.")
PAGES["elektriker-molndal"] = small_area(
    "elektriker-molndal", "Mölndal", "Elektriker i Mölndal | Bloms El & Data", "Elektriker och elinstallatör i Mölndal med lång och gedigen erfarenhet.",
    "molndal.jpg",
    "Vi är en komplett partner inom el och data i Mölndal och närliggande områden, med många års erfarenhet som grund. Vårt mål är att alltid leverera högsta kvalitet och att säkerställa att du som kund blir mer än nöjd, oavsett om det gäller fastigheter inom industri, butik, restaurang eller hemmamiljö.",
    ["Belysning", "Datanät", "Nybyggnation", "Elsäkerhetsintyg", "Värme", "Ritning", "Styrsystem", "Solceller", "Industri"],
    "Vi har lång erfarenhet av allt som hör en elektrikers arbete till, från installation i nyproduktion och renoveringsprojekt till datanät, solcellsanläggningar och smart hemel. Vi utför elarbeten i hus, butikslokaler och fabriker, byter ut äldre elsystem, dokumenterar installationer och installerar laddstationer för elbilar. Våra kunder är allt från privata villaägare och bostadsrättsföreningar till småföretag och stora byggentreprenörer. Med oss får du en elektriker som kombinerar professionalism med personligt engagemang för varje projekt.",
    "Men vi finns också i Göteborg och Borås.")
PAGES["elektriker-vastra-frolunda"] = small_area(
    "elektriker-vastra-frolunda", "Västra Frölunda", "Elektriker i Västra Frölunda | Bloms El & Data", "Erfaren elektriker och elinstallatör i Västra Frölunda. Lång erfarenhet och mycket goda referenser.",
    "butik-servicebil.jpg",
    "Bloms El är din elpartner i Västra Frölunda och omkringliggande områden, med lång erfarenhet och gedigen kompetens i bagaget. Oavsett om det handlar om industrifastigheter, butiker, restauranger eller privata bostäder ser vi till att hitta lösningar som passar dina behov.",
    ["Belysning", "Datanät", "Nybyggnation", "Elsäkerhetsintyg", "Värme", "Ritning", "Styrsystem", "Solceller", "Industri"],
    "Med många års erfarenhet som elektriker hjälper vi dig med allt från nyinstallationer och renoveringsprojekt till moderna lösningar som datanät, solcellsanläggningar och smarta hem. Vi arbetar med elinstallationer i bostäder, butiker och industrilokaler. Vi uppgraderar äldre elsystem, dokumenterar installationer och sätter upp laddstationer för elbilar. Våra kunder är privatpersoner och bostadsrättsföreningar, småföretag, lantbrukare, kommuner och stora byggföretag.",
    "Men vi finns naturligtvis också i Göteborg och Kungsbacka.")

# ================================================================ COOKIEPOLICY
doc = [
    ("p", "Vi använder kakor, så kallade cookies, på vår hemsida. Genom att inte stänga av cookies i din webbläsare och fortsätta använda webbplatsen samtycker du till vår användning av cookies i enlighet med denna cookiepolicy."),
    ("p", "Du kan ändra ditt val genom att när som helst ändra din webbläsares inställningar. Om du inaktiverar cookies kan det negativt påverka din användning av vår webbplats."),
    ("p", "Besökare av en webbplats som använder cookies ska få information om:"),
    ("ul", ["att webbplatsen innehåller cookies,", "vad dessa cookies används till,", "vem som använder informationen, och", "hur cookies kan undvikas."]),
    ("p", "Dessutom ska du som besökare samtycka till användningen av cookies, till exempel genom din webbläsares inställningar, men även ges möjlighet att vägra cookies."),
    ("h", "Vad är cookies och vad används de till?"),
    ("p", "Cookies är små textfiler som sänds till och lagras på din enhet (mobil, dator eller surfplatta) och som är vanligt förekommande på internet. En del är nödvändiga för att du ska kunna använda webbplatsens funktionalitet fullt ut, medan andra används för att förbättra din användarupplevelse och underlätta navigation på webbplatsen."),
    ("p", "Det finns två typer av cookies; permanenta och temporära (så kallade sessionscookies). Permanenta cookies lagras som en fil på din enhet under en längre period för att kunna anpassa webbplatsen efter dina önskemål, val och intressen. De används till exempel vid funktioner som talar om vad som är nytt sedan du senast besökte webbplatsen. När utgångsdatumet passerats raderas cookien när du återvänder till den webbplats som skapade den. Sessionscookies placeras temporärt på din dator när du besöker webbplatsen och skickas mellan din dator och servern under tiden du besöker webbplatsen, och raderas när du stänger din webbläsare. Den används exempelvis för att hålla reda på vilket språk du valt."),
    ("h", "Några exempel på vad vi använder cookies till"),
    ("ul", ["Följa upp trafiken genom statistik för att kunna förbättra webbplatsen och för att lära oss mer om olika målgrupper. Några av våra cookies som används för statistik är tredjepartskakor, till exempel Google Analytics.", "Hålla reda på tidigare besökta sidor."]),
    ("h", "Om du vill undvika cookies"),
    ("p", "Cookies används inte för att skada eller förstöra din dator och de flesta webbläsare accepterar automatiskt cookies. Om du trots allt inte vill tillåta cookies kan du vägra cookies i din webbläsares inställningar och radera cookies som finns sparade på din hårddisk. Du kan även ställa in din webbläsare så att den meddelar dig när den tar emot en cookie. På så vis har du möjlighet att acceptera eller avvisa cookien. Mer information om detta får du från tillverkaren av din webbläsare. Du hittar även mer information på youronlinechoices.eu."),
    ("p", "Vissa tredjepartscookies kontrollerar dock inte Bloms El & Data. Dessa kan endast stängas av på respektive webbplats och i enlighet med de instruktioner som framgår där. Nekar du cookies kan det medföra att de digitala tjänsterna inte fungerar som avsett."),
    ("h", "Varför använder vi cookies?"),
    ("p", "Genom att använda cookies känner vår webbplats igen din enhet när du besöker oss igen. Bloms El & Data använder även cookies för utvärdering av sök- och användarbeteenden inom webbplatsen, för att vidareutveckla våra digitala tjänster. Syftet är att optimera användarupplevelsen samt föra statistik."),
    ("h", "Samtycke till användning av cookies"),
    ("p", "Du samtycker till Bloms El & Datas användning av cookies i enlighet med denna cookiepolicy genom att fortsätta använda webbplatsen och ha webbläsaren inställd på att tillåta cookies."),
    ("h", "Kontakta oss"),
]
d = ""
for kind, val in doc:
    d += {"p": lambda v: f"<p>{e(v)}</p>", "h": lambda v: f"<h2>{e(v)}</h2>",
          "ul": lambda v: "<ul>" + "".join(f"<li>{e(x)}</li>" for x in v) + "</ul>"}[kind](val)
d += '<p>Har du frågor och kommentarer om vår cookiepolicy är du välkommen att kontakta oss. Du hittar kontaktuppgifter <a href="kontakt.html" style="color:var(--red);text-decoration:underline">här</a>.</p>'
PAGES["cookiepolicy"] = page("cookiepolicy", "Cookiepolicy | Bloms El & Data", "Sidan beskriver hur och varför Bloms El & Datas hemsida använder cookies.",
                             hero("team-bro.jpg", "Cookiepolicy", None, None, eyebrow="Bloms El & Data", buttons="")
                             + f'<section class="sec"><div class="wrap"><div class="prose doc">{d}</div></div></section>')


# ================================================================ TJÄNSTESIDOR OCH INFOSIDOR (pages_extra.py)
EXIST = {"tjanster": ("kanal.jpg", "Alla tjänster"), "smart-teknik": ("smart-hem.jpg", "Smart Teknik"), "solceller": ("solceller.jpg", "Solceller"),
         "elbilsladdare": ("laddbox.jpg", "Elbilsladdare"), "skattereduktion": ("kabelrulle.jpg", "ROT och Grön teknik"),
         "kontakt": ("utebelysning.jpg", "Kontakt"), "elektriker-hisingen": ("team-bro.jpg", "Elektriker Hisingen")}
EXTRA_BY = {x["slug"]: x for x in EXTRA}


def faq_html(items):
    return '<div class="faq">' + "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in items) + '</div>'


def service_page(d):
    cards = [img_card(i, t, f"#{a}") for i, t, a in d["cards"]]
    b = hero(d["hero"], d["h1"], d["lead"], cards, eyebrow=d["eyebrow"], pos=d.get("pos", "center"))
    k = 0
    for sec in d["sections"]:
        bg = "gray" if k % 2 else ""
        link = f'<div class="btns"><a class="btn btn-line arrow" href="{sec["link"][0]}">{e(sec["link"][1])} </a></div>' if sec.get("link") else ""
        if sec["kind"] == "split":
            html = split(sec["img"], head(sec["eyebrow"], sec["title"]) + ps(*sec["paras"]) + link, rev=k % 2 == 1, bg=bg,
                         alt=sec["title"], media_cls=sec.get("media", ""))
        elif sec["kind"] == "items":
            html = (f'<section class="sec {bg}"><div class="wrap"><div class="sec-head"><div class="prose">{head(sec["eyebrow"], sec["title"])}</div></div>'
                    '<div class="grid g3">' + "".join(f'<div class="feature"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in sec["items"]) + '</div></div></section>')
        else:
            html = (f'<section class="sec {bg}"><div class="wrap split" style="align-items:start"><div class="prose">{head(sec["eyebrow"], sec["title"])}{btns(ghost=False)}</div>'
                    '<ul class="checklist cols">' + "".join(f'<li class="chk">{e(x)}</li>' for x in sec["list"]) + '</ul></div></section>')
        b += html.replace('<section class="sec', f'<section id="{sec["id"]}" class="sec', 1)
        k += 1
    if d.get("faq_groups"):
        for gid, title, items in d["faq_groups"]:
            b += (f'<section id="{gid}" class="sec {"gray" if k % 2 else ""}"><div class="wrap split" style="align-items:start">'
                  f'<div class="prose">{head("Vanliga frågor", title)}</div>{faq_html(items)}</div></section>')
            k += 1
    elif d["sections"] and d["slug"] != "om-oss":
        b += ('<section class="sec gray" id="sa-gar-det-till"><div class="wrap"><div class="sec-head"><div class="prose">' + head("Så går det till", "Från första kontakt till färdig installation") + '</div></div>'
              '<ol class="steps">' + "".join(f'<li><b>{e(t)}</b><p>{e(x)}</p></li>' for t, x in STEPS_STANDARD) + '</ol></div></section>')
    if d.get("faq"):
        b += ('<section class="sec" id="fragor"><div class="wrap split" style="align-items:start"><div class="prose">' + head("Frågor och svar", "Vanliga frågor")
              + ps("Hittar du inte svaret? Ring eller mejla oss.") + '<div class="btns"><a class="btn btn-line arrow" href="vanliga-fragor.html">Fler frågor och svar </a></div></div>'
              + faq_html(d["faq"]) + '</div></section>')
    rel = []
    for r in d.get("related", []):
        img, name = (EXTRA_BY[r]["hero"], EXTRA_BY[r]["name"]) if r in EXTRA_BY else EXIST[r]
        rel.append(img_card(img, name, f"{r}.html"))
    if rel:
        b += ('<section class="sec gray"><div class="wrap"><div class="sec-head"><div class="prose">' + head("Mer från Bloms El & Data", "Relaterade tjänster") + '</div>'
              '<a class="btn btn-line arrow" href="tjanster.html">Alla tjänster </a></div><div class="grid g4">' + "".join(rel) + '</div></div></section>')
    b += contact_cta(*d["cta"]) + trust_section()
    active = {"tjanster": "tjanster.html", "elbilsladdare": "elbilsladdare.html"}.get(d.get("parent"))
    return page(d["slug"], d["title"], d["desc"], b, active)


for d in EXTRA:
    PAGES[d["slug"]] = service_page(d)

for slug, html in PAGES.items():
    (OUT / f"{slug}.html").write_text(html, encoding="utf-8")

# Manifest och tomt innehåll för adminpanelen
import json, re
manifest = {
    "pages": [{"slug": slug, "file": f"{slug}.html",
               "name": {"index": "Startsida", "cookiepolicy": "Cookiepolicy", **{h[:-5]: t for h, t in NAV[1:]},
                        **{h[:-5]: f"Elektriker {t}" for h, t in AREAS}, **{x["slug"]: x["name"] for x in EXTRA}}.get(slug, slug),
               "title": re.search(r"<title>(.*?)</title>", html).group(1).replace("&amp;", "&"),
               "description": re.search(r'<meta name="description" content="(.*?)">', html).group(1).replace("&amp;", "&")}
              for slug, html in PAGES.items()],
    "images": sorted(f"img/{p.relative_to(OUT / 'img').as_posix()}" for p in (OUT / "img").rglob("*") if p.is_file()),
    "heroes": [{"id": sid, "name": name} for sid, name, _ in gallery_parts()[1]],
}
(OUT / "assets" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
if not (OUT / "content.json").exists():
    (OUT / "content.json").write_text(json.dumps({"version": 1, "updated": None, "text": {}, "link": {}, "img": {}, "meta": {},
                                                  "hero": {}, "settings": {}}, indent=1), encoding="utf-8")
print(f"{len(PAGES)} sidor byggda i {OUT}")
