"""Funciones de auto-descubrimiento para documentos japoneses.

Este módulo contiene scrapers automáticos que buscan nuevos documentos
en las páginas oficiales del gobierno japonés, en múltiples idiomas.
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JapanStrategyMonitor/2.0)"}
TIMEOUT = 30


def fetch_soup(url):
    """Fetch and parse HTML from URL."""
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def discover_defense_white_papers():
    """Scrape MOD website for Defense White Papers in EN and JA.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []
    
    # English version
    url_en = "https://www.mod.go.jp/en/publ/w_paper/index.html"
    try:
        soup = fetch_soup(url_en)
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True)
            match = re.search(r"DEFENSE OF JAPAN (\d{4})", text)
            if match:
                year = int(match.group(1))
                section = heading.find_parent(["div", "section"])
                if section:
                    links = section.find_all("a", href=re.compile(r"DOJ.*\.pdf|wp.*index\.html"))
                    for link in links:
                        href = link.get("href", "")
                        if "_EN" in href or "english" in href.lower() or ".pdf" in href.lower():
                            url_doc = href if href.startswith("http") else f"https://www.mod.go.jp{href}"
                            documents.append({
                                "year": year,
                                "url": url_doc,
                                "title": f"Defense of Japan {year}",
                                "lang": "en",
                                "organization": "MOD",
                                "category": "defense_white_paper"
                            })
                            break
    except Exception as e:
        print(f"Error scraping Defense White Papers (EN): {e}")
    
    # Japanese version
    url_ja = "https://www.mod.go.jp/j/publication/wp/index.html"
    try:
        soup = fetch_soup(url_ja)
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True)
            # Look for 防衛白書 or 令和XX年
            match = re.search(r"令和(\d+)年|防衛白書.*(\d{4})", text)
            if match:
                if match.group(1):  # 令和 year
                    # Convert Reiwa to Western year (令和元年 = 2019)
                    reiwa_year = int(match.group(1))
                    year = 2018 + reiwa_year if reiwa_year > 1 else 2019
                elif match.group(2):  # Western year
                    year = int(match.group(2))
                else:
                    continue
                    
                section = heading.find_parent(["div", "section"])
                if section:
                    links = section.find_all("a", href=re.compile(r"\.pdf|/wp/"))
                    for link in links:
                        href = link.get("href", "")
                        if href and ("_JP" in href or "j/" in href or ".pdf" in href):
                            url_doc = href if href.startswith("http") else f"https://www.mod.go.jp{href}"
                            documents.append({
                                "year": year,
                                "url": url_doc,
                                "title": f"防衛白書 {year}",
                                "lang": "ja",
                                "organization": "MOD",
                                "category": "defense_white_paper"
                            })
                            break
    except Exception as e:
        print(f"Error scraping Defense White Papers (JA): {e}")
    
    return documents


def discover_diplomatic_bluebooks():
    """Scrape MOFA website for Diplomatic Bluebooks in EN and JA.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []
    
    # English version
    url_en = "https://www.mofa.go.jp/policy/other/bluebook/index.html"
    try:
        soup = fetch_soup(url_en)
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                title_cell = cells[0]
                # Look for "DIPLOMATIC BLUEBOOK 2025" pattern
                title_text = title_cell.get_text(strip=True)
                match = re.search(r"DIPLOMATIC BLUEBOOK (\d{4})", title_text, re.IGNORECASE)
                if match:
                    year = int(match.group(1))
                    # Find English links
                    links = title_cell.find_all("a")
                    for link in links:
                        link_text = link.get_text(strip=True).lower()
                        if "english" in link_text or "html" in link_text:
                            href = link.get("href", "")
                            if href:
                                url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                                documents.append({
                                    "year": year,
                                    "url": url_doc,
                                    "title": f"Diplomatic Bluebook {year}",
                                    "lang": "en",
                                    "organization": "MOFA",
                                    "category": "diplomatic_bluebook"
                                })
                                break
    except Exception as e:
        print(f"Error scraping Diplomatic Bluebooks (EN): {e}")
    
    # Japanese version
    url_ja = "https://www.mofa.go.jp/mofaj/gaiko/bluebook/index.html"
    try:
        soup = fetch_soup(url_ja)
        # Look for links with 外交青書 pattern
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"(令和|平成)(\d+)年.*外交青書|外交青書.*(\d{4})", link_text)
            if match:
                if match.group(2):  # Era year
                    era_year = int(match.group(2))
                    if "令和" in link_text:
                        year = 2018 + era_year if era_year > 1 else 2019
                    elif "平成" in link_text:
                        year = 1988 + era_year
                    else:
                        continue
                elif match.group(3):  # Western year
                    year = int(match.group(3))
                else:
                    continue
                
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                    # Avoid duplicates
                    if not any(d["year"] == year and d["lang"] == "ja" for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"外交青書 {year}",
                            "lang": "ja",
                            "organization": "MOFA",
                            "category": "diplomatic_bluebook"
                        })
    except Exception as e:
        print(f"Error scraping Diplomatic Bluebooks (JA): {e}")
    
    return documents


def discover_nids_china_reports():
    """Scrape NIDS website for China Security Reports in EN, JA, and CH.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []
    url = "https://www.nids.mod.go.jp/english/publication/chinareport/index.html"
    
    try:
        soup = fetch_soup(url)
        
        # Find all year headings "China Security Report XXXX"
        for heading in soup.find_all(["h2", "h3", "h4"]):
            text = heading.get_text(strip=True)
            match = re.search(r"China Security Report (\d{4})", text)
            if match:
                year = int(match.group(1))
                
                # Find the subtitle/theme
                next_elem = heading.find_next_sibling()
                subtitle = ""
                if next_elem and next_elem.name in ["p", "h5"]:
                    subtitle = next_elem.get_text(strip=True)
                
                # Find PDF links in the section
                section = heading.find_next(["div", "section"])
                if not section:
                    section = heading.find_parent(["div", "section"])
                
                if section:
                    # Look for language-specific PDFs
                    links = section.find_all("a", href=re.compile(r".*_EN.*\.pdf|.*english.*\.pdf|.*\.pdf"))
                    
                    # English version
                    for link in links:
                        href = link.get("href", "")
                        if "_EN" in href or "english" in href.lower():
                            url_doc = href if href.startswith("http") else f"https://www.nids.mod.go.jp{href}"
                            documents.append({
                                "year": year,
                                "url": url_doc,
                                "title": f"China Security Report {year}" + (f": {subtitle}" if subtitle else ""),
                                "lang": "en",
                                "organization": "NIDS",
                                "category": "nids_china_report"
                            })
                            break
    except Exception as e:
        print(f"Error scraping NIDS China Reports (EN): {e}")
    
    # Try Japanese version
    url_ja = "https://www.nids.mod.go.jp/publication/chinareport/index.html"
    try:
        soup = fetch_soup(url_ja)
        for heading in soup.find_all(["h2", "h3", "h4"]):
            text = heading.get_text(strip=True)
            match = re.search(r"中国安全保障レポート.*(\d{4})|.*(\d{4}).*中国", text)
            if match:
                year = int(match.group(1) or match.group(2))
                section = heading.find_next(["div", "section"])
                if not section:
                    section = heading.find_parent(["div", "section"])
                if section:
                    links = section.find_all("a", href=re.compile(r"\.pdf"))
                    for link in links:
                        href = link.get("href", "")
                        if "_JP" in href or "j/" in href or (".pdf" in href and "_EN" not in href):
                            url_doc = href if href.startswith("http") else f"https://www.nids.mod.go.jp{href}"
                            if not any(d["year"] == year and d["lang"] == "ja" for d in documents):
                                documents.append({
                                    "year": year,
                                    "url": url_doc,
                                    "title": f"中国安全保障レポート {year}",
                                    "lang": "ja",
                                    "organization": "NIDS",
                                    "category": "nids_china_report"
                                })
                                break
    except Exception as e:
        print(f"Error scraping NIDS China Reports (JA): {e}")
    
    # Try Chinese version - typically linked from English page
    try:
        soup = fetch_soup(url)  # Back to English page
        for heading in soup.find_all(["h2", "h3", "h4"]):
            text = heading.get_text(strip=True)
            match = re.search(r"China Security Report (\d{4})", text)
            if match:
                year = int(match.group(1))
                section = heading.find_next(["div", "section"])
                if not section:
                    section = heading.find_parent(["div", "section"])
                if section:
                    # Look for Chinese version link
                    chinese_heading = section.find(string=re.compile(r"Chinese Version", re.IGNORECASE))
                    if chinese_heading:
                        parent = chinese_heading.find_parent(["p", "div", "h5"])
                        if parent:
                            links = parent.find_all("a", href=re.compile(r"\.pdf"))
                            for link in links:
                                href = link.get("href", "")
                                url_doc = href if href.startswith("http") else f"https://www.nids.mod.go.jp{href}"
                                if not any(d["year"] == year and d["lang"] == "zh" for d in documents):
                                    documents.append({
                                        "year": year,
                                        "url": url_doc,
                                        "title": f"中国安全保障报告 {year}",
                                        "lang": "zh",
                                        "organization": "NIDS",
                                        "category": "nids_china_report"
                                    })
                                    break
    except Exception as e:
        print(f"Error scraping NIDS China Reports (ZH): {e}")
    
    return documents


def discover_oda_white_papers():
    """Scrape MOFA website for ODA/Development Cooperation White Papers.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []
    
    # English version
    url_en = "https://www.mofa.go.jp/policy/oda/white/index.html"

    # Note: Cybersecurity Strategy, FOIP, Economic Security, and Gender Equality documents
# have stable URLs and are infrequently updated, so they are kept in the manual corpus.
# If needed, similar scraper functions can be added here following the same pattern.


    try:
        soup = fetch_soup(url_en)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            href = link.get("href", "")
            # Look for year patterns
            match = re.search(r"(\d{4})", link_text)
            if match and ("white paper" in link_text.lower() or "development cooperation" in link_text.lower()):
                year = int(match.group(1))
                if year >= 2015:  # Only recent years
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                    if not any(d["year"] == year and d["lang"] == "en" for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"Development Cooperation White Paper {year}",
                            "lang": "en",
                            "organization": "MOFA",
                            "category": "oda_white_paper"
                        })
    except Exception as e:
        print(f"Error scraping ODA White Papers (EN): {e}")
    
    # Japanese version
    url_ja = "https://www.mofa.go.jp/mofaj/gaiko/oda/shiryo/hakusyo.html"
    try:
        soup = fetch_soup(url_ja)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            href = link.get("href", "")
            match = re.search(r"(令和|平成)(\d+)年|ODA白書.*(\d{4})", link_text)
            if match:
                if match.group(2):  # Era year
                    era_year = int(match.group(2))
                    if "令和" in link_text:
                        year = 2018 + era_year if era_year > 1 else 2019
                    elif "平成" in link_text:
                        year = 1988 + era_year
                    else:
                        continue
                elif match.group(3):  # Western year
                    year = int(match.group(3))
                else:
                    continue
                
                if year >= 2015:  # Only recent years
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                    if not any(d["year"] == year and d["lang"] == "ja" for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"ODA白書 {year}",
                            "lang": "ja",
                            "organization": "MOFA",
                            "category": "oda_white_paper"
                        })
    except Exception as e:
        print(f"Error scraping ODA White Papers (JA): {e}")
    
    return documents


def get_latest_years(documents):
    """Get latest year for each category.
    
    Args:
        documents: List of document dicts
    
    Returns:
        dict: Dictionary with category -> latest year mapping
    """
    latest = {}
    for doc in documents:
        category = doc.get("category", "unknown")
        year = doc.get("year", 0)
        if category not in latest or year > latest[category]:
            latest[category] = year
    return latest


if __name__ == "__main__":
    print("=== Auto-discovering Japanese Strategy Documents ===")
    
    print("\n1. Defense White Papers:")
    defense = discover_defense_white_papers()
    for doc in sorted(defense, key=lambda x: (x["year"], x["lang"]), reverse=True)[:6]:
        print(f"  {doc['year']} ({doc['lang'].upper()}): {doc['title']}")
    
    print("\n2. Diplomatic Bluebooks:")
    bluebooks = discover_diplomatic_bluebooks()
    for doc in sorted(bluebooks, key=lambda x: (x["year"], x["lang"]), reverse=True)[:6]:
        print(f"  {doc['year']} ({doc['lang'].upper()}): {doc['title']}")
    
    print("\n3. NIDS China Reports:")
    nids = discover_nids_china_reports()
    for doc in sorted(nids, key=lambda x: (x["year"], x["lang"]), reverse=True)[:9]:
        print(f"  {doc['year']} ({doc['lang'].upper()}): {doc['title']}")
    
    print("\n4. ODA White Papers:")
    oda = discover_oda_white_papers()
    for doc in sorted(oda, key=lambda x: (x["year"], x["lang"]), reverse=True)[:6]:
        print(f"  {doc['year']} ({doc['lang'].upper()}): {doc['title']}")
    
    print("\n5. Latest Years Detected:")
    all_docs = defense + bluebooks + nids + oda
    latest = get_latest_years(all_docs)
    for category, year in sorted(latest.items()):
        category_name = category.replace("_", " ").title()
        print(f"  {category_name}: {year}")
    
    print(f"\nTotal documents found: {len(all_docs)} across all categories and languages")



def discover_cybersecurity_strategy():
    """Scrape NISC website for the current Cybersecurity Strategy (EN and JA).

    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []

    url_en = "https://www.nisc.go.jp/eng/index.html"
    try:
        soup = fetch_soup(url_en)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"Cybersecurity Strategy.*?(\d{4})", link_text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                href = link.get("href", "")
                if href and ".pdf" in href.lower():
                    url_doc = href if href.startswith("http") else f"https://www.nisc.go.jp{href}"
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": f"Cybersecurity Strategy ({year})",
                        "lang": "en",
                        "organization": "NISC",
                        "category": "cybersecurity_strategy"
                    })
    except Exception as e:
        print(f"Error scraping Cybersecurity Strategy (EN): {e}")

    url_ja = "https://www.nisc.go.jp/index.html"
    try:
        soup = fetch_soup(url_ja)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"サイバーセキュリティ戦略.*?(\d{4})", link_text)
            if match:
                year = int(match.group(1))
                href = link.get("href", "")
                if href and ".pdf" in href.lower():
                    url_doc = href if href.startswith("http") else f"https://www.nisc.go.jp{href}"
                    if not any(d["year"] == year and d["lang"] == "ja" for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"サイバーセキュリティ戦略（{year}年）",
                            "lang": "ja",
                            "organization": "NISC",
                            "category": "cybersecurity_strategy"
                        })
    except Exception as e:
        print(f"Error scraping Cybersecurity Strategy (JA): {e}")

    return documents


def discover_economic_security():
    """Scrape METI website for Economic Security Promotion Act updates.

    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []
    url = "https://www.meti.go.jp/policy/economy/economic_security/index.html"

    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"(20\d{2})", link_text)
            if match and ("economic security" in link_text.lower() or "経済安全保障" in link_text):
                year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    lang = "ja" if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", link_text) else "en"
                    url_doc = href if href.startswith("http") else f"https://www.meti.go.jp{href}"
                    if not any(d["year"] == year and d["lang"] == lang for d in documents):
                        title = f"経済安全保障推進法（{year}年）" if lang == "ja" else f"Economic Security Promotion Act ({year})"
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": title,
                            "lang": lang,
                            "organization": "METI",
                            "category": "economic_security"
                        })
    except Exception as e:
        print(f"Error scraping Economic Security updates: {e}")

    return documents


def discover_gender_equality_plans():
    """Scrape Gender Equality Bureau / Cabinet Office for Basic Plans (EN and JA).

    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []

    url_en = "https://www.gender.go.jp/english_contents/index.html"
    try:
        soup = fetch_soup(url_en)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"Basic Plan for Gender Equality.*?(\d{4})", link_text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.gender.go.jp{href}"
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": link_text,
                        "lang": "en",
                        "organization": "Gabinete",
                        "category": "gender_equality_plan"
                    })
    except Exception as e:
        print(f"Error scraping Gender Equality Plans (EN): {e}")

    url_ja = "https://www.gender.go.jp/about_danjo/basic_plans/index.html"
    try:
        soup = fetch_soup(url_ja)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"男女共同参画基本計画.*?(\d{4})|第(\d+)次男女共同参画基本計画", link_text)
            if match:
                href = link.get("href", "")
                if not href:
                    continue
                year_match = re.search(r"(20\d{2})", link_text)
                if not year_match:
                    continue
                year = int(year_match.group(1))
                url_doc = href if href.startswith("http") else f"https://www.gender.go.jp{href}"
                if not any(d["year"] == year and d["lang"] == "ja" for d in documents):
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": link_text,
                        "lang": "ja",
                        "organization": "Gabinete",
                        "category": "gender_equality_plan"
                    })
    except Exception as e:
        print(f"Error scraping Gender Equality Plans (JA): {e}")

    return documents


def discover_foip():
    """Scrape MOFA website for Free and Open Indo-Pacific (FOIP) updates.

    Returns:
        list: Lista de dict con {"year": int, "url": str, "title": str, "lang": str}
    """
    documents = []

    url_en = "https://www.mofa.go.jp/policy/page1e_000278.html"
    try:
        soup = fetch_soup(url_en)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"Free and Open Indo-Pacific.*?(\d{4})", link_text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": link_text,
                        "lang": "en",
                        "organization": "MOFA",
                        "category": "foip"
                    })
    except Exception as e:
        print(f"Error scraping FOIP (EN): {e}")

    return documents
