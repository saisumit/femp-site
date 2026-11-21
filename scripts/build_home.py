#!/usr/bin/env python3
"""Build the plugin pages of femp.ai: the general home (index.html), /jobs/ and /finance/.

Femp for DTC brands lives at /dtc/ (dtc/index.html, hand-written) and its pages are built by build_blog.py.
Run from anywhere: python3 scripts/build_home.py (standard library only).
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://femp.ai"
WA = "https://wa.me/918073735097?text=Hi%20Femp"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500&display=swap">')

PLUGINS = [
    {"id": "femp-dtc", "key": "dtc", "letter": "D", "name": "Femp for DTC brands", "status": "In beta", "href": "/dtc/",
     "q": "Running a store?", "a": "Stock, ads, pixel, chargebacks and social, fixed for you.",
     "about": "For Shopify and Amazon store owners: stock and reorders, ads against real sales, pixel health, SEO and AI search, chargebacks, inbox, and daily social stories and posts.",
     "connects": "Shopify · Amazon · Meta · Google Ads · Search Console · Gmail · Instagram"},
    {"id": "femp-jobs", "key": "jobs", "letter": "J", "name": "Femp Job Hunter", "status": "Coming soon", "href": "/jobs/",
     "q": "Looking for a job?", "a": "New roles every morning, each application tailored.",
     "about": "New roles that match you every morning, a tailored resume and cover letter for each, an application tracker, follow-up emails and interview prep.",
     "connects": "Your resume · Gmail · Google Calendar"},
    {"id": "femp-finance", "key": "fin", "letter": "F", "name": "Femp Finance", "status": "Coming soon", "href": "/finance/",
     "q": "Managing money?", "a": "Your stocks, bills and subscriptions, summed up daily.",
     "about": "Watches the stocks you follow (earnings dates, big moves, filings, news) and your money admin (bills due, subscriptions you no longer use), summed up each morning. Research and reminders only: Femp never trades or tells you what to buy.",
     "connects": "Your watchlist · Gmail (bills and receipts)"},
]

SCENES = {
    "dtc": ["DTC plugin", [
        ["f", "Morning Maya! Shopify had <b>64 orders</b> yesterday, but Meta only saw <b>46</b>. The pixel broke with Tuesday's theme update.", "8:02"],
        ["m", "ugh. can you fix it?", "8:05"],
        ["d", "Fixed ✓ Orders now go to Meta straight from Shopify. 12 counted so far today.", "8:07"]]],
    "jobs": ["Job Hunter", [
        ["f", "Morning! <b>4 new roles</b> match you. Best fit: Senior Product Designer at Lumen Health, remote, posted 6 hours ago. Your design-systems work is exactly what they list.", "8:30"],
        ["f", "Tailored resume and cover letter are ready. Want me to draft the email to the hiring manager?", "8:30"],
        ["m", "yes, send me the draft", "8:41"],
        ["d", "Draft is in your Gmail with both files attached ✓ I'll remind you to follow up in 5 days.", "8:42"]]],
    "fin": ["Finance", [
        ["f", "Morning. On your watchlist (sample tickers): <b>ORBT</b> reports earnings Wednesday after close, and <b>KLMN</b> fell 6% yesterday after cutting its outlook.", "7:45"],
        ["m", "summarise KLMN's filing", "7:52"],
        ["d", "Revenue up 12% on last year, margin down 2 points on freight, full-year outlook lowered. Research only, not advice. Also: your card bill (<b>$1,240</b>) is due Friday.", "7:53"]]],
}

CSS = """
:root {
  --paper: #f6f8f5; --panel: #ffffff; --ink: #0c1510; --muted: #56655d; --faint: #8a988f; --rule: #dfe6e0;
  --forest: #17694b; --accent: #146043; --tint: #e6f4ec; --mine: #d6f2e2; --chat: #ecf0ed; --mint: #5cc596;
  --dtc: #146043; --dtc-bg: #e6f4ec; --jobs: #3d6fb6; --jobs-bg: #e7eef8; --fin: #9a5b13; --fin-bg: #fbf1de;
  --sans: "Geist", "Avenir Next", "Segoe UI", system-ui, sans-serif; --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #09120d; --panel: #0f1b15; --ink: #e7f0ea; --muted: #9db0a5; --faint: #6d8075; --rule: #1d2d24;
  --accent: #6fd3a5; --tint: #12291e; --mine: #173a29; --chat: #17241d;
  --dtc: #6fd3a5; --dtc-bg: #12291e; --jobs: #8db2ea; --jobs-bg: #142235; --fin: #e3ad55; --fin-bg: #2b2212; color-scheme: dark; } }
:root[data-theme="dark"] {
  --paper: #09120d; --panel: #0f1b15; --ink: #e7f0ea; --muted: #9db0a5; --faint: #6d8075; --rule: #1d2d24;
  --accent: #6fd3a5; --tint: #12291e; --mine: #173a29; --chat: #17241d;
  --dtc: #6fd3a5; --dtc-bg: #12291e; --jobs: #8db2ea; --jobs-bg: #142235; --fin: #e3ad55; --fin-bg: #2b2212; color-scheme: dark; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 400 1.0625rem/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
h1, h2, h3, p, ul { margin: 0; }
a { color: var(--accent); text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--mint); outline-offset: 3px; }
.wrap { max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.frame { border-left: 1px solid var(--rule); border-right: 1px solid var(--rule); }
.label { font: 500 .74rem/1.3 var(--mono); letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.muted { color: var(--muted); }
.topbar { background: var(--forest); color: #fff; text-align: center; font-size: .85rem; padding: 8px 12px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; align-items: center; }
.topbar b { font-weight: 700; } .topbar a { color: #fff; font-weight: 600; }
.topbar .early { font: 500 .66rem/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; background: rgba(255,255,255,.18); padding: 4px 8px; border-radius: 99px; }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--paper); }
.nav { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 6; background: color-mix(in srgb, var(--paper) 86%, transparent); backdrop-filter: blur(12px); border-bottom: 1px solid var(--rule); }
.nav .wrap { display: flex; align-items: center; gap: 22px; padding-block: 12px; }
.brand { display: flex; align-items: center; gap: 9px; font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; color: var(--ink); text-decoration: none; margin-right: auto; }
.brand img { width: 30px; height: 30px; border-radius: 8px; }
.nav nav { display: flex; align-items: center; gap: 22px; }
.nav nav a { font: 500 .76rem/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); text-decoration: none; }
.nav nav a[aria-current="page"] { color: var(--ink); }
.btn { display: inline-flex; align-items: center; gap: 9px; padding: 12px 20px; border-radius: 10px; font: 600 .96rem/1 var(--sans); text-decoration: none; border: 1px solid transparent; cursor: pointer; transition: transform .15s; }
.btn:hover { transform: translateY(-1px); }
.btn.green { background: var(--forest); color: #fff; } .btn.solid { background: var(--ink); color: var(--paper); } .btn.line { background: var(--panel); border-color: var(--rule); color: var(--ink); }
.nav nav .btn { font: 600 .9rem/1 var(--sans); letter-spacing: 0; text-transform: none; color: #fff; padding: 10px 16px; }
.sec { padding: 56px 40px; border-top: 1px solid var(--rule); display: grid; gap: 26px; }
.sec h2 { font-size: clamp(1.9rem, 4vw, 2.8rem); font-weight: 800; letter-spacing: -0.04em; line-height: 1.04; text-wrap: balance; max-width: 22ch; }
.hero { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, .9fr); gap: 40px; padding: 56px 40px 52px; align-items: center; }
.hero h1 { font-size: clamp(2.8rem, 7vw, 5.4rem); font-weight: 800; letter-spacing: -0.055em; line-height: .95; text-wrap: balance; }
.hero h1 em { font-style: normal; color: var(--accent); }
.lede { font-size: 1.15rem; color: var(--muted); max-width: 54ch; margin-top: 20px; }
.ptabs { display: grid; gap: 6px; margin-top: 24px; list-style: none; padding: 0; }
.ptab { all: unset; box-sizing: border-box; width: 100%; display: grid; grid-template-columns: 12.5rem minmax(0, 1fr); gap: 3px 18px; padding: 11px 12px; border-radius: 10px; cursor: pointer; align-items: baseline; border: 1px solid transparent; }
.ptab:hover { background: var(--panel); }
.ptab:focus-visible { outline: 2px solid var(--mint); outline-offset: 2px; }
.ptab b { font-weight: 700; color: var(--c); } .ptab span { color: var(--muted); font-size: .95rem; }
.ptab small { grid-column: 1 / -1; font: 500 .66rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase; color: var(--faint); }
.ptab[aria-pressed="true"] { background: var(--cb); border-color: var(--rule); }
.k-dtc { --c: var(--dtc); --cb: var(--dtc-bg); } .k-jobs { --c: var(--jobs); --cb: var(--jobs-bg); } .k-fin { --c: var(--fin); --cb: var(--fin-bg); }
.ctas { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.phone { justify-self: center; width: 100%; max-width: 330px; height: 580px; border: 10px solid var(--ink); border-radius: 44px; background: var(--chat); display: grid; grid-template-rows: auto 1fr auto; overflow: hidden; box-shadow: 0 30px 60px -30px rgba(12,21,16,.5); }
.p-head { background: var(--forest); color: #fff; padding: 12px 14px; display: flex; gap: 10px; align-items: center; font-size: .9rem; }
.p-head img { width: 30px; height: 30px; border-radius: 50%; background: #fff; }
.p-head small { display: block; opacity: .75; font-size: .72rem; }
.p-head .plug { margin-left: auto; font: 500 .62rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase; background: rgba(255,255,255,.18); padding: 5px 7px; border-radius: 6px; }
.p-thread { padding: 12px; display: flex; flex-direction: column; justify-content: flex-end; gap: 8px; overflow: hidden; }
.bub { max-width: 88%; background: var(--panel); border-radius: 4px 14px 14px 14px; padding: 9px 12px 7px; font-size: .88rem; line-height: 1.42; animation: pop .3s ease-out both; }
.bub.me { align-self: flex-end; background: var(--mine); border-radius: 14px 4px 14px 14px; }
.bub.done { border-left: 3px solid var(--accent); }
.bub time { display: block; text-align: right; font: 400 .66rem/1 var(--mono); color: var(--faint); margin-top: 4px; }
.bub b { font-weight: 600; }
@keyframes pop { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.p-input { margin: 0 10px 10px; background: var(--panel); border-radius: 99px; padding: 10px 14px; font-size: .82rem; color: var(--faint); }
.plugins { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.plugin { background: var(--panel); border: 1px solid var(--rule); border-radius: 16px; padding: 20px; display: grid; gap: 10px; align-content: start; min-width: 0; color: inherit; text-decoration: none; transition: transform .15s; }
a.plugin:hover { transform: translateY(-2px); }
.plugin .top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.plugin .ic { width: 40px; height: 40px; border-radius: 11px; background: var(--cb); color: var(--c); display: grid; place-items: center; font-weight: 800; }
.pill { font: 500 .64rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase; padding: 5px 7px; border-radius: 99px; background: var(--cb); color: var(--c); }
.plugin h3 { font-size: 1.15rem; letter-spacing: -0.02em; }
.plugin p { color: var(--muted); font-size: .92rem; }
.plugin .conn { font: 400 .75rem/1.5 var(--mono); color: var(--faint); }
.plugin .go { font: 600 .9rem/1 var(--sans); color: var(--c); }
.plugin.more { border-style: dashed; background: transparent; } .plugin.more .ic { background: var(--chat); color: var(--muted); }
.steps { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; counter-reset: s; list-style: none; padding: 0; }
.steps li { display: grid; gap: 6px; border-top: 2px solid var(--forest); padding-top: 12px; counter-increment: s; }
.steps li::before { content: counter(s); font: 500 .76rem/1 var(--mono); color: var(--accent); }
.steps b { letter-spacing: -0.01em; } .steps p { color: var(--muted); font-size: .94rem; }
.steps code, .lede code { font: 500 .84em/1 var(--mono); background: var(--tint); color: var(--accent); padding: 3px 6px; border-radius: 5px; }
.core { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; }
.core li { border: 1px solid var(--rule); background: var(--panel); border-radius: 99px; padding: 7px 13px; font-size: .9rem; }
.feat { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; list-style: none; padding: 0; }
.feat li { background: var(--panel); border: 1px solid var(--rule); border-radius: 14px; padding: 18px; display: grid; gap: 6px; }
.feat b { letter-spacing: -0.01em; } .feat p { color: var(--muted); font-size: .93rem; }
.note { background: var(--fin-bg); border-radius: 12px; padding: 14px 16px; font-size: .95rem; max-width: 70ch; }
.closer { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 24px; }
.closer h2 { margin-bottom: 8px; }
footer { border-top: 1px solid var(--rule); }
footer .frame { padding: 22px 40px; display: flex; flex-wrap: wrap; gap: 8px 22px; font: 400 .8rem/1.6 var(--mono); color: var(--muted); }
footer a { color: var(--muted); }
@media (max-width: 1000px) { .hero { grid-template-columns: minmax(0, 1fr); } .plugins, .steps { grid-template-columns: repeat(2, minmax(0, 1fr)); } .feat { grid-template-columns: minmax(0, 1fr); } .ptab { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 620px) { .plugins, .steps { grid-template-columns: minmax(0, 1fr); } .hide-sm { display: none; } .hero, .sec, footer .frame { padding-left: 18px; padding-right: 18px; } }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .bub { animation: none; } .btn, a.plugin { transition: none; } }
"""


def head(title: str, desc: str, path: str, schema: dict) -> str:
    url = f"{SITE}{path}"
    t, d = escape(title), escape(desc)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#17694b">
<meta property="og:site_name" content="Femp"><meta property="og:type" content="website">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/img/og.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/img/og.jpg">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<script type="application/ld+json">{json.dumps(schema)}</script>
<style>{CSS}</style>
</head>"""


def nav(current: str) -> str:
    links = "".join(f'<a class="hide-sm" href="{p["href"]}"{" aria-current=\"page\"" if p["href"] == current else ""}>{"DTC brands" if p["key"] == "dtc" else p["name"].replace("Femp ", "")}</a>' for p in PLUGINS)
    return f"""<div class="topbar"><span class="early">Early access</span><span>Join the waitlist and get <b>$100 in free credits</b> for any plugin.</span><a href="/waitlist/?from=bar">Join the waitlist →</a></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/icon-512.png" alt="">Femp</a>
  <nav aria-label="Main">{links}<a class="hide-sm" href="/blog/">Blog</a><a class="btn green" href="{WA}">Say hi on WhatsApp</a></nav>
</div></header>"""


FOOTER = f"""<footer><div class="wrap"><div class="frame">
  <span>Femp is made by Femp AI, Inc. · <a href="mailto:support@femp.ai">support@femp.ai</a></span>
  <a href="/dtc/">DTC brands</a><a href="/jobs/">Job Hunter</a><a href="/finance/">Finance</a><a href="/blog/">Blog</a><a href="/dtc/security/">Security</a><a href="https://auth.femp.ai/support">Support</a><a href="https://auth.femp.ai/privacy">Privacy</a>
</div></div></footer>"""


def phone(first: str) -> str:
    plug = SCENES[first][0]
    return f"""<div class="phone" aria-live="polite">
  <div class="p-head"><img src="/img/icon-512.png" alt=""><div>Femp<small>online</small></div><span class="plug" id="plugname">{plug}</span></div>
  <div class="p-thread" id="thread"></div>
  <div class="p-input">Message</div>
</div>"""


def script(keys: list[str], rotate: bool) -> str:
    scenes = {k: SCENES[k] for k in keys}
    return f"""<script>
(() => {{
  const SCENES = {json.dumps(scenes)};
  const thread = document.getElementById("thread"), plugname = document.getElementById("plugname");
  const tabs = [...document.querySelectorAll(".ptab")];
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let run = 0, visible = true;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const bubble = ([w, h, t]) => {{ const el = document.createElement("div"); el.className = "bub" + (w === "m" ? " me" : "") + (w === "d" ? " done" : ""); el.innerHTML = h + "<time>" + t + "</time>"; return el; }};
  async function show(key, token, auto) {{
    tabs.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.p === key)));
    plugname.textContent = SCENES[key][0];
    thread.replaceChildren();
    for (const m of SCENES[key][1]) {{
      while (!visible) {{ await wait(400); if (token !== run) return; }}
      if (token !== run) return;
      thread.append(bubble(m));
      if (!still) await wait(1200);
    }}
    if (auto && !still && {str(rotate).lower()}) {{
      await wait(3800);
      if (token !== run) return;
      const keys = Object.keys(SCENES), next = keys[(keys.indexOf(key) + 1) % keys.length];
      show(next, token, true);
    }}
  }}
  tabs.forEach((b) => b.addEventListener("click", () => show(b.dataset.p, ++run, false)));
  new IntersectionObserver(([e]) => {{ visible = e.isIntersecting; }}).observe(thread);
  show({json.dumps(keys[0])}, ++run, true);
}})();
</script>"""


def card(p: dict) -> str:
    return f"""<a class="plugin k-{p['key']}" href="{p['href']}"><div class="top"><span class="ic">{p['letter']}</span><span class="pill">{p['status']}</span></div>
  <h3>{p['name']}</h3><p>{escape(p['about'])}</p><p class="conn">Connects: {escape(p['connects'])}</p><span class="go">{p['href'].strip('/') and 'femp.ai' + p['href']} →</span></a>"""


def home() -> str:
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Femp AI, Inc.", "legalName": "Femp AI, Inc.", "url": f"{SITE}/", "logo": f"{SITE}/img/icon-512.png", "email": "support@femp.ai"},
        {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "Femp", "alternateName": ["Femp AI", "femp.ai"], "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}, "inLanguage": "en-US"},
        {"@type": "SoftwareApplication", "name": "Femp", "alternateName": "Femp AI", "applicationCategory": "BusinessApplication", "operatingSystem": "iOS, WhatsApp",
         "description": "An assistant you text on WhatsApp or use in the Femp app, extended with plugins for running a store, job hunting and personal finance.",
         "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free during the beta"}}]}
    tabs = "".join(f'<li><button class="ptab k-{p["key"]}" type="button" data-p="{p["key"]}" aria-pressed="{"true" if i == 0 else "false"}"><b>{p["q"]}</b><span>{p["a"]}</span><small>{p["name"]} · {p["status"].lower()}</small></button></li>' for i, p in enumerate(PLUGINS))
    cards = "".join(card(p) for p in PLUGINS) + '<a class="plugin more" href="/waitlist/?for=other&amp;from=home-suggest"><div class="top"><span class="ic">+</span></div><h3>Your next plugin</h3><p>Planning a wedding, running a clinic, managing rentals? Tell us the job you\'d hand to Femp.</p><span class="go">Suggest one →</span></a>'
    return f"""{head("Femp AI: Your First Employee, With Plugins", "Femp is an assistant you text on WhatsApp. Install a plugin and it learns a job: running your store, finding your next role, keeping on top of your money.", "/", schema)}
<body>
{nav("/")}
<main><div class="wrap"><div class="frame">
<section class="hero">
  <div>
    <h1>Hire your <em>first employee.</em></h1>
    <p class="lede">Femp is an assistant you text on WhatsApp. Install a plugin and it learns a job: running your store, finding your next role, keeping on top of your money. It messages you when something needs you, and acts only after your yes.</p>
    <ul class="ptabs" aria-label="Tap one to see Femp at work">{tabs}</ul>
    <div class="ctas"><a class="btn solid" href="/waitlist/?from=home-hero">Join the waitlist →</a><a class="btn line" href="{WA}">Say hi on WhatsApp</a></div>
  </div>
  {phone("dtc")}
</section>
<section class="sec" id="plugins">
  <p class="label">Plugins</p>
  <h2>One assistant. Install the jobs you need.</h2>
  <div class="plugins">{cards}</div>
</section>
<section class="sec" id="how">
  <p class="label">How it works</p>
  <h2>Say hi, install a plugin, let it work.</h2>
  <ol class="steps">
    <li><b>Say hi on WhatsApp</b><p>Or download the Femp app. No forms.</p></li>
    <li><b>Install a plugin</b><p>Text <code>install job hunter</code>, or pick one in the app.</p></li>
    <li><b>Connect what it needs</b><p>Each connection uses the platform's own sign-in. Femp never sees your passwords.</p></li>
    <li><b>It checks in, you approve</b><p>Daily automations run in your time zone. Anything that changes or sends waits for your yes.</p></li>
  </ol>
  <ul class="core" aria-label="Included with every plugin"><li>Approvals before any change</li><li>Remembers your preferences</li><li>Automations you set in one message</li><li>Team members on their own WhatsApp</li><li>Undo and a log of everything</li></ul>
</section>
<section class="sec closer">
  <div><h2>Get Femp first.</h2><p class="muted">Join once, pick the plugins you want, and get $100 in free credits when yours launches.</p></div>
  <div class="ctas" style="margin:0"><a class="btn green" href="/waitlist/?from=home-closer">Join the waitlist</a><a class="btn line" href="{WA}">Say hi on WhatsApp</a></div>
</section>
</div></div></main>
{FOOTER}
{script(["dtc", "jobs", "fin"], True)}
</body></html>
"""


def plugin_page(p: dict, h1: str, lede: str, feats: list[tuple[str, str]], note: str = "") -> str:
    path = p["href"]
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": p["name"], "description": p["about"], "url": f"{SITE}{path}",
              "isPartOf": {"@type": "WebSite", "name": "Femp", "url": f"{SITE}/"}, "inLanguage": "en-US"}
    items = "".join(f"<li><b>{escape(t)}</b><p>{escape(d)}</p></li>" for t, d in feats)
    return f"""{head(f"{p['name']}: {p['a'].rstrip('.')}", p["about"], path, schema)}
<body>
{nav(path)}
<main><div class="wrap"><div class="frame">
<section class="hero">
  <div>
    <p class="label"><a href="/">Femp</a> / {p['name']} · {p['status'].lower()}</p>
    <h1 style="margin-top:14px">{h1}</h1>
    <p class="lede">{lede}</p>
    <div class="ctas"><a class="btn solid" href="/waitlist/?for={p['id']}&amp;from={p['key']}-hero">Join the waitlist →</a><a class="btn line" href="/">All plugins</a></div>
  </div>
  {phone(p["key"])}
</section>
<section class="sec">
  <p class="label">What it does</p>
  <h2>What {p['name'].replace('Femp ', '')} handles for you</h2>
  <ul class="feat">{items}</ul>
  {f'<p class="note">{note}</p>' if note else ''}
  <p class="muted">Connects: {escape(p['connects'])}. Each connection uses the platform's own sign-in, and nothing is sent without your yes.</p>
</section>
<section class="sec closer">
  <div><h2>Get {p['name']} first.</h2><p class="muted">Join the waitlist and get $100 in free credits when it launches.</p></div>
  <div class="ctas" style="margin:0"><a class="btn green" href="/waitlist/?for={p['id']}&amp;from={p['key']}-closer">Join the waitlist</a></div>
</section>
</div></div></main>
{FOOTER}
{script([p["key"]], False)}
</body></html>
"""


def main() -> None:
    by = {p["key"]: p for p in PLUGINS}
    (ROOT / "index.html").write_text(home(), encoding="utf-8")
    jobs = plugin_page(by["jobs"], "Your job search, <em>on autopilot.</em>",
        "Femp Job Hunter finds roles that fit you every morning, tailors your resume and cover letter for each one, and keeps your search moving with follow-ups and interview prep. You decide what gets sent.",
        [("New roles every morning", "Fresh openings that match your role, level and locations, ranked by how well you fit."),
         ("A tailored application each time", "Your resume and cover letter rewritten for the role, using only what's true about you."),
         ("Follow-ups that don't slip", "An application tracker, and follow-up emails drafted in your Gmail when it's time."),
         ("Interview prep", "What the company does, likely questions, and stories from your experience to tell."),
         ("Calendar handled", "Interview times added to Google Calendar, with a reminder and notes the day before."),
         ("You stay in charge", "Femp never applies or emails on its own. Every send waits for your yes.")])
    fin = plugin_page(by["fin"], "Your money, <em>summed up daily.</em>",
        "Femp Finance watches the stocks you follow and the bills you'd rather not miss, and sends one short summary each morning: earnings coming up, big moves, new filings, bills due and subscriptions you've stopped using.",
        [("Watchlist summary", "Earnings dates, big price moves and the news behind them, for the stocks you choose."),
         ("Filings in plain words", "Quarterly and annual reports summed up: revenue, margins and what changed in the outlook."),
         ("Bills due", "Card and utility bills found in your Gmail, with a reminder before the due date."),
         ("Subscriptions you don't use", "Recurring charges you haven't touched in a while, so you can cancel them."),
         ("Ask anything", "“What did Orbit say about margins?” or “How much did I spend on apps this year?”"),
         ("Research only", "No trades, no buy or sell calls. You make every decision.")],
        "Femp Finance is research and reminders, not financial advice. It never places trades or tells you what to buy or sell.")
    for name, html in (("jobs", jobs), ("finance", fin)):
        (ROOT / name).mkdir(exist_ok=True)
        (ROOT / name / "index.html").write_text(html.replace("<h1 style=\"margin-top:14px\">", "<h1 style=\"margin-top:14px\">"), encoding="utf-8")
    print("built home, jobs, finance")


if __name__ == "__main__":
    main()
