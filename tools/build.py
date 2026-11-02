"""Builds every page of alauddinstudio.com from data/games.json: the studio home, the games and the apps.

Run after any change to data/games.json:  python tools/build.py
"""
import hashlib
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "games.json").read_text(encoding="utf-8"))
SITE = DATA["site"]
GAMES = DATA["games"]
APPS = DATA["apps"]
COMPANY = SITE["company"]
BASE = SITE["policy_base"]
STUDIO_URL = BASE
# The studio home shows these games first; the rest keep their order after them.
STUDIO_GAMES = sorted(GAMES, key=lambda g: SITE["studio_first"].index(g["slug"]) if g["slug"] in SITE["studio_first"] else len(GAMES))
E = html.escape
# Changes whenever the CSS/JS changes, so browsers never mix a new page with an old cached file.
VER = hashlib.md5(b"".join((ROOT / "assets" / f).read_bytes() for f in ("style.css", "app.js"))).hexdigest()[:8]

STATUS = {
    "live": ("On Google Play", "live"),
    "testing": ("In testing", "testing"),
    "soon": ("Coming soon", "soon"),
}

PLAY_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 2.5v19l10-9.5z" fill="#fff" opacity=".95"/>'
    '<path d="M14 12l3.2 3.1L21 13c.9-.5.9-1.5 0-2l-3.8-2.1z" fill="#fff" opacity=".7"/>'
    '<path d="M4 2.5L14 12l3.2-3.1L5.4 2.2c-.5-.3-1-.2-1.4.3z" fill="#fff" opacity=".85"/>'
    '<path d="M4 21.5c.4.5.9.6 1.4.3l11.8-6.7L14 12z" fill="#fff" opacity=".6"/></svg>'
)
CHROME_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="#DB4437"/>'
    '<path d="M20.66 7A10 10 0 0 1 12 22l4.33-7.5A5 5 0 0 0 16.33 9.5 5 5 0 0 0 12 7z" fill="#FFCD40"/>'
    '<path d="M12 22A10 10 0 0 1 3.34 7l4.33 7.5A5 5 0 0 0 12 17z" fill="#0F9D58"/>'
    '<circle cx="12" cy="12" r="4.2" fill="#fff"/><circle cx="12" cy="12" r="3.3" fill="#4285F4"/></svg>'
)


def play_url(g):
    return "https://play.google.com/store/apps/details?id=" + g["pkg"]


def policy(g, page):
    return SITE["policy_base"] + g["policy"] + page + ".html"


def ld(data):
    return f'\n  <script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def write_seo_files(folder, base, paths):
    (folder / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n", encoding="utf-8", newline="\n")
    urls = "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in paths)
    (folder / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n',
        encoding="utf-8", newline="\n",
    )
    print("built robots.txt and sitemap.xml for", base)


def head(title, desc, image, url, prefix, color, extra="", favicon="favicon.png"):
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8">
  <script>document.documentElement.className = "js";</script>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{E(title)}</title>
  <meta name="description" content="{E(desc)}">
  <meta name="theme-color" content="{color}">
  <meta property="og:title" content="{E(title)}">
  <meta property="og:description" content="{E(desc)}">
  <meta property="og:image" content="{image}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="{prefix}assets/{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/style.css?v={VER}">{extra}
</head>"""


def backdrop():
    return """  <div class="sky" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>
  <div class="particles" aria-hidden="true"></div>"""


def studio_mark(prefix=""):
    return f'<img src="{prefix}assets/logo-icon.svg" alt="" width="36" height="36">'


def topbar(prefix, right, name=COMPANY, mark=None):
    """Every page shows the studio's logo and name, linking to the studio home at prefix."""
    mark = mark or studio_mark(prefix)
    return f"""    <header class="topbar">
      <a class="brand" href="{prefix or './'}"><span class="brand-mark">{mark}</span><span>{name}</span></a>
      <nav class="nav">{right}</nav>
    </header>"""


def badge(g):
    label, cls = STATUS[g["status"]]
    return f'<span class="badge {cls}"><span class="dot"></span>{label}</span>'


def footer(prefix, links, name=COMPANY, mark=None, line="Small, gentle games made with love.", made="", home=None):
    mark = mark or studio_mark(prefix)
    return f"""  <footer class="footer">
    <div class="wrap">
      <div class="foot-top">
        <a class="brand" href="{home or prefix or './'}"><span class="brand-mark">{mark}</span><span>{name}</span></a>
        <p>{line}</p>
      </div>
      {links}{made}
      <p class="copy">© 2026 <a href="{STUDIO_URL}">{COMPANY}</a> · <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
    </div>
  </footer>
  <script src="{prefix}assets/app.js?v={VER}"></script>
</body>
</html>
"""


def build_home():
    """The games page, /games/; the site's root is the studio home."""
    cards = []
    for i, g in enumerate(GAMES):
        cards.append(f"""      <a class="game-card reveal" href="../{g['slug']}/" style="--c1:{g['color']};--c2:{g['color2']};--d:{i * 0.07:.2f}s">
        <div class="art"><img src="../assets/icons/{g['slug']}.png" alt="{E(g['name'])} icon" loading="lazy" width="256" height="256">{badge(g)}</div>
        <h3>{E(g['name'])}</h3>
        <p>{E(g['tagline'])}</p>
        <span class="go">Explore →</span>
      </a>""")

    collage = "".join(
        f'<img class="ci ci{i}" src="../assets/icons/{g["slug"]}.png" alt="{E(g["name"])}" width="256" height="256">'
        for i, g in enumerate(GAMES[:6])
    )
    testing = [g for g in GAMES if g["status"] == "testing"]
    tester_band = ""
    if testing:
        chips = "".join(
            f'<a class="chip" href="../{g["slug"]}/#test" style="--c1:{g["color"]}"><img src="../assets/icons/{g["slug"]}.png" alt="" width="28" height="28">{E(g["name"])}</a>'
            for g in testing
        )
        tester_band = f"""
    <section class="band reveal" id="testers">
      <div class="band-inner">
        <span class="eyebrow">Early access</span>
        <h2>Play before everyone else</h2>
        <p>Some of our games are still in closed testing on Google Play. Join as a tester, play for free and help us make them even cozier.</p>
        <div class="chips">{chips}</div>
      </div>
    </section>"""

    links = "".join(
        f'<div><b>{E(g["name"])}</b><a href="{policy(g, "privacy")}">Privacy</a><a href="{policy(g, "support")}">Support</a></div>'
        for g in GAMES
    )
    page = f"""{head(f"Cozy games by {COMPANY}", "Small, gentle idle games with cute critters. Bees, bakeries, blossoms, fluffy sheep and more.", BASE + "assets/og-games.png", BASE + "games/", "../", "#FFF6E6")}
<body data-particles='["🐝","🌸","🥐","🫧","❄️","🧶","🍃","✨"]'>
{backdrop()}
  <div class="wrap">
{topbar("../", '<a href="#games">Games</a><a href="#why">About</a><a href="#contact">Contact</a>')}

    <section class="hero home-hero">
      <div class="hero-text">
        <span class="pill"><span class="dot"></span> {len(GAMES)} games and counting</span>
        <h1>Little <span class="rainbow">cozy</span> worlds</h1>
        <p>We make small, gentle games you can enjoy in a few minutes a day. Bees, bakeries, blossoms, fluffy sheep and more on the way.</p>
        <div class="cta-row">
          <a class="btn" href="#games">See the games</a>
          {'<a class="btn ghost" href="#testers">Become a tester</a>' if testing else ''}
        </div>
      </div>
      <div class="collage" aria-hidden="true">{collage}</div>
    </section>

    <section id="games">
      <div class="section-head reveal"><span class="eyebrow">Our games</span><h2>Pick a cozy world</h2></div>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </section>

    <section class="why" id="why">
      <div class="section-head reveal"><span class="eyebrow">Why you'll love them</span><h2>Cozy by design</h2></div>
      <div class="why-grid">
        <div class="why-card reveal" style="--d:0s"><span class="why-ic">📴</span><b>Plays offline</b><span>No internet needed. Play on the bus, in bed, anywhere.</span></div>
        <div class="why-card reveal" style="--d:.07s"><span class="why-ic">🤗</span><b>No stress, ever</b><span>No timers that punish you. Nobody leaves angry.</span></div>
        <div class="why-card reveal" style="--d:.14s"><span class="why-ic">💤</span><b>Grows while you rest</b><span>Your farm, shop or salon keeps working while you're away.</span></div>
        <div class="why-card reveal" style="--d:.21s"><span class="why-ic">🎨</span><b>Made with love</b><span>Cute critters, soft art and gentle music made just for each game.</span></div>
      </div>
    </section>
{tester_band}

    <section class="contact reveal" id="contact">
      <span class="why-ic big">💌</span>
      <h2>Say hello</h2>
      <p>Found a bug, have an idea, or just want to tell us which critter you love most? We read every message.</p>
      <a class="btn" href="mailto:{SITE['email']}">Email us</a>
    </section>
  </div>
{footer("../", '<div class="foot-links">' + links + '</div>')}"""
    out = ROOT / "games" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("built", out.relative_to(ROOT))


def build_game(g):
    slug = g["slug"]
    status = g["status"]
    others = [o for o in GAMES if o is not g]

    if status == "live":
        cta = f'<a class="btn" href="{play_url(g)}" target="_blank" rel="noopener">{PLAY_ICON} Get it on Google Play</a>'
    elif status == "testing":
        cta = '<a class="btn" href="#test">✨ Become a tester</a>'
    else:
        cta = '<span class="btn ghost disabled">🌱 Coming soon</span>'
    more = '<a class="btn ghost" href="#about">What\'s inside</a>'

    if g.get("video"):
        # the store preview video, playing with its sound in the phone (app.js)
        visual = (
            f'<div class="phone has-video"><video src="../assets/video/{slug}.mp4" poster="../assets/video/{slug}.jpg" '
            f'autoplay loop playsinline preload="auto" aria-label="{E(g["name"])} gameplay video"></video>'
            '<button class="sound" type="button" aria-label="Turn sound off">🔊</button></div>'
        )
    elif g["shots"]:
        visual = f"""<div class="phone"><img src="../assets/shots/{slug}-1.jpg" alt="{E(g['name'])} screenshot" width="432" height="768"></div>"""
    else:
        visual = f'<div class="icon-stage big"><div class="ring"></div><img src="../assets/icons/{slug}.png" alt="" width="256" height="256"></div>'
    if g["shots"]:
        shots = "".join(
            f'<img src="../assets/shots/{slug}-{i}.jpg" data-big="../assets/shots/{slug}-{i}@2.jpg" alt="{E(g["name"])} screenshot {i}" loading="lazy" width="432" height="768">'
            for i in range(1, g["shots"] + 1)
        )
        gallery = f"""
    <section class="gallery reveal" aria-label="Screenshots">
      <button class="arrow prev" type="button" aria-label="Previous screenshots">‹</button>
      <div class="shots" style="--n:{g['shots']}">{shots}</div>
      <button class="arrow next" type="button" aria-label="Next screenshots">›</button>
    </section>"""
    else:
        gallery = ""

    features = "".join(
        f'<div class="feat reveal" style="--d:{i * 0.07:.2f}s"><span class="feat-ic">{ic}</span><b>{E(t)}</b><span>{E(x)}</span></div>'
        for i, (ic, t, x) in enumerate(g["features"])
    )

    inapp = tester = ""
    if status == "testing":
        inapp = f"""
    <div class="inapp" id="inapp">
      <b>Open this page in Chrome</b>
      <p>Google Play sign-in doesn't work inside Messenger or Facebook.</p>
      <a class="btn light" id="chrome" href="#">{CHROME_ICON} Open in Chrome</a>
      <div class="ios-hint">Tap <b>•••</b> at the top, then <b>Open in browser</b>.</div>
    </div>"""
        tester = f"""
    <section class="tester" id="test">
      <div class="section-head reveal"><span class="eyebrow">Closed testing</span><h2>Become a tester</h2><p>Two quick steps. Thank you for helping! 💛</p></div>
      <div class="steps">
        <div class="step reveal" id="step-optin">
          <div class="step-head">
            <span class="num"><span>1</span></span>
            <div><h3>Join the test</h3><div class="sub">Opens Google Play. Tap <b>"Become a tester"</b>.</div></div>
          </div>
          <a class="btn" id="optin" href="https://play.google.com/apps/testing/{g['pkg']}" target="_blank" rel="noopener">✨ Join the test</a>
        </div>
        <div class="step reveal" id="step-install">
          <div class="step-head">
            <span class="num"><span>2</span></span>
            <div><h3>Install from Google Play</h3><div class="sub">Opens the game in the Play Store app.</div></div>
          </div>
          <a class="btn" id="install" href="{play_url(g)}" target="_blank" rel="noopener">{PLAY_ICON} Install on Google Play</a>
        </div>
      </div>
      <div class="notes reveal">
        <h3>A few small things</h3>
        <ul>
          <li><span class="ic">📧</span><span>Stay signed in with the <b>same Gmail</b> you gave us.</span></li>
          <li><span class="ic">🔄</span><span>See <b>"Item not found"</b>? Switch to that Gmail in the Play Store (tap your profile picture).</span></li>
          <li><span class="ic">📅</span><span>Please <b>keep the game installed for 14 days</b>. It really helps!</span></li>
          <li><span class="ic">🙏</span><span>Please <b>don't tap "Leave"</b> on the test page for at least 14 days. It helps the game launch on Google Play.</span></li>
        </ul>
      </div>
      <button class="btn ghost" id="share" type="button">🔗 Share this page</button>
    </section>"""

    more_games = "".join(
        f'<a class="mini" href="../{o["slug"]}/" style="--c1:{o["color"]}"><img src="../assets/icons/{o["slug"]}.png" alt="" loading="lazy" width="256" height="256"><span>{E(o["name"])}</span></a>'
        for o in others
    )
    links = (
        f'<div class="foot-links one"><div><b>{E(g["name"])}</b>'
        f'<a href="{policy(g, "privacy")}">Privacy Policy</a><a href="{policy(g, "support")}">Support</a></div></div>'
    )
    particles = json.dumps(g["particles"], ensure_ascii=False)
    style = f'\n  <style>:root {{ --c1: {g["color"]}; --c2: {g["color2"]}; }}</style>'
    desc = g["tagline"] + (" Join the closed test on Google Play." if status == "testing" else "")
    style += ld({
        "@context": "https://schema.org", "@type": "VideoGame", "name": g["title"], "description": g["intro"],
        "url": BASE + slug + "/", "image": BASE + "assets/icons/" + slug + ".png", "applicationCategory": "Game",
        "operatingSystem": "Android, iOS", "publisher": {"@type": "Organization", "name": COMPANY, "url": STUDIO_URL},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    })

    page = f"""{head(g["title"], desc, BASE + "assets/icons/" + slug + ".png", BASE + slug + "/", "../", g["color"], style)}
<body data-game="{slug}" data-status="{status}" data-particles='{particles}'>
{backdrop()}
  <div class="wrap">
{topbar("../", '<a href="../games/#games">All games</a>')}
{inapp}
    <section class="hero game-hero">
      <div class="hero-text">
        <div class="title-row"><img class="app-icon" src="../assets/icons/{slug}.png" alt="" width="256" height="256">{badge(g)}</div>
        <h1>{E(g['name'])}</h1>
        <p>{E(g['tagline'])}</p>
        <div class="cta-row">{cta}{more}</div>
      </div>
      <div class="hero-visual">{visual}</div>
    </section>
{gallery}
    <section class="about" id="about">
      <div class="section-head reveal"><span class="eyebrow">What's inside</span><h2>A cozy little story</h2><p>{E(g['intro'])}</p></div>
      <div class="feats">{features}</div>
    </section>
{tester}
    <section class="more">
      <div class="section-head reveal"><span class="eyebrow">More from {COMPANY}</span><h2>Other cozy worlds</h2></div>
      <div class="minis">{more_games}</div>
    </section>
  </div>
{footer("../", links)}"""
    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("built", out.relative_to(ROOT))


def studio_card(g, href, icon, i, highlights):
    """A live game or app sends people straight to Google Play; the rest open their own page as Coming soon."""
    live = g["status"] == "live"
    target = f'{play_url(g)}" target="_blank" rel="noopener' if live else href
    state = badge(g) if live else badge({"status": "soon"})
    label = STATUS[g["status"] if live else "soon"][0]
    chips = "".join(f"<li>{E(h)}</li>" for h in highlights)
    return f"""      <a class="game-card reveal" href="{target}" style="--c1:{g['color']};--c2:{g['color2']};--d:{i * 0.07:.2f}s">
        <div class="art"><img src="{icon}" alt="{E(g['name'])} icon" loading="lazy" width="256" height="256">{state}</div>
        <h3 data-status="{E(label)}">{E(g['name'])}</h3>
        <p>{E(g['tagline'])}</p>
        <ul class="highlights">{chips}</ul>
        <span class="go">{"Get it on Google Play" if live else "Explore"} →</span>
      </a>"""


def build_studio():
    """The company home page, the site's root."""
    game_cards = [
        studio_card(g, f"{g['slug']}/", f"assets/icons/{g['slug']}.png", i, [f"{f[0]} {f[1]}" for f in g["features"][:3]])
        for i, g in enumerate(STUDIO_GAMES)
    ]
    app_cards = [studio_card(a, f"{a['slug']}/", f"{a['slug']}/icon.png", i, a["highlights"]) for i, a in enumerate(APPS)]
    any_live = any(g["status"] == "live" for g in GAMES + APPS)
    store_note = "Find them on Google Play, with more on the way." if any_live else "Coming soon to Google Play and the App Store."
    icons = [(f"assets/icons/{g['slug']}.png", g["name"]) for g in GAMES[:4]] + [(f"{a['slug']}/icon.png", a["name"]) for a in APPS[:2]]
    collage = "".join(f'<img class="ci ci{i}" src="{src}" alt="{E(name)}" width="256" height="256">' for i, (src, name) in enumerate(icons))
    legal = "".join(
        f'<div><b>{E(g["name"])}</b><a href="{g["policy"]}privacy.html">Privacy</a><a href="{g["policy"]}support.html">Support</a></div>'
        for g in STUDIO_GAMES
    ) + "".join(
        f'<div><b>{E(a["name"])}</b><a href="{a["slug"]}/privacy.html">Privacy</a><a href="{a["slug"]}/">Support</a></div>'
        for a in APPS
    )
    game_links = "".join(f'<a href="{g["slug"]}/">{E(g["name"])}</a>' for g in STUDIO_GAMES)
    app_links = "".join(f'<a href="{a["slug"]}/">{E(a["name"])}</a>' for a in APPS)
    social = "".join(f'<a href="{url}" target="_blank" rel="noopener">{E(label)}</a>' for label, url in SITE["social"]["links"])
    links = f"""<div class="foot-cols">
        <div><b>Games</b>{game_links}</div>
        <div><b>Apps</b>{app_links}</div>
        <div><b>Studio</b><a href="#about">About us</a><a href="#contact">Contact</a></div>
        <div><b>{E(SITE["social"]["title"])}</b>{social}</div>
      </div>
      <details class="legal"><summary>Privacy and support</summary><div class="legal-rows">{legal}</div></details>"""
    desc = "Alauddin Studio makes cozy games and useful apps for Android and iPhone."
    extra = '\n  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">' + ld({
        "@context": "https://schema.org", "@type": "Organization", "name": COMPANY, "url": STUDIO_URL,
        "logo": STUDIO_URL + "assets/logo-512.png", "email": SITE["email"],
    })
    page = f"""{head(COMPANY + ": cozy games and useful apps", desc, STUDIO_URL + "assets/og.png", STUDIO_URL, "", "#EEF5FF", extra)}
<body class="studio">
{backdrop()}
  <div class="wrap">
{topbar("", '<a href="#games">Games</a><a href="#apps">Apps</a><a href="#contact">Contact</a>', COMPANY, studio_mark())}

    <section class="hero home-hero studio-hero">
      <div class="hero-text">
        <span class="pill"><span class="dot"></span> Little ideas, a touch of magic</span>
        <h1>Games and apps, made with <span class="rainbow">care</span></h1>
        <p>{COMPANY} makes cozy games and useful apps for Android and iPhone.</p>
        <div class="cta-row">
          <a class="btn" href="#games">See the games</a>
          <a class="btn ghost" href="#apps">See the apps</a>
        </div>
      </div>
      <div class="collage" aria-hidden="true">{collage}</div>
    </section>

    <section id="games">
      <div class="section-head reveal"><span class="eyebrow">Our games</span><h2>Cozy worlds to relax in</h2><p>Gentle idle and merge games you can enjoy at your own pace. {store_note}</p></div>
      <div class="grid">
{chr(10).join(game_cards)}
      </div>
    </section>

    <section id="apps">
      <div class="section-head reveal"><span class="eyebrow">Our apps</span><h2>Useful little helpers</h2><p>Simple apps that each solve one everyday problem.</p></div>
      <div class="grid center">
{chr(10).join(app_cards)}
      </div>
    </section>

    <section class="why" id="about">
      <div class="section-head reveal"><span class="eyebrow">About us</span><h2>Small studio, big care</h2><p>We are an independent studio. We take one clear idea at a time and polish it until it feels right.</p></div>
      <div class="why-grid">
        <div class="why-card reveal" style="--d:0s"><span class="why-ic">🌱</span><b>One clear idea</b><span>Each game and app does one thing and does it well.</span></div>
        <div class="why-card reveal" style="--d:.07s"><span class="why-ic">🎨</span><b>Made with care</b><span>Soft art, simple screens and details we are proud of.</span></div>
        <div class="why-card reveal" style="--d:.14s"><span class="why-ic">🔒</span><b>Clear about privacy</b><span>Every game and app has its own plain privacy policy.</span></div>
        <div class="why-card reveal" style="--d:.21s"><span class="why-ic">💬</span><b>Real support</b><span>Your email reaches the people who build the app.</span></div>
      </div>
    </section>

    <section class="contact reveal" id="contact">
      <span class="why-ic big">💌</span>
      <h2>Say hello</h2>
      <p>Found a bug, have an idea, or want to work with us? We read every message.</p>
      <a class="btn" href="mailto:{SITE['email']}">Email us</a>
    </section>
  </div>
{footer("", links, COMPANY, studio_mark(), "Little ideas, a touch of magic.", f'<p class="made">Made with care by {COMPANY}</p>')}"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("built index.html")


def build_app_page(a):
    """An app's page, in the same style as a game page. It is also the Support URL in the stores, so the help stays on it."""
    slug = a["slug"]
    url = f"{STUDIO_URL}{slug}/"
    prefix = "../"
    if a["status"] == "live":
        cta = f'<a class="btn" href="{play_url(a)}" target="_blank" rel="noopener">{PLAY_ICON} Get it on Google Play</a>'
    else:
        cta = '<span class="btn ghost disabled">🌱 Coming soon</span>'
    features = "".join(
        f'<div class="feat reveal" style="--d:{i * 0.07:.2f}s"><span class="feat-ic">{ic}</span><b>{E(t)}</b><span>{E(x)}</span></div>'
        for i, (ic, t, x) in enumerate(a["features"])
    )
    steps = "".join(
        f'<div class="feat reveal" style="--d:{i * 0.07:.2f}s"><span class="feat-ic step-no">{i + 1}</span><b>{E(t)}</b><span>{E(x)}</span></div>'
        for i, (t, x) in enumerate(a["steps"])
    )
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{answer}</p></details>' for q, answer in a["faq"])
    shots = "".join(
        f'<img src="shots/{i}.jpg" data-big="shots/{i}@2.jpg" alt="{E(a["name"])} screenshot {i}" loading="lazy" width="432" height="970">'
        for i in range(1, a["shots"] + 1)
    )
    gallery = f"""    <section class="gallery tall reveal" aria-label="Screenshots">
      <button class="arrow prev" type="button" aria-label="Previous screenshots">‹</button>
      <div class="shots" style="--n:{a['shots'] // 2}">{shots}</div>
      <button class="arrow next" type="button" aria-label="Next screenshots">›</button>
      <p class="sample">Light and dark themes. Screens show sample data.</p>
    </section>"""
    others = "".join(
        f'<a class="mini" href="../{o["slug"]}/" style="--c1:{o["color"]}"><img src="../{o["slug"]}/icon.png" alt="" loading="lazy" width="256" height="256"><span>{E(o["name"])}</span></a>'
        for o in APPS if o is not a
    )
    home = f'<a class="mini" href="../" style="--c1:#2B2A6B"><img src="../assets/logo-512.png" alt="" loading="lazy" width="256" height="256"><span>All games and apps</span></a>'
    links = (
        f'<div class="foot-links one"><div><b>{E(a["name"])}</b><a href="privacy.html">Privacy Policy</a><a href="#help">Support</a>'
        '<a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">Terms of Use</a></div></div>'
    )
    made = f'<p class="made">Made with care by {COMPANY}</p>'
    if a.get("credit"):
        made += f'<p class="credit">{E(a["credit"])}</p>'
    particles = json.dumps(a["particles"], ensure_ascii=False)
    style = f"""
  <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
  <style>:root {{ --c1: {a['color']}; --c2: {a['color2']}; --bg: {a['bg']}; }}</style>""" + ld({
        "@context": "https://schema.org", "@type": "MobileApplication", "name": a["title"], "description": a["description"],
        "url": url, "image": url + "icon.png", "applicationCategory": a["category"], "operatingSystem": "Android, iOS",
        "publisher": {"@type": "Organization", "name": COMPANY, "url": STUDIO_URL},
    })

    page = f"""{head(a["title"], a["description"], url + "icon.png", url, prefix, a["color"], style)}
<body class="app-page" data-particles='{particles}'>
{backdrop()}
  <div class="wrap">
{topbar(prefix, '<a href="#features">Features</a><a href="#help">Help</a><a href="#contact">Contact</a>', COMPANY, studio_mark(prefix))}

    <section class="hero game-hero">
      <div class="hero-text">
        <div class="title-row"><img class="app-icon" src="icon.png" alt="" width="256" height="256">{badge(a)}</div>
        <h1>{E(a['name'])}</h1>
        <p class="app-tag">{E(a['tag'])}</p>
        <p>{E(a['lead'])}</p>
        <div class="cta-row">{cta}<a class="btn ghost" href="#features">See what it does</a></div>
      </div>
      <div class="hero-visual"><div class="phone tall"><img src="shots/1.jpg" alt="{E(a['name'])} screenshot" width="432" height="970"></div></div>
    </section>
{gallery}

    <section class="about" id="features">
      <div class="section-head reveal"><span class="eyebrow">What it does</span><h2>Everything in one simple app</h2></div>
      <div class="feats">{features}</div>
    </section>

    <section class="about" id="how">
      <div class="section-head reveal"><span class="eyebrow">How it works</span><h2>Three easy steps</h2></div>
      <div class="feats three">{steps}</div>
    </section>

    <section class="about" id="help">
      <div class="section-head reveal"><span class="eyebrow">Help</span><h2>Questions and answers</h2></div>
      <div class="faqs">{faq}</div>
    </section>

    <section class="contact reveal" id="contact">
      <span class="why-ic big">💌</span>
      <h2>Contact us</h2>
      <p>Questions, bugs or ideas? We usually reply within 2 days.</p>
      <a class="btn" href="mailto:{SITE['email']}?subject={E(a['name'])}">Email us</a>
    </section>

    <section class="more">
      <div class="section-head reveal"><span class="eyebrow">More from {COMPANY}</span><h2>Keep exploring</h2></div>
      <div class="minis">{others}{home}</div>
    </section>
  </div>
{footer(prefix, links, COMPANY, studio_mark(prefix), "Little ideas, a touch of magic.", made)}"""
    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    print("built", out.relative_to(ROOT))


build_home()
for game in GAMES:
    build_game(game)
build_studio()
for app in APPS:
    build_app_page(app)
write_seo_files(ROOT, BASE, ["", "games/"] + [g["slug"] + "/" for g in GAMES + APPS])
