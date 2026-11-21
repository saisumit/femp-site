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
    {"id": "femp-dtc", "key": "dtc", "letter": "D", "name": "Femp for DTC brands", "short": "DTC brands", "line": "Your store's operations, handled.", "status": "In beta", "href": "/dtc/",
     "q": "Running a store?", "a": "Stock, ads, pixel, chargebacks and social, fixed for you.",
     "about": "For Shopify and Amazon store owners: stock and reorders, ads against real sales, pixel health, SEO and AI search, chargebacks, inbox, and daily social stories and posts.",
     "connects": "Shopify · Amazon · Meta · Google Ads · Search Console · Gmail · Instagram"},
    {"id": "femp-jobs", "key": "jobs", "letter": "J", "name": "Femp for Jobs", "short": "Jobs", "line": "Your job search, on autopilot.", "status": "Coming soon", "href": "/jobs/",
     "q": "Looking for a job?", "a": "New roles every morning, each application tailored.",
     "about": "New roles that match you every morning, a tailored resume and cover letter for each, an application tracker, follow-up emails and interview prep.",
     "connects": "Your resume · Gmail · Google Calendar"},
    {"id": "femp-finance", "key": "fin", "letter": "F", "name": "Femp for Finance", "short": "Finance", "line": "Your stocks and bills, summed up.", "status": "Coming soon", "href": "/finance/",
     "q": "Managing money?", "a": "Your stocks, bills and subscriptions, summed up daily.",
     "about": "Watches the stocks you follow (earnings dates, big moves, filings, news) and your money admin (bills due, subscriptions you no longer use), summed up each morning. Research and reminders only: Femp never trades or tells you what to buy.",
     "connects": "Your watchlist · Gmail (bills and receipts)"},
]

SCENES = {
    "dtc": ["DTC plugin", [
        ["f", "Morning Maya! Shopify had <b>64 orders</b> yesterday, but Meta only saw <b>46</b>. The pixel broke with Tuesday's theme update.", "8:02"],
        ["m", "ugh. can you fix it?", "8:05"],
        ["d", "Fixed ✓ Orders now go to Meta straight from Shopify. 12 counted so far today.", "8:07"]]],
    "jobs": ["Jobs", [
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
.plugin { background: var(--panel); border: 1px solid var(--rule); border-radius: 16px; padding: 20px; display: grid; gap: 8px; grid-template-rows: auto auto 1fr auto; min-width: 0; color: inherit; text-decoration: none; transition: transform .15s; }
a.plugin:hover { transform: translateY(-2px); }
.plugin .top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.plugin .ic { width: 40px; height: 40px; border-radius: 11px; background: var(--cb); color: var(--c); display: grid; place-items: center; font-weight: 800; }
.pill { font: 500 .64rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase; padding: 5px 7px; border-radius: 99px; background: var(--cb); color: var(--c); }
.plugin h3 { font-size: 1.15rem; letter-spacing: -0.02em; }
.plugin p { color: var(--muted); font-size: .92rem; }
.plugin .conn { font: 400 .75rem/1.5 var(--mono); color: var(--faint); }
.plugin .go { font: 600 1.1rem/1 var(--sans); color: var(--c); margin-top: 6px; }
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

/* home: lock screen hero */
.label .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--mint); margin-right: 4px; vertical-align: 1px; box-shadow: 0 0 0 4px color-mix(in srgb, var(--mint) 25%, transparent); }
.uhero { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); gap: 40px; padding: 64px 40px 56px; align-items: center; position: relative; overflow: hidden; }
.uhero::before { content: ""; position: absolute; right: -120px; top: -80px; width: 560px; height: 560px; border-radius: 50%; background: radial-gradient(circle, color-mix(in srgb, var(--mint) 22%, transparent), transparent 65%); pointer-events: none; }
.uhero h1 { font-size: clamp(3rem, 7.4vw, 6rem); font-weight: 800; letter-spacing: -0.058em; line-height: .92; text-wrap: balance; margin-top: 14px; }
.uhero h1 em { font-style: normal; color: var(--accent); }
.plugs { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 30px; }
.plug { all: unset; box-sizing: border-box; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 99px; border: 1px solid var(--rule); background: var(--panel); font-weight: 600; font-size: .9rem; }
.plug i { width: 9px; height: 9px; border-radius: 50%; background: var(--c); }
.plug[aria-pressed="true"] { background: var(--cb); border-color: var(--c); color: var(--c); }
.plug:focus-visible { outline: 2px solid var(--mint); outline-offset: 2px; }
.lock { justify-self: center; width: 100%; max-width: 340px; aspect-ratio: 9 / 18.5; border: 10px solid var(--ink); border-radius: 50px; overflow: hidden; position: relative; z-index: 1; box-shadow: 0 40px 80px -40px rgba(12,21,16,.6); background: #0b1a13; }
.lscreen { position: absolute; inset: 0; background: radial-gradient(120% 70% at 20% 0%, #2f8a64 0%, transparent 60%), radial-gradient(90% 60% at 100% 100%, #c9a26a 0%, transparent 55%), linear-gradient(170deg, #17694b, #0b2a1f 70%); display: grid; grid-template-rows: auto 1fr auto; padding: 22px 12px 14px; }
.ltime { text-align: center; color: #fff; display: grid; gap: 2px; padding-top: 18px; }
.ltime small { font-size: .82rem; font-weight: 600; opacity: .85; }
.ltime span { font-size: 4.6rem; font-weight: 700; letter-spacing: -0.04em; line-height: 1; }
.lstack { display: flex; flex-direction: column; gap: 8px; align-self: end; margin-bottom: 10px; }
.lnote { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 10px; align-items: start; padding: 11px 12px; border-radius: 20px; background: rgba(245,248,246,.78); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); color: #0c1510; animation: drop .5s cubic-bezier(.2,.9,.2,1) both; opacity: calc(1 - var(--d, 0) * .18); transform-origin: top center; }
.lnote img { width: 30px; height: 30px; border-radius: 8px; }
.lnote small { display: flex; gap: 4px; font-size: .68rem; color: #4a5a51; text-transform: uppercase; letter-spacing: .03em; }
.lnote small b { font-weight: 700; color: #0c1510; } .lnote small em { margin-left: auto; font-style: normal; text-transform: none; }
.lnote strong { display: block; font-size: .86rem; margin-top: 2px; }
.lnote span { display: block; font-size: .8rem; line-height: 1.35; color: #2b3a31; }
.lnote.k-dtc strong { color: #146043; } .lnote.k-jobs strong { color: #2c5ea8; } .lnote.k-fin strong { color: #8a4f0e; }
@keyframes drop { from { opacity: 0; transform: translateY(-18px) scale(.96); } to { transform: none; } }
.lbar { justify-self: center; width: 120px; height: 5px; border-radius: 3px; background: rgba(255,255,255,.7); }

/* home: photo cards */
.shead { display: grid; gap: 8px; }
.pcards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.pcard { position: relative; aspect-ratio: 4 / 5.2; border-radius: 22px; overflow: hidden; color: #fff; text-decoration: none; isolation: isolate; box-shadow: 0 24px 50px -36px rgba(12,21,16,.7); }
.pcard > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .6s cubic-bezier(.2,.8,.2,1); }
.pcard::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(0,0,0,.05) 35%, rgba(6,18,12,.82) 100%); }
.pcard:hover > img { transform: scale(1.05); }
.pstat { position: absolute; top: 14px; left: 14px; font: 600 .66rem/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; background: rgba(255,255,255,.88); color: var(--c); padding: 6px 9px; border-radius: 99px; }
.pnote { position: absolute; left: 14px; right: 14px; top: 46%; display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 9px; padding: 10px 11px; border-radius: 16px; background: rgba(245,248,246,.82); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); color: #0c1510; transform: translateY(-50%); transition: transform .4s cubic-bezier(.2,.8,.2,1); }
.pcard:hover .pnote { transform: translateY(calc(-50% - 6px)); }
.pnote img { width: 26px; height: 26px; border-radius: 7px; }
.pnote small { display: block; font-size: .64rem; text-transform: uppercase; letter-spacing: .04em; color: #4a5a51; }
.pnote b { display: block; font-size: .84rem; color: var(--c); }
.pnote span { display: block; font-size: .76rem; color: #2b3a31; line-height: 1.3; }
.pfoot { position: absolute; left: 18px; right: 18px; bottom: 18px; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2px 12px; align-items: end; }
.pfoot h3 { font-size: 1.3rem; letter-spacing: -0.025em; grid-column: 1; }
.pfoot p { font-size: .95rem; opacity: .9; grid-column: 1; }
.parrow { grid-column: 2; grid-row: 1 / span 2; width: 40px; height: 40px; border-radius: 50%; background: #fff; color: #0c1510; display: grid; place-items: center; font-weight: 700; transition: transform .3s; }
.pcard:hover .parrow { transform: translateX(3px); }
.suggest { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 14px; align-items: center; padding: 16px 20px; border: 1px dashed var(--rule); border-radius: 16px; color: var(--ink); text-decoration: none; }
.suggest:hover { border-color: var(--accent); }
.suggest .plus { width: 34px; height: 34px; border-radius: 10px; background: var(--chat); display: grid; place-items: center; font-weight: 700; color: var(--muted); }
.suggest b { font-weight: 700; } .suggest span:nth-child(2) { color: var(--muted); } .suggest span:nth-child(2) b { color: var(--ink); }

/* home: plugging in */
.plugin-in { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); align-items: center; gap: 40px; }
.pin-copy { display: grid; gap: 14px; }
.flow { list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 0; counter-reset: f; }
.flow li { display: grid; grid-template-columns: 2.2rem minmax(0, 1fr); gap: 2px 12px; padding: 12px 0; border-bottom: 1px solid var(--rule); counter-increment: f; }
.flow li::before { content: counter(f); grid-row: 1 / span 2; width: 26px; height: 26px; border-radius: 50%; background: var(--tint); color: var(--accent); display: grid; place-items: center; font: 600 .8rem/1 var(--mono); }
.flow b { letter-spacing: -0.01em; } .flow span { color: var(--muted); font-size: .94rem; }
.chatcard { justify-self: center; width: 100%; max-width: 400px; border-radius: 24px; overflow: hidden; background: var(--chat); border: 1px solid var(--rule); box-shadow: 0 30px 60px -40px rgba(12,21,16,.5); min-height: 360px; display: grid; grid-template-rows: auto 1fr; }
.chead { background: var(--forest); color: #fff; display: flex; gap: 10px; align-items: center; padding: 12px 16px; font-weight: 600; }
.chead img { width: 32px; height: 32px; border-radius: 50%; background: #fff; } .chead small { display: block; font-weight: 400; opacity: .75; font-size: .72rem; }
.cthread { padding: 16px; display: flex; flex-direction: column; justify-content: flex-end; gap: 9px; }
.cb { max-width: 85%; background: var(--panel); border-radius: 4px 16px 16px 16px; padding: 10px 13px; font-size: .92rem; line-height: 1.45; animation: pop .35s ease-out both; }
.cb.me { align-self: flex-end; background: var(--mine); border-radius: 16px 4px 16px 16px; }
.cb .file { display: block; background: var(--panel); border-radius: 10px; padding: 8px 10px; margin-bottom: 6px; font-weight: 600; font-size: .86rem; }

/* home: trust + closer */
.trust h2 { max-width: none; }
.tgrid { list-style: none; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--rule); }
.tgrid li { padding: 18px 20px 4px 0; display: grid; gap: 6px; }
.tgrid b { letter-spacing: -0.01em; } .tgrid span { color: var(--muted); font-size: .94rem; }
.closer2 { justify-items: center; text-align: center; gap: 16px; padding-block: 72px; }
.closer2 h2 { max-width: none; }
.faces { display: flex; } .faces img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 3px solid var(--paper); margin-left: -14px; } .faces img:first-child { margin-left: 0; }
@media (max-width: 1000px) { .uhero, .plugin-in { grid-template-columns: minmax(0, 1fr); } .pcards { grid-template-columns: minmax(0, 1fr); max-width: 460px; } .tgrid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 620px) { .uhero { padding: 40px 18px; } .tgrid { grid-template-columns: minmax(0, 1fr); } .suggest { grid-template-columns: auto minmax(0, 1fr); } .suggest > span:last-child { display: none; } }
@media (prefers-reduced-motion: reduce) { .lnote, .cb { animation: none; } .pcard > img, .pnote, .parrow { transition: none; } }
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
    links = "".join(f'<a class="hide-sm" href="{p["href"]}"{" aria-current=\"page\"" if p["href"] == current else ""}>{p["short"]}</a>' for p in PLUGINS)
    return f"""<div class="topbar"><span class="early">Early access</span><span>Join the waitlist and get <b>$100 in free credits</b> for any plugin.</span><a href="/waitlist/?from=bar">Join the waitlist →</a></div>
<header class="nav"><div class="wrap">
  <a class="brand" href="/"><img src="/img/icon-512.png" alt="">Femp</a>
  <nav aria-label="Main">{links}<a class="hide-sm" href="/blog/">Blog</a><a class="btn green" href="{WA}">Say hi on WhatsApp</a></nav>
</div></header>"""


FOOTER = f"""<footer><div class="wrap"><div class="frame">
  <span>Femp is made by Femp AI, Inc. · <a href="mailto:support@femp.ai">support@femp.ai</a></span>
  <a href="/dtc/">DTC brands</a><a href="/jobs/">Jobs</a><a href="/finance/">Finance</a><a href="/blog/">Blog</a><a href="/dtc/security/">Security</a><a href="https://auth.femp.ai/support">Support</a><a href="https://auth.femp.ai/privacy">Privacy</a>
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
  <h3>{p['name']}</h3><p>{p['line']}</p><span class="go" aria-hidden="true">→</span></a>"""


NOTES = [
    {"k": "fin", "plug": "Finance", "title": "Card bill due Friday", "text": "$1,240 on your Visa. You also pay for 2 apps you haven't opened in 60 days."},
    {"k": "dtc", "plug": "DTC brands", "title": "Pixel fixed ✓", "text": "Meta missed 18 orders after Tuesday's theme update. Tracking is back."},
    {"k": "jobs", "plug": "Jobs", "title": "4 new roles match you", "text": "Best fit: Senior Product Designer, remote. Your tailored resume is ready."},
    {"k": "dtc", "plug": "DTC brands", "title": "3 stories ready", "text": "Made from today's restock. Tap to preview and post everywhere."},
    {"k": "fin", "plug": "Finance", "title": "ORBT reports Wednesday", "text": "Earnings after close. Summary of last quarter attached. Research only."},
    {"k": "jobs", "plug": "Jobs", "title": "Follow up with Lumen Health?", "text": "It's been 5 days. A short follow-up is drafted in your Gmail."},
]

PHOTOS = {
    "dtc": ("/img/home/dtc.jpg", "A skincare brand owner packing orders and checking her phone", "Pixel fixed ✓", "18 missed orders are back in Meta."),
    "jobs": ("/img/home/jobs.jpg", "A man at a cafe smiling at his phone", "4 new roles match you", "Best fit is remote. Resume tailored."),
    "fin": ("/img/home/fin.jpg", "A woman at her kitchen table checking her phone", "Card bill due Friday", "$1,240. Plus 2 apps you never open."),
}


def home() -> str:
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Femp AI, Inc.", "legalName": "Femp AI, Inc.", "url": f"{SITE}/", "logo": f"{SITE}/img/icon-512.png", "email": "support@femp.ai"},
        {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "Femp", "alternateName": ["Femp AI", "femp.ai"], "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}, "inLanguage": "en-US"},
        {"@type": "SoftwareApplication", "name": "Femp", "alternateName": "Femp AI", "applicationCategory": "BusinessApplication", "operatingSystem": "iOS, WhatsApp",
         "description": "An assistant you text on WhatsApp or use in the Femp app, extended with plugins for running a store, job hunting and personal finance.",
         "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free during the beta"}}]}
    plugs = "".join(f'<button class="plug k-{p["key"]}" type="button" data-k="{p["key"]}" aria-pressed="false"><i></i>{p["short"]}</button>' for p in PLUGINS)
    cards = ""
    for p in PLUGINS:
        img, alt, t, d = PHOTOS[p["key"]]
        cards += f"""<a class="pcard k-{p['key']}" href="{p['href']}">
  <img src="{img}" alt="{escape(alt)}" loading="lazy">
  <span class="pstat">{p['status']}</span>
  <div class="pnote"><img src="/img/icon-512.png" alt=""><div><small>Femp · {p['short']}</small><b>{t}</b><span>{d}</span></div></div>
  <div class="pfoot"><h3>{p['name']}</h3><p>{p['line']}</p><span class="parrow" aria-hidden="true">→</span></div>
</a>"""
    return f"""{head("Femp AI: Your First Employee, With Plugins", "Femp is an assistant you text on WhatsApp. Plug in a job and it gets to work: running your store, finding your next role, keeping on top of your money.", "/", schema)}
<body>
{nav("/")}
<main><div class="wrap"><div class="frame">
<section class="uhero">
  <div class="ucopy">
    <p class="label"><b class="dot"></b> Early access · $100 in free credits</p>
    <h1>Hire your <em>first employee.</em></h1>
    <p class="lede">One assistant on WhatsApp. Plug in a job, and Femp gets to work. It messages you when something needs you, and acts only after your yes.</p>
    <div class="ctas"><a class="btn solid" href="/waitlist/?from=home-hero">Join the waitlist →</a><a class="btn line" href="{WA}">Say hi on WhatsApp</a></div>
    <div class="plugs" role="group" aria-label="Show one plugin"><span class="label">Plugged in:</span>{plugs}</div>
  </div>
  <div class="lock" aria-label="Femp notifications on a phone lock screen">
    <div class="lscreen">
      <div class="ltime"><small>Saturday 22 November</small><span>8:15</span></div>
      <div class="lstack" id="stack" aria-live="polite"></div>
      <div class="lbar"></div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="shead"><p class="label">Plugins</p><h2>One employee. Many jobs.</h2></div>
  <div class="pcards">{cards}</div>
  <a class="suggest" href="/waitlist/?for=other&amp;from=home-suggest"><span class="plus">+</span><span><b>Got another job for Femp?</b> Wedding planning, a clinic's bookings, your rentals. Suggest a plugin.</span><span aria-hidden="true">→</span></a>
</section>

<section class="sec plugin-in">
  <div class="pin-copy">
    <p class="label">How it works</p>
    <h2>Plugging in takes one message.</h2>
    <ol class="flow">
      <li><b>Say hi on WhatsApp</b><span>Or open the Femp app.</span></li>
      <li><b>Ask for a plugin</b><span>“install femp for jobs”</span></li>
      <li><b>Connect what it needs</b><span>Each app's own sign-in. No passwords shared.</span></li>
      <li><b>Femp starts working</b><span>Checks in on a schedule. Waits for your yes.</span></li>
    </ol>
  </div>
  <div class="chatcard" aria-label="Installing a plugin on WhatsApp">
    <div class="chead"><img src="/img/icon-512.png" alt=""><div>Femp<small>online</small></div></div>
    <div class="cthread" id="install"></div>
  </div>
</section>

<section class="sec trust">
  <h2>It asks before it acts.</h2>
  <ul class="tgrid">
    <li><b>Your yes, every time</b><span>Nothing is sent, posted, paid or changed without it.</span></li>
    <li><b>Remembers you</b><span>Preferences, people and past decisions, across every plugin.</span></li>
    <li><b>Undo and a log</b><span>See everything Femp did, and take it back.</span></li>
    <li><b>Your team, too</b><span>Add people who chat with Femp from their own WhatsApp.</span></li>
  </ul>
</section>

<section class="sec closer2">
  <div class="faces"><img src="/img/home/dtc.jpg" alt=""><img src="/img/home/jobs.jpg" alt=""><img src="/img/home/fin.jpg" alt=""></div>
  <h2>Get Femp first.</h2>
  <p class="muted">Join once, pick your plugins, and get $100 in free credits when yours launches.</p>
  <div class="ctas"><a class="btn green" href="/waitlist/?from=home-closer">Join the waitlist</a><a class="btn line" href="{WA}">Say hi on WhatsApp</a></div>
</section>
</div></div></main>
{FOOTER}
<script>
(() => {{
  const NOTES = {json.dumps(NOTES)};
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const stack = document.getElementById("stack"), plugs = [...document.querySelectorAll(".plug")];
  let filter = null, i = 0, timer = 0, onScreen = true;
  const card = (n) => {{
    const el = document.createElement("div");
    el.className = "lnote k-" + n.k;
    el.innerHTML = `<img src="/img/icon-512.png" alt=""><div><small><b>Femp</b> · ${{n.plug}}<em>now</em></small><strong>${{n.title}}</strong><span>${{n.text}}</span></div>`;
    return el;
  }};
  const list = () => NOTES.filter((n) => !filter || n.k === filter);
  function push() {{
    const notes = list(); const n = notes[i % notes.length]; i++;
    stack.prepend(card(n));
    while (stack.children.length > 4) stack.lastElementChild.remove();
    [...stack.children].forEach((c, j) => c.style.setProperty("--d", j));
  }}
  function seed() {{ stack.replaceChildren(); i = 0; const n = Math.min(3, list().length); for (let k = 0; k < n; k++) push(); }}
  function loop() {{ clearInterval(timer); if (still) return; timer = setInterval(() => {{ if (onScreen) push(); }}, 2600); }}
  plugs.forEach((b) => b.addEventListener("click", () => {{
    const k = b.dataset.k; filter = filter === k ? null : k;
    plugs.forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.k === filter)));
    seed(); loop();
  }}));
  new IntersectionObserver(([e]) => {{ onScreen = e.isIntersecting; }}).observe(stack);
  seed(); loop();

  // install chat plays once when it scrolls into view
  const box = document.getElementById("install");
  const CHAT = [["me", "install femp for jobs"], ["f", "Done ✓ <b>Femp for Jobs</b> is plugged in. Send me your resume and tell me what you're looking for."],
                ["me", "<span class='file'>📄 Resume_2026.pdf</span>senior product designer, remote"], ["f", "Got it. Your first matching roles arrive tomorrow at 8:30, each with a tailored resume."]];
  const bub = ([w, h]) => {{ const el = document.createElement("div"); el.className = "cb" + (w === "me" ? " me" : ""); el.innerHTML = h; return el; }};
  let played = false;
  async function play() {{
    if (played) return; played = true;
    for (const m of CHAT) {{ box.append(bub(m)); if (!still) await new Promise((r) => setTimeout(r, 1100)); }}
  }}
  if (still) CHAT.forEach((m) => box.append(bub(m)));
  else new IntersectionObserver(([e]) => {{ if (e.isIntersecting) play(); }}, {{ threshold: 0.4 }}).observe(box);
}})();
</script>
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
  <h2>What {p['name']} does for you</h2>
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
        "Femp for Jobs finds roles that fit you every morning, tailors your resume and cover letter for each one, and keeps your search moving with follow-ups and interview prep. You decide what gets sent.",
        [("New roles every morning", "Fresh openings that match your role, level and locations, ranked by how well you fit."),
         ("A tailored application each time", "Your resume and cover letter rewritten for the role, using only what's true about you."),
         ("Follow-ups that don't slip", "An application tracker, and follow-up emails drafted in your Gmail when it's time."),
         ("Interview prep", "What the company does, likely questions, and stories from your experience to tell."),
         ("Calendar handled", "Interview times added to Google Calendar, with a reminder and notes the day before."),
         ("You stay in charge", "Femp never applies or emails on its own. Every send waits for your yes.")])
    fin = plugin_page(by["fin"], "Your money, <em>summed up daily.</em>",
        "Femp for Finance watches the stocks you follow and the bills you'd rather not miss, and sends one short summary each morning: earnings coming up, big moves, new filings, bills due and subscriptions you've stopped using.",
        [("Watchlist summary", "Earnings dates, big price moves and the news behind them, for the stocks you choose."),
         ("Filings in plain words", "Quarterly and annual reports summed up: revenue, margins and what changed in the outlook."),
         ("Bills due", "Card and utility bills found in your Gmail, with a reminder before the due date."),
         ("Subscriptions you don't use", "Recurring charges you haven't touched in a while, so you can cancel them."),
         ("Ask anything", "“What did Orbit say about margins?” or “How much did I spend on apps this year?”"),
         ("Research only", "No trades, no buy or sell calls. You make every decision.")],
        "Femp for Finance is research and reminders, not financial advice. It never places trades or tells you what to buy or sell.")
    for name, html in (("jobs", jobs), ("finance", fin)):
        (ROOT / name).mkdir(exist_ok=True)
        (ROOT / name / "index.html").write_text(html.replace("<h1 style=\"margin-top:14px\">", "<h1 style=\"margin-top:14px\">"), encoding="utf-8")
    print("built home, jobs, finance")


if __name__ == "__main__":
    main()
