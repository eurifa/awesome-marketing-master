#!/usr/bin/env python3
"""Build README.md and tools.csv from data/tools.txt.

Usage: python3 scripts/build.py
"""
import csv
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "tools.txt"

PRICING = {"F": "🆓", "M": "🔓", "P": "💲", "O": "🧩"}
PRICING_NAME = {"F": "Free", "M": "Freemium", "P": "Paid", "O": "Open source"}


def slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s", "-", s.strip())


def parse():
    cats = []  # [{name, subs: [{name, tools: []}]}]
    cat = sub = None
    seen = set()
    for n, raw in enumerate(DATA.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") and not line.startswith("##"):
            continue
        if line.startswith("### "):
            sub = {"name": line[4:].strip(), "tools": []}
            cat["subs"].append(sub)
            continue
        if line.startswith("## "):
            cat = {"name": line[3:].strip(), "subs": []}
            cats.append(cat)
            sub = None
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4 or parts[2] not in PRICING:
            sys.exit(f"tools.txt:{n}: bad line: {raw!r}")
        name, url, price, desc = parts
        if not url.startswith("http"):
            sys.exit(f"tools.txt:{n}: bad url: {url!r}")
        if sub is None:  # category with no subsections
            sub = {"name": "", "tools": []}
            cat["subs"].append(sub)
        key = (cat["name"], name.lower(), urlparse(url).netloc.lower().removeprefix("www."))
        if key in seen:
            continue
        seen.add(key)
        sub["tools"].append(dict(name=name, url=url, price=price, desc=desc))
    return cats


def main():
    cats = parse()
    total = sum(len(s["tools"]) for c in cats for s in c["subs"])
    unique_urls = {t["url"] for c in cats for s in c["subs"] for t in s["tools"]}

    out = []
    w = out.append
    w("# Awesome Marketing: The Master List\n")
    w(
        "A single, curated, opinionated list of marketing tools and resources, built by merging "
        "[awesome-marketing](https://github.com/marketingtoolslist/awesome-marketing) with 20 other "
        "awesome-lists and cleaning the result: dead and renamed tools fixed, duplicates merged, "
        "and **AI search (GEO/AEO), open-source, privacy-first, and indie/creator tools** added.\n"
    )
    w(f"**{total} tools** across **{len(cats)} categories** · {len(unique_urls)} unique links · last built {date.today().isoformat()}\n")
    w("**Legend:** 🆓 Free · 🔓 Freemium / free tier · 💲 Paid · 🧩 Open source (self-hostable)\n")
    w("> Pricing models change often. Treat the icon as a starting point and check the vendor's site.\n")

    # quick start
    w("## Start here: a lean stack by stage\n")
    w("| Goal | Solo / bootstrapped (cheap) | Growing team |")
    w("|---|---|---|")
    w("| Analytics | Google Analytics 4 + Search Console, Plausible, or PostHog | Mixpanel / Amplitude + Segment, Looker Studio |")
    w("| SEO | Search Console, Ahrefs Webmaster Tools, Screaming Frog (free), Keywords Everywhere | Ahrefs or Semrush, Surfer / Clearscope |")
    w("| AI search visibility | Free manual prompt checks + Otterly | Peec AI, Profound, Ahrefs Brand Radar |")
    w("| Email | Kit, MailerLite, Buttondown, or beehiiv | Customer.io, Klaviyo, HubSpot |")
    w("| Social | Buffer or Publer, Typefully | Sprout Social, Hootsuite, Brand24 |")
    w("| CRM / automation | HubSpot free CRM, Attio, n8n / Zapier | HubSpot, Salesforce, Make, Clay |")
    w("| Outbound | Apollo free, Hunter, Instantly | Clay + Smartlead / Outreach |")
    w("| CRO | Microsoft Clarity, Tally, PostHog experiments | VWO / Optimizely, Hotjar |")
    w("| Design | Canva, Figma, Photopea | Figma, Adobe Express, Frontify |")
    w("| Launch | Product Hunt, Hacker News, BetaList, Indie Hackers | PH + G2 / Capterra + PR (Muck Rack) |")
    w("")

    # TOC
    w("## Contents\n")
    for c in cats:
        cnt = sum(len(s["tools"]) for s in c["subs"])
        w(f"- [{c['name']}](#{slug(c['name'])}) ({cnt})")
        for s in c["subs"]:
            if s["name"]:
                w(f"  - [{s['name']}](#{slug(s['name'])})")
    w("- [Defunct, Renamed & Acquired](#defunct-renamed--acquired)")
    w("- [Contributing](#contributing)\n")

    # body
    for c in cats:
        w(f"## {c['name']}\n")
        for s in c["subs"]:
            if s["name"]:
                w(f"### {s['name']}\n")
            for t in s["tools"]:
                w(f"- {PRICING[t['price']]} [{t['name']}]({t['url']}) - {t['desc']}")
            w("")

    # defunct
    w("## Defunct, Renamed & Acquired\n")
    w(
        "Older awesome-lists are full of tools that no longer exist or changed names. "
        "This table is what was fixed while merging.\n"
    )
    w("| Old name | Status | Use instead |")
    w("|---|---|---|")
    for old, status, new in [
        ("Google Optimize", "Shut down Sept 30, 2023", "VWO, Optimizely, GrowthBook, PostHog Experiments, Statsig"),
        ("Google Data Studio", "Renamed", "Looker Studio"),
        ("Google Surveys", "Shut down 2023", "Google Forms, Typeform, Tally"),
        ("Pocket", "Shut down by Mozilla, July 2025", "Raindrop.io, Readwise, Pinboard"),
        ("HARO / Connectively", "Shut down Dec 2024", "Qwoted, Featured, Source of Sources, Help a B2B Writer"),
        ("Semrush Prowly", "Phased out Dec 2025", "Muck Rack, Prezly, Cision"),
        ("CrowdTangle", "Shut down by Meta, Aug 2024", "Meta Content Library, Brandwatch, Sprout Social"),
        ("Revue (Twitter)", "Shut down Jan 2023", "Substack, beehiiv, Buttondown"),
        ("TinyLetter", "Shut down 2024", "Mailchimp, Buttondown, beehiiv, Substack"),
        ("Perfect Audience", "Shut down 2019", "AdRoll, Criteo, platform-native retargeting"),
        ("MediaMath", "Bankrupt 2023, assets sold", "The Trade Desk, DV360"),
        ("Integromat", "Renamed", "Make"),
        ("Automate.io", "Shut down", "Zapier, Make, n8n"),
        ("Adobe Spark", "Rebranded", "Adobe Express"),
        ("Sendinblue", "Renamed 2023", "Brevo"),
        ("ConvertKit", "Renamed 2024", "Kit"),
        ("Autopilot", "Renamed", "Ortto"),
        ("Revealbot", "Renamed", "Bïrch"),
        ("AspireIQ", "Renamed", "Aspire"),
        ("Infusionsoft", "Renamed", "Keap"),
        ("Pardot", "Renamed", "Marketing Cloud Account Engagement"),
        ("DeepCrawl", "Renamed", "Lumar"),
        ("ContentKing", "Acquired by Conductor", "Conductor Monitoring"),
        ("Kompyte", "Acquired by Semrush", "Semrush, Crayon, Klue"),
        ("Clearbit (free tools)", "Acquired by HubSpot; now Breeze Intelligence", "Apollo, Clay, People Data Labs"),
        ("Drift", "Acquired by Salesloft", "Intercom, Qualified, HubSpot chat"),
        ("TweetDeck", "Became X Pro (paywalled)", "Typefully, Buffer, Hypefury"),
        ("Alexa Traffic Rank", "Shut down 2022", "Similarweb, Semrush"),
        ("Periscope / Meerkat / Blab", "Shut down", "YouTube Live, LinkedIn Live, StreamYard"),
        ("Google Analytics (Universal)", "Sunset July 2024", "Google Analytics 4, Plausible, Matomo, PostHog"),
    ]:
        w(f"| {old} | {status} | {new} |")
    w("")

    w("## Contributing\n")
    w("1. Edit `data/tools.txt` (one tool per line: `Name | url | F/M/P/O | description`).")
    w("2. Run `python3 scripts/build.py` to regenerate this README and `tools.csv`.")
    w("3. Optional: `python3 scripts/check_links.py` to find dead links before committing.\n")
    w("**Inclusion rules:** the tool must be live and useful on its own merits; no pay-to-play entries; "
      "prefer one best-in-class entry per job over ten near-duplicates; note if it is free or open source.\n")
    w("## Sources & Method\n")
    w(
        "Merged and de-duplicated from 21 lists (see *Related Awesome Lists* above); tools that several "
        "independent lists agree on were prioritized, then everything was curated by hand. Added current AI-search tools, open-source "
        "alternatives, and 2025–2026 changes the older lists missed. Link health is checked with "
        "`scripts/check_links.py`.\n"
    )
    w("## License\n")
    w("[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/): do whatever you like with this list.\n")

    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")

    with open(ROOT / "tools.csv", "w", newline="", encoding="utf-8") as f:
        cw = csv.writer(f)
        cw.writerow(["category", "subcategory", "name", "url", "pricing", "description"])
        for c in cats:
            for s in c["subs"]:
                for t in s["tools"]:
                    cw.writerow([c["name"], s["name"], t["name"], t["url"], PRICING_NAME[t["price"]], t["desc"]])
    print(f"built README.md + tools.csv: {total} tools, {len(cats)} categories")


if __name__ == "__main__":
    main()
