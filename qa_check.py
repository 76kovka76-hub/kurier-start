#!/usr/bin/env python3
"""Static release checks for the public GitHub Pages site."""
from pathlib import Path
import re
import json
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
css_text = (ROOT / "styles.css").read_text(encoding="utf-8")
check('id="hours"' in calculator and 'id="hourly"' in calculator and 'id="days"' in calculator, "Calculator hourly and daily estimate fields missing")
check("net/v.hours" in calculator, "Calculator hourly net calculation missing")
check("fuelCost,serviceCost,total,net,daily,monthEstimate" in calculator and "Number.isFinite(hourlyNet)" in calculator and "числовой диапазон" in calculator, "Calculator must guard against numeric overflow")
check('id="calc-status"' in calculator and "Расходы превышают выплаты" in calculator, "Calculator negative-balance warning missing")
check(calculator.count("required>") >= 9 and 'aria-invalid' in calculator and "Расчёт временно недоступен" in calculator, "Calculator must reject blank and invalid inputs")
check('id="mode"' in calculator and 'option value="bike"' in calculator and 'mode==="car"' in calculator, "Calculator must support car and bicycle modes")
check('id="month-estimate"' in calculator and "daily*30" in calculator and "monthEstimate].every(Number.isFinite)" in calculator, "Calculator monthly equivalent estimate missing or unguarded")
check(chr(92) + "n" not in calculator, "Calculator script contains a literal escaped newline")
check(calculator.count("const daily=net/v.days;") == 1, "Calculator daily estimate must be declared exactly once")
check('input[aria-invalid="true"]' in css_text, "Invalid calculator inputs must be visually highlighted")
city_js = ROOT / "city.js"

check("<h1" in home.lower(), "Homepage is missing H1")
check('name="description"' in home, "Homepage is missing meta description")
h1_match = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", home, re.I)
h1_text = re.sub(r"<[^>]+>", " ", h1_match.group(1)) if h1_match else ""
check("Работа курьером во ВкусВилл" in h1_text, "Homepage H1 must target the main courier-work search phrase")

check('name="keywords"' in home, "Homepage is missing keyword meta")
check("hero-intro" in home and "trust-strip" in home, "Homepage value proposition and trust summary missing")
check('href="cities.html"' in home and 'href="earnings.html"' in home, "Homepage must link to city and earnings guides")
check("fonts.googleapis.com" not in home and "fonts.googleapis.com" not in calculator, "External font stylesheet should not block rendering")
check("не является официальным сайтом" in home.lower(), "Homepage disclaimer missing")
check(all("href=\\"https://vkusvill.ru/" not in source for source in pages.values()) and "vkusvill.ru" not in city_js.read_text(encoding="utf-8"), "Unexpected outbound links to employer site")
check("https://wa.me/79201461682" in home and "https://t.me/daaaggg1" in home, "Contact links missing")
check("Узнай, где проверить<br>вакансии в своём городе" in home and "Контакт для связи по вопросам вакансий. Это не официальная служба поддержки ВкусВилл." in home, "Homepage must clearly distinguish independent contact from official hiring")
check("<form" not in home.lower(), "Unexpected data-collection form in homepage")
check("на сайте нет анкет, форм заявок и регистрации" in privacy.lower(), "Privacy notice about no forms missing")
check("ipapi.co" in privacy and "локальном хранилище" in privacy.lower(), "City-detection privacy notice missing")
check(city_js.is_file(), "Missing city.js")
check((ROOT / "styles.css").is_file(), "Missing styles.css")
check("scroll-padding-top:122px" in css_text, "Mobile anchor offset missing")
for filename in ("guide.html", "auto.html", "bike.html", "calculator.html", "cities.html", "earnings.html"):
    source = pages.get(filename, "")
    nav_match = re.search(r'<nav class="main-nav"[^>]*>(.*?)</nav>', source, re.S)
    check(bool(nav_match), f"{filename}: primary navigation missing")
    breadcrumb = re.search(r'<nav class="breadcrumbs" aria-label="Хлебные крошки">(.*?)</nav>', source, re.S)
    check(bool(breadcrumb) and 'href="index.html"' in breadcrumb.group(1) and 'aria-current="page"' in breadcrumb.group(1), f"{filename}: visible breadcrumb navigation missing or incomplete")
    if nav_match:
        nav = nav_match.group(1)
        for target in ("index.html#directions", "guide.html", "auto.html", "bike.html", "calculator.html"):
            check(f'href="{target}"' in nav, f"{filename}: primary navigation missing {target}")
        check(f'href="{filename}" aria-current="page"' in nav, f"{filename}: current page is not identified in navigation")
check("scrollbar-width:thin" in css_text and "scroll-snap-type:x proximity" in css_text, "Mobile navigation scroll affordance missing")
check("@media(prefers-reduced-motion:reduce)" in css_text and "scroll-behavior:auto" in css_text, "Reduced-motion support missing")
check("@import url('https://fonts.googleapis.com'" not in (ROOT / "styles.css").read_text(encoding="utf-8"), "Google Font import must not be late in CSS")
check(re.search(r"^body\s*\{[^}]*font:\s*15px/1\.6\s+system-ui", css_text, re.M) is not None, "Body must use a fast system font stack")
for filename, source in pages.items():
    check("fonts.googleapis.com" not in source and "fonts.gstatic.com" not in source, f"{filename}: external font dependency should be removed for faster rendering")

if city_js.is_file():
    js = city_js.read_text(encoding="utf-8")
    check("https://ipapi.co/json/" in js, "IP city lookup missing")
    check("AbortController()" in js and "clearTimeout(timeoutId)" in js and "6000" in js, "IP city lookup must have a six-second timeout")
    check('if (!city) throw new Error("City unavailable")' in js, "IP lookup must not treat region-only data as a city")
    check("kurierStartCity" in js, "Manual city persistence missing")
    check("city-personal-text" in js, "City-specific page content missing")
    check('aria-live="polite"' in js and 'aria-atomic="true"' in js, "City changes must be announced to assistive technology")
    check('aria-expanded' in js and 'aria-controls="city-edit"' in js, "City selector toggle accessibility attributes missing")
    check('changeButton.focus()' in js, "Focus is not returned after saving city")
    check("wa.me/79201461682" in js, "City-prefilled WhatsApp link missing")
    check("Контакт на этом сайте независимый и не подтверждает трудоустройство" in js, "City information must distinguish independent contact from hiring authority")
    check("где проверить актуальные вакансии курьеров и официальные условия" in js, "WhatsApp city message must direct users to official vacancy information")

# Ensure homepage FAQ structured data stays aligned with visible questions.
homepage = pages.get("index.html", "")
# Remove structured-data scripts before checking that FAQ answers are actually visible.
visible_homepage = re.sub(r'<script\b[^>]*>.*?</script>', '', homepage, flags=re.I | re.S)
for schema_match in re.finditer(r'<script\s+type="application/ld\+json">([\s\S]*?)</script>', homepage, re.I):
    try:
        schema_data = json.loads(schema_match.group(1))
    except json.JSONDecodeError:
        continue
    graph = schema_data.get("@graph", []) if isinstance(schema_data, dict) else []
    for item in graph:
        if item.get("@type") != "FAQPage":
            continue
        for question in item.get("mainEntity", []):
            name = question.get("name", "")
            answer = question.get("acceptedAnswer", {}).get("text", "")
            check(bool(name) and name in visible_homepage, f"Homepage FAQ schema question is not visible: {name}")
            check(bool(answer) and answer in visible_homepage, f"Homepage FAQ schema answer is out of sync with visible content: {name}")

# Keep search snippets distinct and prevent accidental duplicate page titles.
seo_titles = []
seo_descriptions = []
for filename, source in pages.items():
    if filename in ("privacy.html", "404.html"):
        continue
    title_match = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
    description_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', source, re.I)
    check(bool(title_match), f"{filename}: page title missing")
    check(bool(description_match), f"{filename}: meta description missing")
    if title_match:
        seo_titles.append((filename, re.sub(r"\s+", " ", title_match.group(1)).strip()))
    if description_match:
        seo_descriptions.append((filename, description_match.group(1).strip()))
check(len({value for _, value in seo_titles}) == len(seo_titles), "Indexable pages must have unique titles")
check(len({value for _, value in seo_descriptions}) == len(seo_descriptions), "Indexable pages must have unique meta descriptions")
# Every supporting page should answer real candidate questions in visible, crawlable text.
faq_expectations = {
    "guide.html": ("Частые вопросы перед откликом", "Где проверить, есть ли набор в моём городе?"),
    "auto.html": ("Частые вопросы о работе на своём авто", "Какие расходы нужно вычесть из выплат?"),
    "bike.html": ("Частые вопросы о доставке на велосипеде", "Подойдёт ли обычный велосипед?"),
    "calculator.html": ("Частые вопросы о калькуляторе", "Сохраняются ли введённые данные?"),
}
for filename, phrases in faq_expectations.items():
    source = pages.get(filename, "")
    for phrase in phrases:
        check(phrase in source, f"{filename}: useful FAQ content missing: {phrase}")
    check(len(re.findall(r"<details>", source, re.I)) >= 3, f"{filename}: expected at least three visible FAQ answers")
    if filename == "guide.html":
        check("Как проверить надёжность предложения" in source and "Не плати за обещание гарантированного трудоустройства" in source, "Guide must include practical recruitment-scam safety guidance")
        check("Нужно ли платить за трудоустройство курьером?" in source, "Guide must answer whether candidates should pay for recruitment")


for filename, source in pages.items():
    if filename not in ("privacy.html", "404.html"):
        check('name="robots" content="noindex' not in source, f"{filename}: unexpected noindex")
        title_match = re.search(r"<title>([\s\S]*?)</title>", source, re.I)
        desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', source, re.I)
        if title_match:
            check(25 <= len(re.sub(r"\s+", " ", title_match.group(1)).strip()) <= 70, f"{filename}: title length should be useful in search results")
        if desc_match:
            check(90 <= len(desc_match.group(1)) <= 170, f"{filename}: meta description length should be 90–170 characters")
        for schema_match in re.finditer(r'<script\s+type="application/ld\+json">([\s\S]*?)</script>', source, re.I):
            try:
                json.loads(schema_match.group(1))
            except json.JSONDecodeError as exc:
                check(False, f"{filename}: invalid JSON-LD structured data: {exc}")

        check('rel="canonical"' in source, f"{filename}: canonical missing")
        check('property="og:url"' in source, f"{filename}: Open Graph URL missing")
        if filename in ("guide.html", "auto.html", "bike.html", "calculator.html", "cities.html", "earnings.html"):
            check('"@type": "BreadcrumbList"' in source and '"itemListElement"' in source, f"{filename}: breadcrumb structured data missing")
        check('name="twitter:card"' in source and 'name="twitter:title"' in source and 'name="twitter:description"' in source, f"{filename}: social preview metadata incomplete")
    check('src="city.js' in source, f"{filename}: city.js not included")
    check('class="skip-link"' in source and ('<main id="main-content"' in source or '<main id="top"' in source), f"{filename}: keyboard skip navigation missing")
    for match in re.finditer(r'<a\b([^>]*target="_blank"[^>]*)>', source, re.I):
        check("noopener" in match.group(1), f"{filename}: unsafe target=_blank link")
    for href in re.findall(r'<(?:a|link)\b[^>]*href=["\']([^"\']+)["\']', source, re.I):
        if href.startswith(("#", "https://", "http://", "mailto:", "tel:", "data:", "javascript:")):
            continue
        local = href.split("#", 1)[0].split("?", 1)[0]
        if local:
            check((ROOT / local).is_file(), f"{filename}: broken local link {href}")


# Validate in-page and cross-page fragment links, not only file existence.
page_ids = {
    filename: set(re.findall(r'\bid=["\']([^"\']+)["\']', source))
    for filename, source in pages.items()
}
for filename, source in pages.items():
    found_ids = re.findall(r'\bid=["\']([^"\']+)["\']', source)
    check(len(found_ids) == len(set(found_ids)), f"{filename}: duplicate HTML id")
    for href in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']', source, re.I):
        if "#" not in href or href.startswith(("https://", "http://", "mailto:", "tel:")):
            continue
        target_file, fragment = href.split("#", 1)
        target_name = target_file.split("?", 1)[0] or filename
        if target_name in pages and fragment:
            check(fragment in page_ids[target_name], f"{filename}: broken fragment link {href}")

sitemap = ROOT / "sitemap.xml"
check(sitemap.is_file(), "Missing sitemap.xml")
if sitemap.is_file():
    try:
        root = ET.parse(sitemap).getroot()
        sitemap_urls = []
        for loc in root.findall(".//{*}loc"):
            url = (loc.text or "").strip()
            sitemap_urls.append(url)
            if "/kurier-start/" in url:
                path = url.split("/kurier-start/", 1)[1]
                target = ROOT / (path or "index.html")
                check(target.is_file(), f"Sitemap points to missing file: {url}")
                canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', pages.get(path or "index.html", ""), re.I)
                check(bool(canonical) and canonical.group(1) == url, f"Sitemap URL and canonical URL differ: {url}")
        expected_sitemap = {
            "https://76kovka76-hub.github.io/kurier-start/",
            "https://76kovka76-hub.github.io/kurier-start/guide.html",
            "https://76kovka76-hub.github.io/kurier-start/auto.html",
            "https://76kovka76-hub.github.io/kurier-start/bike.html",
            "https://76kovka76-hub.github.io/kurier-start/calculator.html",
        }
        expected_sitemap.update({"https://76kovka76-hub.github.io/kurier-start/cities.html", "https://76kovka76-hub.github.io/kurier-start/earnings.html"})
        check(set(sitemap_urls) == expected_sitemap, "Sitemap must list exactly the seven canonical indexable pages")
        check(len(sitemap_urls) == len(set(sitemap_urls)), "Sitemap contains duplicate URLs")
    except ET.ParseError as exc:
        check(False, f"Invalid sitemap.xml: {exc}")

if errors:
    print("FAIL")
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(pages)} HTML pages, city personalization, local links and sitemap")
