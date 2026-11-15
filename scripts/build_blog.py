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
WA = "https://wa.me/919351808066?text=Hi%20Femp"
OG = f"{SITE}/img/og.jpg"
LOGO = f"{SITE}/img/icon-512.png"
HOME_UPDATED = "2026-11-15"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800'
    '&family=Geist+Mono:wght@400;500&display=swap">'
)

MAIN_NAV = [("/features/", "Features"), ("/how-it-works/", "How it works"), ("/pricing/", "Pricing"), ("/faq/", "FAQ")]


def nav(current: str = "") -> str:
    links = "".join(
        f'<a class="hide-sm" href="{h}"{" aria-current=\"page\"" if h == current else ""}>{t}</a>' for h, t in MAIN_NAV
    )
    blog = ' aria-current="page"' if current == "/blog/" else ""
    return f"""<header class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/icon-512.png" alt="Femp" width="30" height="30">Femp</a>
  <nav aria-label="Main">{links}<a href="/blog/"{blog}>Blog</a>
  <a class="btn green" href="{WA}">Say hi on WhatsApp</a></nav>
</div></header>"""

FOOTER = """<footer><div class="wrap"><div class="frame ruled" style="border-bottom:0"><div>
  <span>Femp is made by Neobrix · <a href="mailto:support@femp.ai">support@femp.ai</a></span>
  <nav aria-label="Footer"><a href="/features/">Features</a><a href="/how-it-works/">How it works</a><a href="/integrations/">Integrations</a><a href="/pricing/">Pricing</a><a href="/security/">Security</a><a href="/faq/">FAQ</a><a href="/blog/">Blog</a><a href="/blog/feed.xml">RSS</a><a href="https://auth.femp.ai/support">Support</a><a href="https://auth.femp.ai/privacy">Privacy</a><a href="https://youtu.be/W9z4sHcGYgk">Demo</a></nav>
</div></div></div></footer>"""

CLOSER = f"""<section class="closer ruled"><div>
  <h2>Put Femp on shift.</h2>
  <p>Say hi on WhatsApp, connect your Shopify or Amazon store, and your first stock check arrives a few minutes later. Free while we're in beta.</p>
  <div class="ctas"><a class="btn green" href="{WA}">Say hi on WhatsApp</a><a class="btn line" href="/#game">Play a week at a store</a></div>
</div><img src="/img/icon-512.png" alt="" width="110" height="110" loading="lazy"></section>"""

ORG = {"@type": "Organization", "name": "Neobrix", "url": SITE, "logo": {"@type": "ImageObject", "url": LOGO}}
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
    urls = [(f"{SITE}/", HOME_UPDATED)] + [(p["url"], p["updated"]) for p in pages]
    urls += [(f"{SITE}/blog/", latest)] + [(p["url"], p["updated"]) for p in posts]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def llms(posts: list[dict], pages: list[dict]) -> str:
    lines = [
        "# Femp",
        "",
        "> Femp (also called Femp AI, by Neobrix) is an AI operations assistant for owners of Shopify and Amazon brands. It watches stock, "
        "ad spend against real sales, search and AI-assistant findability, and the store's Gmail inbox, messages the "
        "owner on WhatsApp or in the Femp app when something needs them, and makes the fixes they approve. Free during the beta.",
        "",
        "Femp never changes prices, stock or checkout. Ads access is read-only. Product SEO and blog edits happen only after the owner says yes, and can be undone.",
        "",
        "## Product",
        f"- [Home]({SITE}/): what Femp does, an interactive week at a store, daily check-ins and ground rules",
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
    for p in posts:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article(p, posts), encoding="utf-8")
    (ROOT / "blog" / "index.html").write_text(index(posts), encoding="utf-8")
    (ROOT / "blog" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(posts, pages), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(posts, pages), encoding="utf-8")
    (ROOT / "llms-full.txt").write_text(llms_full(posts, pages), encoding="utf-8")
    print(f"built {len(pages)} pages and {len(posts)} posts")


if __name__ == "__main__":
    main()
