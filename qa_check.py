#!/usr/bin/env python3
"""Static release checks for the public GitHub Pages site."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

html_files = sorted(p for p in ROOT.glob("*.html") if not re.match(r"^(?:google|yandex).*\.html$", p.name))
check(bool(html_files), "No HTML pages found")
pages = {p.name: p.read_text(encoding="utf-8") for p in html_files}
home = pages.get("index.html", "")
privacy = pages.get("privacy.html", "")
calculator = pages.get("calculator.html", "")
check('id="hours"' in calculator and 'id="hourly"' in calculator, "Calculator hourly estimate fields missing")
check("net/v.hours" in calculator, "Calculator hourly net calculation missing")
city_js = ROOT / "city.js"

check("<h1" in home.lower(), "Homepage is missing H1")
check('name="description"' in home, "Homepage is missing meta description")
check('name="keywords"' in home, "Homepage is missing keyword meta")
check("не является официальным сайтом" in home.lower(), "Homepage disclaimer missing")
check("https://vkusvill.ru/job/courier/" in home, "Official courier link missing")
check("https://wa.me/79201461682" in home and "https://t.me/daaaggg1" in home, "Contact links missing")
check("<form" not in home.lower(), "Unexpected data-collection form in homepage")
check("не предусмотрены анкеты" in privacy.lower(), "Privacy notice about no forms missing")
check("ipapi.co" in privacy and "локальном хранилище" in privacy.lower(), "City-detection privacy notice missing")
check(city_js.is_file(), "Missing city.js")
check((ROOT / "styles.css").is_file(), "Missing styles.css")

if city_js.is_file():
    js = city_js.read_text(encoding="utf-8")
    check("https://ipapi.co/json/" in js, "IP city lookup missing")
    check("kurierStartCity" in js, "Manual city persistence missing")
    check("city-personal-text" in js, "City-specific page content missing")
    check("wa.me/79201461682" in js, "City-prefilled WhatsApp link missing")

for filename, source in pages.items():
    if filename not in ("privacy.html", "404.html"):
        check('name="robots" content="noindex' not in source, f"{filename}: unexpected noindex")
        check('rel="canonical"' in source, f"{filename}: canonical missing")
    check('src="city.js' in source, f"{filename}: city.js not included")
    for match in re.finditer(r'<a\b([^>]*target="_blank"[^>]*)>', source, re.I):
        check("noopener" in match.group(1), f"{filename}: unsafe target=_blank link")
    for href in re.findall(r'<(?:a|link)\b[^>]*href=["\']([^"\']+)["\']', source, re.I):
        if href.startswith(("#", "https://", "http://", "mailto:", "tel:", "data:", "javascript:")):
            continue
        local = href.split("#", 1)[0].split("?", 1)[0]
        if local:
            check((ROOT / local).is_file(), f"{filename}: broken local link {href}")

sitemap = ROOT / "sitemap.xml"
check(sitemap.is_file(), "Missing sitemap.xml")
if sitemap.is_file():
    try:
        root = ET.parse(sitemap).getroot()
        for loc in root.findall(".//{*}loc"):
            url = (loc.text or "").strip()
            if "/kurier-start/" in url:
                path = url.split("/kurier-start/", 1)[1]
                target = ROOT / (path or "index.html")
                check(target.is_file(), f"Sitemap points to missing file: {url}")
    except ET.ParseError as exc:
        check(False, f"Invalid sitemap.xml: {exc}")

if errors:
    print("FAIL")
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(pages)} HTML pages, city personalization, local links and sitemap")
