#!/usr/bin/env python3
"""Build the femp.ai blog and product pages from content/blog/*.html and content/pages/*.html.

Each source file starts with a JSON header in an HTML comment, then the article body:

    <!--{"slug": "...", "title": "...", "description": "...", "category": "...",
          "date": "2026-11-15", "updated": "2026-11-15", "lede": "..."}-->
    <p>Body HTML...</p>

Pages use the same header (plus "nav", and "faq": true for a Q&A page of <h2>/<p> pairs) and render at /<slug>/.
Writes <slug>/index.html, blog/<slug>/index.html, blog/index.html, blog/feed.xml, sitemap.xml, llms.txt and llms-full.txt.
Run from anywhere: python3 scripts/build_blog.py (standard library only).
"""

from __future__ import annotations

import json
import re
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from html import escape, unescape
from pathlib import Path

SITE = "https://femp.ai"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "blog"
PAGES = ROOT / "content" / "pages"
WA = "https://wa.me/918073735097?text=Hi%20Femp"
OG = f"{SITE}/img/og.jpg"
LOGO = f"{SITE}/img/icon-512.png"
HOME_UPDATED = "2026-11-15"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800'
    '&family=Geist+Mono:wght@400;500&display=swap">'
)

# one nav for the whole site; each plugin is a single page (/dtc/, /jobs/, /finance/), the rest is shared
NAV = [("/pricing/", "Pricing"), ("/faq/", "FAQ")]
# the Plugins dropdown that opens the nav (same markup in build_home.py and dtc/index.html)
PLUGINS_MENU = '''<details class="pmenu"><summary>Plugins</summary><div class="pdrop"><a class="pm" href="/dtc/"><span class="pi" style="--pc:#146043">D</span><span class="pt"><b>Femp for DTC brands</b><small>Your store's operations</small></span><em>Beta</em></a><a class="pm" href="/jobs/"><span class="pi" style="--pc:#3d6fb6">J</span><span class="pt"><b>Femp for Jobs</b><small>Your job search</small></span><em>Soon</em></a><a class="pm" href="/finance/"><span class="pi" style="--pc:#9a5b13">F</span><span class="pt"><b>Femp for Finance</b><small>Stocks and bills</small></span><em>Soon</em></a><a class="pall" href="/#plugins">All plugins →</a></div></details>'''
MENU_JS = '''<script>(()=>{const m=[...document.querySelectorAll("details.pmenu")];document.addEventListener("click",e=>m.forEach(d=>{if(d.open&&!d.contains(e.target))d.open=false;}));document.addEventListener("keydown",e=>{if(e.key==="Escape")m.forEach(d=>{if(d.open){d.open=false;d.querySelector("summary").focus();}});});})();</script>'''
# DTC pages that became part of /dtc/; their old addresses forward there
MERGED_INTO_DTC = ["features", "how-it-works", "integrations"]


BAR = """<div class="topbar"><span class="early">Early access</span><span><a href="/" style="color:inherit">← All plugins</a> · Femp for DTC brands is coming to the Shopify App Store and the App Store. Join the waitlist and get <b>$100 in free credits</b>.</span><a href="/waitlist/?for=femp-dtc&amp;from=bar">Join the waitlist →</a></div>"""
GENERAL_BAR = """<div class="topbar"><span class="early">Early access</span><span>Femp is your first employee, with plugins for your store, your job search and your money. Join the waitlist and get <b>$100 in free credits</b>.</span><a href="/waitlist/?from=bar">Join the waitlist →</a></div>"""


def nav(current: str = "") -> str:
    links = "".join(
        f'<a class="hide-sm" href="{h}"{" aria-current=\"page\"" if h == current else ""}>{t}</a>' for h, t in NAV
    )
    blog = ' aria-current="page"' if current == "/blog/" else ""
    bar = "" if current == "/waitlist/" else GENERAL_BAR
    return f"""{bar}<header class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/icon-512.png" alt="Femp" width="30" height="30">Femp</a>
  <nav aria-label="Main">{PLUGINS_MENU}{links}<a href="/blog/"{blog}>Blog</a>
  <a class="btn green" href="{WA}">Say hi on WhatsApp</a></nav>
</div></header>"""

FOOTER = """<footer><div class="wrap"><div class="frame ruled" style="border-bottom:0"><div>
  <span>Femp is made by Femp AI, Inc. · <a href="mailto:support@femp.ai">support@femp.ai</a></span>
  <nav aria-label="Footer"><a href="/dtc/">DTC brands</a><a href="/jobs/">Jobs</a><a href="/finance/">Finance</a><a href="/pricing/">Pricing</a><a href="/faq/">FAQ</a><a href="/security/">Security</a><a href="/blog/">Blog</a><a href="/blog/feed.xml">RSS</a><a href="https://auth.femp.ai/support">Support</a><a href="https://auth.femp.ai/privacy">Privacy</a><a href="https://youtu.be/W9z4sHcGYgk">Demo</a></nav>
</div></div></div></footer>"""

CLOSER = f"""<section class="closer ruled"><div>
  <h2>Get Femp first.</h2>
  <p>Femp is your First EMPloyee: an AI assistant on WhatsApp that you can give a job. Join the waitlist and get $100 in free credits.</p>
  <div class="ctas"><a class="btn green" href="/waitlist/?from=closer">Join the waitlist</a><a class="btn line" href="{WA}">Say hi on WhatsApp</a></div>
</div><img src="/img/icon-512.png" alt="" width="110" height="110" loading="lazy"></section>"""

ORG = {"@type": "Organization", "name": "Femp AI, Inc.", "url": SITE, "logo": {"@type": "ImageObject", "url": LOGO}}
SOFTWARE = {
    "@type": "SoftwareApplication", "name": "Femp", "alternateName": "Femp AI", "applicationCategory": "BusinessApplication",
    "url": f"{SITE}/", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free during the beta"},
}


def ld(data: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def human(d: str) -> str:
    return date.fromisoformat(d).strftime("%B %-d, %Y")


def head(title: str, description: str, url: str, kind: str = "website", extra: str = "") -> str:
    t, d = escape(title), escape(description)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#17694b">
<meta property="og:site_name" content="Femp"><meta property="og:type" content="{kind}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{OG}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{OG}">
<link rel="alternate" type="application/rss+xml" title="Femp blog" href="{SITE}/blog/feed.xml">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}<link rel="stylesheet" href="/assets/site.css">
{extra}
</head>"""


def moved(url: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>'
            f'<link rel="canonical" href="{url}"><meta name="robots" content="noindex">'
            f'<meta http-equiv="refresh" content="0; url={url}"></head>'
            f'<body><p>This page moved to <a href="{url}">{url}</a>.</p></body></html>\n')


def load(src: Path = SRC, prefix: str = "/blog/") -> list[dict]:
    posts = []
    for path in sorted(src.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(\{.*?\})-->\s*", text, re.S)
        if not m:
            raise SystemExit(f"{path}: missing JSON header")
        meta = json.loads(m.group(1))
        meta["body"] = text[m.end():]
        words = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
        meta["minutes"] = max(1, round(words / 230))
        meta["url"] = f"{SITE}{prefix}{meta['slug']}/"
        meta.setdefault("date", HOME_UPDATED)
        meta.setdefault("updated", meta["date"])
        meta.setdefault("order", 99)
        posts.append(meta)
    posts.sort(key=lambda p: (p["order"], p["date"]))
    return posts


def card(p: dict, lead: bool = False) -> str:
    return f"""<a class="card{' lead' if lead else ''}" href="/blog/{p['slug']}/">
  <p class="label"><b>●</b> {escape(p['category'])}</p><h2>{escape(p['title'])}</h2>
  <p>{escape(p['description'])}</p><p class="meta">{human(p['date'])} · {p['minutes']} min read</p></a>"""


def article(p: dict, posts: list[dict]) -> str:
    related = [q for q in posts if q["slug"] != p["slug"]][:3]
    schema = [
        {
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
            "description": p["description"], "image": OG, "url": p["url"], "mainEntityOfPage": p["url"],
            "datePublished": p["date"], "dateModified": p["updated"], "articleSection": p["category"],
            "inLanguage": "en-US", "wordCount": p["minutes"] * 230,
            "author": {"@type": "Organization", "name": "The Femp team", "url": SITE}, "publisher": ORG,
        },
        {
            "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Femp", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
            ],
        },
    ]
    extra = (
        f'<meta property="article:published_time" content="{p["date"]}">'
        f'<meta property="article:modified_time" content="{p["updated"]}">'
        f'<meta property="article:section" content="{escape(p["category"])}">' + "".join(ld(s) for s in schema)
    )
    return f"""{head(p['seo_title'] if 'seo_title' in p else p['title'] + ' | Femp', p['description'], p['url'], 'article', extra)}
<body>
{nav()}
<main><div class="wrap"><div class="frame">
<article>
  <header class="post-head">
    <p class="crumbs"><a href="/">Femp</a> / <a href="/blog/">Blog</a> / {escape(p['category'])}</p>
    <h1>{escape(p['title'])}</h1>
    <p class="lede">{escape(p['lede'])}</p>
    <p class="meta">By the Femp team · <time datetime="{p['date']}">{human(p['date'])}</time> · {p['minutes']} min read</p>
  </header>
  <div class="post-body ruled"><div class="prose">
{p['body'].strip()}
  </div></div>
</article>
<section class="related ruled"><h2>Keep reading</h2><div class="posts">{''.join(card(q) for q in related)}</div></section>
{CLOSER}
</div></div></main>
{FOOTER}
{MENU_JS}
</body></html>
"""


def faq_items(body: str) -> list[dict]:
    pairs = re.findall(r"<h2>(.*?)</h2>\s*(.*?)(?=<h2>|\Z)", body, re.S)
    return [
        {"@type": "Question", "name": unescape(re.sub(r"<[^>]+>", "", q)).strip(),
         "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", a).strip()}}
        for q, a in pairs
    ]


def page(p: dict, pages: list[dict]) -> str:
    schema = [
        {
            "@context": "https://schema.org", "@type": "FAQPage" if p.get("faq") else "WebPage", "name": p["title"],
            "description": p["description"], "url": p["url"], "inLanguage": "en-US", "dateModified": p["updated"],
            "isPartOf": {"@type": "WebSite", "name": "Femp", "url": f"{SITE}/"}, "publisher": ORG,
            **({"mainEntity": faq_items(p["body"])} if p.get("faq") else {"about": SOFTWARE}),
        },
        {
            "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Femp", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": p["nav"], "item": p["url"]},
            ],
        },
    ]
    others = "".join(f'<a href="/{q["slug"]}/">{escape(q["nav"])}</a>' for q in pages if q["slug"] != p["slug"])
    return f"""{head(p['seo_title'], p['description'], p['url'], extra=''.join(ld(s) for s in schema))}
<body>
{nav("/" + p["slug"] + "/")}
<main><div class="wrap"><div class="frame">
<article>
  <header class="post-head">
    <p class="crumbs"><a href="/">Femp</a> / {escape(p['nav'])}</p>
    <h1>{escape(p['title'])}</h1>
    <p class="lede">{escape(p['lede'])}</p>
  </header>
  <div class="post-body ruled"><div class="prose">
{p['body'].strip()}
  <p class="meta">More about Femp: {others}<a href="/blog/">Blog</a></p>
  </div></div>
</article>
{CLOSER}
</div></div></main>
{FOOTER}
{MENU_JS}
</body></html>
"""


WAITLIST_API = "https://auth.femp.ai/waitlist"  # server copy, best-effort
# Apps Script web app on the "Femp waitlist" sheet (scripts/waitlist-sheet.gs); the record of every signup
WAITLIST_SHEET = "https://script.google.com/macros/s/AKfycbzkG5sM0WUcJ1hKwuXITLArufe2xjf6cV97AJgBR8CceJi-iGRBKDnGnPlvn_72RJmQ/exec"
# country calling codes for the WhatsApp field, most common first; the script preselects the visitor's region
CODES = [
    ("US", "+1"), ("IN", "+91"), ("GB", "+44"), ("CA", "+1"), ("AU", "+61"), ("AE", "+971"), ("DE", "+49"), ("FR", "+33"),
    ("NL", "+31"), ("ES", "+34"), ("IT", "+39"), ("SG", "+65"), ("NZ", "+64"), ("IE", "+353"), ("SE", "+46"), ("SA", "+966"),
    ("MX", "+52"), ("BR", "+55"), ("ZA", "+27"), ("PK", "+92"), ("BD", "+880"), ("ID", "+62"), ("MY", "+60"), ("PH", "+63"),
    ("JP", "+81"), ("KR", "+82"), ("HK", "+852"), ("IL", "+972"), ("TR", "+90"), ("PL", "+48"), ("NG", "+234"), ("KE", "+254"),
]


# sales channels a US store may use; keys match the server's waitlist Platform list
CHANNELS = [
    ("shopify", "Shopify"), ("amazon", "Amazon"), ("walmart", "Walmart"), ("ebay", "eBay"), ("etsy", "Etsy"),
    ("tiktok_shop", "TikTok Shop"), ("target_plus", "Target Plus"), ("woocommerce", "WooCommerce"),
    ("bigcommerce", "BigCommerce"), ("wix", "Wix"), ("squarespace", "Squarespace"), ("other", "Other"),
]


# plugins someone can ask for on the waitlist; keys are the plugin ids
WANTS = [("femp-dtc", "Run my online store"), ("femp-jobs", "Find a job"), ("femp-finance", "Stocks and money"), ("other", "Something else")]


def flag(cc: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in cc)


def waitlist() -> str:
    url = f"{SITE}/waitlist/"
    title = "Join the Femp AI Waitlist: $100 in Free Credits"
    description = ("Join the Femp AI waitlist for your store, your job search or your money. Get an early invite and "
                   "$100 in free credits.")
    schema = {
        "@context": "https://schema.org", "@type": "WebPage", "name": "Femp waitlist", "description": description,
        "url": url, "inLanguage": "en-US", "isPartOf": {"@type": "WebSite", "name": "Femp", "url": f"{SITE}/"},
        "publisher": ORG, "about": SOFTWARE,
    }
    channels = "".join(f'<label><input type="checkbox" name="platforms" id="p-{key}" value="{key}">{name}</label>' for key, name in CHANNELS)
    wants = "".join(f'<label><input type="checkbox" name="wants" id="w-{key}" value="{key}">{name}</label>' for key, name in WANTS)
    options = "".join(f'<option value="{code}" data-cc="{cc}">{flag(cc)} {code}</option>' for cc, code in CODES)
    return f"""{head(title, description, url, extra=ld(schema))}
<body>
{nav("/waitlist/")}
<main><div class="wrap"><div class="frame">
<section class="wl">
  <div class="wl-copy">
    <p class="label"><b>●</b> Early access</p>
    <p class="credit"><strong>$100</strong> in free credits for everyone on the list</p>
    <h1>Get Femp first, with $100 in free credits.</h1>
    <p class="lede">Tell us what you want Femp for. We'll message you on WhatsApp as soon as that plugin is ready to install.</p>
    <ul>
      <li>An invite before the public launch</li>
      <li>$100 in free credits on your account when you install</li>
      <li>Setup with the founder over WhatsApp, if you want it</li>
    </ul>
  </div>
  <div class="wl-form" id="join">
    <form id="wl" novalidate>
      <div class="field"><label for="email">Work email</label>
        <input id="email" name="email" type="email" autocomplete="email" placeholder="you@yourstore.com" required></div>
      <div class="field"><label for="phone">WhatsApp number</label>
        <div class="phone"><select id="cc" aria-label="Country code">{options}</select>
        <input id="phone" name="phone" type="tel" autocomplete="tel-national" inputmode="tel" placeholder="Phone number" required></div></div>
      <fieldset class="field"><legend>What do you want Femp for? <small>(pick all that apply)</small></legend>
        <div class="seg">{wants}</div></fieldset>
      <div id="store-fields">
      <div class="field"><label for="store">Store link <small>(optional)</small></label>
        <input id="store" name="store" type="text" inputmode="url" autocomplete="url" placeholder="yourstore.com or a marketplace storefront link"></div>
      <fieldset class="field"><legend>Where do you sell? <small>(pick all that apply)</small></legend>
        <div class="seg">{channels}</div></fieldset>
      </div>
      <div class="field" id="other-field" hidden><label for="other">What job would you hand to Femp?</label>
        <input id="other" name="other" type="text" placeholder="Book my clinic's appointments"></div>
      <div class="hp" aria-hidden="true"><label for="leave-empty">Leave this field empty</label><input id="leave-empty" name="leave_empty" type="text" tabindex="-1" autocomplete="off" data-1p-ignore data-lpignore="true"></div>
      <label class="consent" for="consent"><input id="consent" type="checkbox" checked><span>Femp can contact me on WhatsApp and email about early access. No spam, and you can leave any time.</span></label>
      <p class="fine bad" id="err" role="alert" hidden></p>
      <button class="btn green" type="submit" id="go">Join and claim $100 in credits</button>
      <p class="fine">Credits apply to Femp after launch, one per person. We use your details only for Femp early access. <a href="https://auth.femp.ai/privacy">Privacy</a></p>
    </form>
    <div class="done" id="done" hidden>
      <div class="tick" aria-hidden="true">✓</div>
      <h2 tabindex="-1" id="done-title">You're on the list.</h2>
      <p class="credit"><strong>$100</strong> in free credits saved for you</p>
      <p>We'll message you on WhatsApp when Femp is ready to install, and the credits will be on your account. You can say hi now if you want to talk about your store.</p>
      <div class="ctas" style="justify-content:center"><a class="btn green" href="{WA}">Say hi on WhatsApp</a><a class="btn line" href="https://youtu.be/W9z4sHcGYgk">Watch the demo</a></div>
    </div>
  </div>
</section>
</div></div></main>
{FOOTER}
<script>
(() => {{
  const $ = id => document.getElementById(id), form = $("wl"), err = $("err"), go = $("go");
  const region = (navigator.languages || [navigator.language]).map(l => (l.split("-")[1] || "").toUpperCase()).find(Boolean);
  const pick = [...$("cc").options].find(o => o.dataset.cc === region);
  if (pick) pick.selected = true;
  const asked = new URLSearchParams(location.search).get("for");
  const box = $("w-" + asked);
  if (box) box.checked = true;
  const sync = () => {{ $("store-fields").hidden = !$("w-femp-dtc").checked; $("other-field").hidden = !$("w-other").checked; }};
  form.addEventListener("change", sync); sync();
  const show = text => {{ err.textContent = text; err.hidden = !text; }};
  form.addEventListener("submit", async e => {{
    e.preventDefault();
    const email = $("email").value.trim(), digits = $("phone").value.replace(/\\D/g, "");
    if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)) return show("Enter your email address."), $("email").focus();
    if (digits.length < 6) return show("Enter your WhatsApp number."), $("phone").focus();
    if (!$("consent").checked) return show("Tick the box so we can contact you about early access.");
    const phone = $("phone").value.trim().startsWith("+") ? "+" + digits : $("cc").value + digits.replace(/^0+/, "");
    const body = {{
      email, phone, store: $("store").value.trim(), consent: true, company: $("leave-empty").value,
      platforms: [...form.querySelectorAll("input[name=platforms]:checked")].map(i => i.value),
      wants: [...form.querySelectorAll("input[name=wants]:checked")].map(i => i.value === "other" && $("other").value.trim() ? "other: " + $("other").value.trim() : i.value),
      source: new URLSearchParams(location.search).get("from") || (document.referrer ? new URL(document.referrer).pathname : "direct"),
    }};
    show(""); go.disabled = true; go.textContent = "Joining…";
    // The Google Sheet is the record (works with our server off); the server copy is best-effort and never awaited
    // unless the sheet can't be reached. text/plain keeps the sheet request free of a CORS preflight.
    const payload = JSON.stringify(body);
    const copied = fetch("{WAITLIST_API}", {{ method: "POST", headers: {{ "content-type": "application/json" }}, body: payload, keepalive: true }})
      .then(r => r.ok, () => false);
    try {{
      let out = {{}};
      try {{
        const res = await fetch("{WAITLIST_SHEET}", {{ method: "POST", headers: {{ "content-type": "text/plain;charset=utf-8" }}, body: payload }});
        out = await res.json().catch(() => ({{}}));
        if (!res.ok && out.ok === undefined) throw new TypeError("sheet unavailable");
      }} catch (down) {{
        if (!(down instanceof TypeError) || !(await copied)) throw down;
        out = {{ ok: true }};
      }}
      if (out.ok === false) throw new Error(out.error || "Something went wrong. Try again in a minute.");
      form.hidden = true; $("done").hidden = false; $("done-title").focus();
    }} catch (problem) {{
      show(problem instanceof TypeError ? "Couldn't reach Femp. Check your connection and try again." : problem.message);
      go.disabled = false; go.textContent = "Join and claim $100 in credits";
    }}
  }});
}})();
</script>
{MENU_JS}
</body></html>
"""


def index(posts: list[dict]) -> str:
    url = f"{SITE}/blog/"
    title = "Femp blog: running a DTC brand without drowning in ops"
    desc = ("Field notes for Shopify and Amazon brand owners on stock, ads, chargebacks, search, cash and compliance, "
            "and the jobs an AI operations assistant can take off your plate.")
    schema = {
        "@context": "https://schema.org", "@type": "Blog", "name": "Femp blog", "url": url, "description": desc,
        "publisher": ORG, "inLanguage": "en-US",
        "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"]} for p in posts],
    }
    cards = "".join(card(p, lead=i == 0) for i, p in enumerate(posts))
    return f"""{head(title, desc, url, extra=ld(schema))}
<body>
{nav("/blog/")}
<main><div class="wrap"><div class="frame">
<section class="chapter">
  <div class="chapter-head"><p class="label"><b>●</b> / field notes</p>
    <div><h1>Run the brand. Let the ops run themselves.</h1>
    <p>Practical notes for owners of Shopify and Amazon brands: what to watch, what it costs you when nobody does, and what an AI operations assistant can take off your plate.</p></div>
  </div>
  <div class="posts">{cards}</div>
</section>
{CLOSER}
</div></div></main>
{FOOTER}
{MENU_JS}
</body></html>
"""


def feed(posts: list[dict]) -> str:
    def rfc(d: str) -> str:
        return format_datetime(datetime.fromisoformat(d).replace(hour=9, tzinfo=timezone.utc))

    items = "".join(
        f"<item><title>{escape(p['title'])}</title><link>{p['url']}</link><guid>{p['url']}</guid>"
        f"<pubDate>{rfc(p['date'])}</pubDate><category>{escape(p['category'])}</category>"
        f"<description>{escape(p['description'])}</description></item>\n"
        for p in sorted(posts, key=lambda p: p["date"], reverse=True)
    )
    latest = max(p["updated"] for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>Femp blog</title><link>{SITE}/blog/</link>
<atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
<description>Field notes for Shopify and Amazon brand owners from the team behind Femp.</description>
<language>en-us</language><lastBuildDate>{rfc(latest)}</lastBuildDate>
{items}</channel></rss>
"""


def sitemap(posts: list[dict], pages: list[dict]) -> str:
    latest = max(p["updated"] for p in posts)
    urls = [(f"{SITE}/", HOME_UPDATED), (f"{SITE}/dtc/", HOME_UPDATED), (f"{SITE}/jobs/", HOME_UPDATED), (f"{SITE}/finance/", HOME_UPDATED), (f"{SITE}/waitlist/", HOME_UPDATED)] + [(p["url"], p["updated"]) for p in pages]
    urls += [(f"{SITE}/blog/", latest)] + [(p["url"], p["updated"]) for p in posts]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def llms(posts: list[dict], pages: list[dict]) -> str:
    lines = [
        "# Femp",
        "",
        "> Femp (also called Femp AI, by Femp AI, Inc.) is an assistant you text on WhatsApp or use in the Femp app, extended with plugins. "
        "Femp for DTC brands (in beta) runs operations for Shopify and Amazon stores: the pixel, ad spend against real sales, search and AI-assistant rankings, "
        "stock, chargebacks, the store's Gmail inbox and social posts. Femp for Jobs and Femp for Finance are coming soon. Femp acts only after the person says yes. Free during the beta.",
        "",
        "Femp never changes prices, stock or checkout. Ads access is read-only. Product SEO and blog edits happen only after the owner says yes, and can be undone.",
        "",
        "## Product",
        f"- [Home]({SITE}/): Femp as your first employee, and its plugins",
        f"- [Femp for DTC brands]({SITE}/dtc/): what Femp does for Shopify and Amazon stores, a WhatsApp demo and 20 ready-made automations",
        f"- [Femp for Jobs]({SITE}/jobs/): matching roles every morning, tailored applications, follow-ups (coming soon)",
        f"- [Femp for Finance]({SITE}/finance/): stock watchlist research, bills and subscriptions (coming soon)",
        *[f"- [{p['nav']}]({p['url']}): {p['description']}" for p in pages],
        "- [Privacy policy](https://auth.femp.ai/privacy)",
        "- [Support](https://auth.femp.ai/support)",
        "",
        "## Blog",
        *[f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts],
        "",
        "## Optional",
        f"- [Full text of every page and post]({SITE}/llms-full.txt)",
        "",
    ]
    return "\n".join(lines)


def text(body: str) -> str:
    body = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", body)
    body = re.sub(r"<li>", "- ", body)
    body = re.sub(r"</(p|li|tr|ul|div)>", "\n", body)
    body = re.sub(r"</t[dh]>", " | ", body)
    body = unescape(re.sub(r"<[^>]+>", "", body))
    return re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]+", " ", body)).strip()


def llms_full(posts: list[dict], pages: list[dict]) -> str:
    parts = [llms(posts, pages).split("## Product")[0].strip()]
    for p in pages + posts:
        parts.append(f"# {p['title']}\n\nURL: {p['url']}\n\n{p['lede']}\n\n{text(p['body'])}")
    return "\n\n---\n\n".join(parts) + "\n"


def main() -> None:
    posts = load()
    pages = load(PAGES, "/")
    for p in pages:
        out = ROOT / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(p, pages), encoding="utf-8")
    # old DTC pages keep working: a small page that forwards to /dtc/ (GitHub Pages has no real redirects)
    for slug in MERGED_INTO_DTC:
        old = ROOT / slug / "index.html"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text(moved(f"{SITE}/dtc/"), encoding="utf-8")
    for p in posts:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article(p, posts), encoding="utf-8")
    (ROOT / "waitlist").mkdir(exist_ok=True)
    (ROOT / "waitlist" / "index.html").write_text(waitlist(), encoding="utf-8")
    (ROOT / "blog" / "index.html").write_text(index(posts), encoding="utf-8")
    (ROOT / "blog" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(posts, pages), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(posts, pages), encoding="utf-8")
    (ROOT / "llms-full.txt").write_text(llms_full(posts, pages), encoding="utf-8")
    print(f"built {len(pages)} pages and {len(posts)} posts")


if __name__ == "__main__":
    main()
