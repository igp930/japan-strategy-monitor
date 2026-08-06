"""Funciones de auto-descubrimiento para documentos japoneses.

Este modulo contiene scrapers automaticos que buscan nuevos documentos
en las paginas oficiales del gobierno japones, en multiples idiomas.

Todas las funciones publicas devuelven una lista de dicts con:
{"year": int, "url": str, "title": str, "lang": str, "organization": str, "category": str}
No reciben argumentos, y cada llamada crea su propia lista de resultados.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}
TIMEOUT = 30


def fetch_soup(url):
    """Fetch and parse HTML from URL."""
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def get_latest_years(documents):
    """Devuelve un dict {category: max_year} a partir de una lista de documentos."""
    latest = {}
    for doc in documents:
        cat = doc.get("category", "unknown")
        year = doc.get("year", 0)
        if cat not in latest or year > latest[cat]:
            latest[cat] = year
    return latest


def discover_defense_white_papers():
    """Scrape MOD website for Defense White Papers in EN and JA."""
    documents = []
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

    url_ja = "https://www.mod.go.jp/j/publication/wp/index.html"
    try:
        soup = fetch_soup(url_ja)
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True)
            match = re.search(r"令和(\d+)年|防衛白書.*(\d{4})", text)
            if match:
                if match.group(1):
                    reiwa_year = int(match.group(1))
                    year = 2018 + reiwa_year if reiwa_year > 1 else 2019
                elif match.group(2):
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
    """Scrape MOFA website for Diplomatic Bluebooks in EN and JA."""
    documents = []
    url_en = "https://www.mofa.go.jp/policy/other/bluebook/index.html"
    try:
        soup = fetch_soup(url_en)
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                title_cell = cells[0]
                title_text = title_cell.get_text(strip=True)
                match = re.search(r"DIPLOMATIC BLUEBOOK (\d{4})", title_text, re.IGNORECASE)
                if match:
                    year = int(match.group(1))
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

    url_ja = "https://www.mofa.go.jp/mofaj/gaiko/bluebook/index.html"
    try:
        soup = fetch_soup(url_ja)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"(令和|平成)(\d+)年.*外交青書|外交青書.*(\d{4})", link_text)
            if match:
                if match.group(2):
                    era_year = int(match.group(2))
                    if "令和" in link_text:
                        year = 2018 + era_year if era_year > 1 else 2019
                    elif "平成" in link_text:
                        year = 1988 + era_year
                    else:
                        continue
                elif match.group(3):
                    year = int(match.group(3))
                else:
                    continue
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
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
    """Discover NIDS China Security Report documents."""
    documents = []
    url = "https://www.nids.mod.go.jp/english/publication/chinareport/index.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"China Security Report (20\d{2})", link_text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.nids.mod.go.jp{href}"
                    if not any(d["year"] == year for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"NIDS China Security Report {year}",
                            "lang": "en",
                            "organization": "NIDS",
                            "category": "nids_china_report"
                        })
    except Exception as e:
        print(f"Error scraping NIDS China Reports: {e}")
    return documents


def discover_oda_white_papers():
    """Discover ODA (Official Development Assistance) White Papers."""
    documents = []
    url = "https://www.mofa.go.jp/policy/oda/white/index.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = re.search(r"(20\d{2})", link_text)
            if match and ("Development Cooperation" in link_text or "ODA" in link_text):
                year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                    if not any(d["year"] == year for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"White Paper on Development Cooperation {year}",
                            "lang": "en",
                            "organization": "MOFA",
                            "category": "oda_white_paper"
                        })
    except Exception as e:
        print(f"Error scraping ODA White Papers: {e}")
    return documents


def discover_cybersecurity_strategy():
    """Discover Japan Cybersecurity Strategy documents (NISC)."""
    documents = []
    url = "https://www.nisc.go.jp/policy/index.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            if "サイバーセキュリティ戦略" in link_text or "Cybersecurity Strategy" in link_text:
                match = re.search(r"(20\d{2}|令和\d+)", link_text)
                if not match:
                    continue
                if "令和" in match.group(1):
                    era_year = int(re.search(r"\d+", match.group(1)).group())
                    year = 2018 + era_year
                else:
                    year = int(match.group(1))
                href = link.get("href", "")
                if href:
                    url_doc = href if href.startswith("http") else f"https://www.nisc.go.jp{href}"
                    lang = "en" if "Cybersecurity Strategy" in link_text else "ja"
                    if not any(d["year"] == year and d["lang"] == lang for d in documents):
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"Cybersecurity Strategy {year}" if lang == "en" else f"サイバーセキュリティ戦略 {year}",
                            "lang": lang,
                            "organization": "NISC",
                            "category": "cybersecurity_strategy"
                        })
    except Exception as e:
        print(f"Error scraping Cybersecurity Strategy: {e}")
    return documents

def discover_economic_security():
    """Discover Economic Security policy documents (Cabinet Secretariat).

    Nota: la URL fue corregida de keizai_anzen_hosho (404) a
    keizai_anzen_hosyo, que es la ruta real usada por cas.go.jp.
    La pagina lista reuniones "第N回" con fechas en era Reiwa; se
    extraen como documentos los enlaces a las actas (gijisidai.html).
    """
    documents = []
    url = "https://www.cas.go.jp/jp/seisaku/keizai_anzen_hosyo/index.html"
    try:
        soup = fetch_soup(url)
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            row_text = row.get_text(strip=True)
            match = re.search(r"令和(\d+)年", row_text)
            if not match:
                continue
            reiwa_year = int(match.group(1))
            year = 2018 + reiwa_year
            for link in row.find_all("a", href=True):
                href = link.get("href", "")
                if not href or "gijisidai" not in href:
                    continue
                url_doc = href if href.startswith("http") else f"https://www.cas.go.jp{href}"
                if not any(d["url"] == url_doc for d in documents):
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": f"経済安全保障推進会議 議事次第・資料 {year}",
                        "lang": "ja",
                        "organization": "Cabinet Secretariat",
                        "category": "economic_security"
                    })
    except Exception as e:
        print(f"Error scraping Economic Security documents: {e}")
    return documents

def discover_gender_equality_plans():
    """Discover Gender Equality Basic Plans (Gender Equality Bureau, Cabinet Office)."""
    documents = []
    url = "https://www.gender.go.jp/about_danjo/basic_plans/index.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            if "男女共同参画基本計画" in link_text:
                match = re.search(r"第(\d+)次", link_text)
                year_match = re.search(r"(20\d{2})", link_text)
                href = link.get("href", "")
                if not href:
                    continue
                url_doc = href if href.startswith("http") else f"https://www.gender.go.jp{href}"
                plan_number = match.group(1) if match else "unknown"
                title = link_text if link_text else f"男女共同参画基本計画 第{plan_number}次"
                if not any(d.get("title") == title for d in documents):
                    documents.append({
                        "year": int(year_match.group(1)) if year_match else 0,
                        "url": url_doc,
                        "title": title,
                        "lang": "ja",
                        "organization": "Gender Equality Bureau",
                        "category": "gender_equality_plan"
                    })
    except Exception as e:
        print(f"Error scraping Gender Equality Plans: {e}")
    return documents


def discover_foip():
    """Discover Free and Open Indo-Pacific (FOIP) related documents (MOFA)."""
    documents = []
    url = "https://www.mofa.go.jp/policy/page25e_000278.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            if "Free and Open Indo-Pacific" in link_text or "FOIP" in link_text or "自由で開かれたインド太平洋" in link_text:
                match = re.search(r"(20\d{2})", link_text)
                year = int(match.group(1)) if match else 0
                href = link.get("href", "")
                if not href:
                    continue
                url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                lang = "ja" if "インド太平洋" in link_text else "en"
                if not any(d.get("url") == url_doc for d in documents):
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": link_text,
                        "lang": lang,
                        "organization": "MOFA",
                        "category": "foip"
                    })
    except Exception as e:
        print(f"Error scraping FOIP documents: {e}")
    return documents


ALL_DISCOVERERS = [
    discover_defense_white_papers,
    discover_diplomatic_bluebooks,
    discover_nids_china_reports,
    discover_oda_white_papers,
    discover_cybersecurity_strategy,
    discover_economic_security,
    discover_gender_equality_plans,
    discover_foip,
]


def discover_all():
    """Ejecuta todas las funciones de auto-descubrimiento y devuelve una lista combinada."""
    all_documents = []
    for discoverer in ALL_DISCOVERERS:
        try:
            all_documents.extend(discoverer())
        except Exception as e:
            print(f"Error running {discoverer.__name__}: {e}")
    return all_documents


if __name__ == "__main__":
    docs = discover_all()
    print(f"Total documentos encontrados: {len(docs)}")
    latest = get_latest_years(docs)
    print("Ultimo anio por categoria:")
    for cat, year in latest.items():
        print(f"  {cat}: {year}")
