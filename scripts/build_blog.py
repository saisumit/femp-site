#!/usr/bin/env python3
"""Build the femp.ai blog from content/blog/*.html.

Each source file starts with a JSON header in an HTML comment, then the article body:

    <!--{"slug": "...", "title": "...", "description": "...", "category": "...",
          "date": "2026-11-15", "updated": "2026-11-15", "lede": "..."}-->
    <p>Body HTML...</p>

Writes blog/<slug>/index.html, blog/index.html, blog/feed.xml, sitemap.xml and llms.txt.
Run from anywhere: python3 scripts/build_blog.py (standard library only).
"""

from __future__ import annotations

import json
import re
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from html import escape
from pathlib import Path

SITE = "https://femp.ai"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "blog"
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

NAV = f"""<header class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/icon-512.png" alt="" width="30" height="30">Femp</a>
  <nav aria-label="Main"><a class="hide-sm" href="/">Product</a><a href="/blog/"{{blog_current}}>Blog</a>
  <a class="btn green" href="{WA}">Say hi on WhatsApp</a></nav>
</div></header>"""

FOOTER = """<footer><div class="wrap"><div class="frame ruled" style="border-bottom:0"><div>
  <span>Femp is made by Neobrix · <a href="mailto:support@femp.ai">support@femp.ai</a></span>
  <nav aria-label="Footer"><a href="/blog/">Blog</a><a href="/blog/feed.xml">RSS</a><a href="https://auth.femp.ai/support">Support</a><a href="https://auth.femp.ai/privacy">Privacy</a><a href="https://youtu.be/W9z4sHcGYgk">Demo</a></nav>
</div></div></div></footer>"""

CLOSER = f"""<section class="closer ruled"><div>
  <h2>Put Femp on shift.</h2>
  <p>Say hi on WhatsApp, connect your Shopify or Amazon store, and your first stock check arrives a few minutes later. Free while we're in beta.</p>
  <div class="ctas"><a class="btn green" href="{WA}">Say hi on WhatsApp</a><a class="btn line" href="/#game">Play a week at a store</a></div>
</div><img src="/img/icon-512.png" alt="" width="110" height="110" loading="lazy"></section>"""

ORG = {"@type": "Organization", "name": "Neobrix", "url": SITE, "logo": {"@type": "ImageObject", "url": LOGO}}


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


def load() -> list[dict]:
    posts = []
    for path in sorted(SRC.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(\{.*?\})-->\s*", text, re.S)
        if not m:
            raise SystemExit(f"{path}: missing JSON header")
        meta = json.loads(m.group(1))
        meta["body"] = text[m.end():]
        words = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
        meta["minutes"] = max(1, round(words / 230))
        meta["url"] = f"{SITE}/blog/{meta['slug']}/"
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
{NAV.replace('{blog_current}', '')}
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
{NAV.replace('{blog_current}', ' aria-current="page"')}
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


def sitemap(posts: list[dict]) -> str:
    latest = max(p["updated"] for p in posts)
    urls = [(f"{SITE}/", HOME_UPDATED), (f"{SITE}/blog/", latest)] + [(p["url"], p["updated"]) for p in posts]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def llms(posts: list[dict]) -> str:
    lines = [
        "# Femp",
        "",
        "> Femp (by Neobrix) is an AI operations assistant for owners of Shopify and Amazon brands. It watches stock, "
        "ad spend against real sales, search and AI-assistant findability, and the store's Gmail inbox, messages the "
        "owner on WhatsApp or in the Femp app when something needs them, and makes the fixes they approve. Free during the beta.",
        "",
        "Femp never changes prices, stock or checkout. Ads access is read-only. Product SEO and blog edits happen only after the owner says yes, and can be undone.",
        "",
        "## Product",
        f"- [Home]({SITE}/): what Femp does, an interactive week at a store, daily check-ins and ground rules",
        "- [Privacy policy](https://auth.femp.ai/privacy)",
        "- [Support](https://auth.femp.ai/support)",
        "",
        "## Blog",
        *[f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    posts = load()
    for p in posts:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article(p, posts), encoding="utf-8")
    (ROOT / "blog" / "index.html").write_text(index(posts), encoding="utf-8")
    (ROOT / "blog" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(posts), encoding="utf-8")
    print(f"built {len(posts)} posts")


if __name__ == "__main__":
    main()
