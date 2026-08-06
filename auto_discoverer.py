"""Funciones de auto-descubrimiento para documentos japoneses.

Este modulo contiene scrapers automaticos que buscan nuevos documentos
en las paginas oficiales del gobierno japones, en multiples idiomas.
Todas las funciones publicas devuelven una lista de dicts con:
{"year": int, "url": str, "title": str, "lang": str, "organization": str, "category": str}
No reciben argumentos, y cada llamada crea su propia lista de resultados.

Nota sobre MOFA (www.mofa.go.jp): este dominio bloquea con 403 Forbidden
las peticiones que provienen de las IPs de los runners de GitHub Actions,
independientemente del User-Agent usado. Para evitar perder estos
documentos, fetch_soup_with_fallback intenta primero la peticion directa
y, si falla con 403, recurre a una copia archivada en Wayback Machine
(web.archive.org), que no esta bloqueada. Se usa el modificador "id_"
en la URL del snapshot para obtener el HTML original sin la barra de
herramientas de Wayback (que en algunos casos causaba un 498).
Como la API de disponibilidad de Wayback (archive.org/wayback/available)
devuelve 429 Too Many Requests con facilidad, fetch_soup_via_wayback
reintenta con backoff exponencial (y respeta el header Retry-After si
esta presente) antes de rendirse. Ademas de 429, tambien se reintenta
ante 498/502/503/504, ya que Wayback puede devolver estos codigos de
forma transitoria (p.ej. cuando el snapshot es grande o el servicio
esta sobrecargado) y normalmente se resuelven tras una breve espera.

Documentos estrategicos fijos (STATIC_STRATEGIC_DOCUMENTS): ademas de los
scrapers dinamicos, se incluye una lista curada de documentos clave cuyas
URLs oficiales son estables (leyes, estrategias con fecha de publicacion
fija, etc.) y que no siempre se pueden descubrir de forma fiable mediante
scraping (paginas con estructura variable, JS, o PDFs sueltos). Estos se
agregan siempre en discover_all() para asegurar su presencia:
- National Security Strategy 2022
- National Defense Program Guidelines 2018
- National Defense Strategy 2022
- Defense Buildup Program 2022
- New Plan for a FOIP (2023, FOIP 3.0)
- White Paper on International Economy and Trade (METI)
- Economic Security Promotion Act (2022)
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}
TIMEOUT = 30
WAYBACK_MAX_RETRIES = 4
WAYBACK_BASE_DELAY = 5
RETRYABLE_STATUS_CODES = {429, 498, 502, 503, 504}


def fetch_soup(url):
    """Fetch and parse HTML from URL."""
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def _get_with_retry(url, max_retries=WAYBACK_MAX_RETRIES, base_delay=WAYBACK_BASE_DELAY):
    """GET con reintentos y backoff exponencial ante codigos transitorios.

    Ademas de 429 Too Many Requests, se reintenta ante 498/502/503/504,
    codigos que Wayback Machine puede devolver de forma intermitente sin
    que ello implique que el recurso no exista. Si la respuesta incluye
    el header Retry-After, se respeta ese valor en lugar del backoff
    calculado. Tras agotar los reintentos, se relanza la ultima excepcion.
    """
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code in RETRYABLE_STATUS_CODES:
                retry_after = r.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else base_delay * (2 ** attempt)
                print(f"{r.status_code} en {url}, esperando {delay:.0f}s antes de reintentar "
                      f"(intento {attempt + 1}/{max_retries + 1})...")
                time.sleep(delay)
                last_exc = requests.exceptions.HTTPError(f"{r.status_code} Client Error", response=r)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as e:
            last_exc = e
            if e.response is not None and e.response.status_code in RETRYABLE_STATUS_CODES:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            raise
        except requests.exceptions.RequestException as e:
            last_exc = e
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    if last_exc:
        raise last_exc
    raise requests.exceptions.RequestException(f"No se pudo obtener {url}")


def fetch_soup_via_wayback(url):
    """Fetch the latest archived snapshot of url from the Wayback Machine.

    Se usa como fallback cuando la peticion directa devuelve 403, algo que
    ocurre de forma sistematica con www.mofa.go.jp desde las IPs de los
    runners de GitHub Actions. Se inserta el modificador "id_" despues del
    timestamp para pedir el HTML original (sin reescribir enlaces ni
    inyectar la barra de herramientas de archive.org), lo que evita errores
    498 al descargar snapshots grandes. Las peticiones a la API de
    disponibilidad y a los propios snapshots usan reintentos con backoff
    ya que es frecuente recibir 429 Too Many Requests o 498/502/503/504
    de forma transitoria.
    """
    api_url = f"https://archive.org/wayback/available?url={url}"
    r = _get_with_retry(api_url)
    data = r.json()
    snapshot = data.get("archived_snapshots", {}).get("closest")
    if not snapshot or not snapshot.get("available"):
        raise ValueError(f"No hay snapshot disponible en Wayback Machine para {url}")
    archive_url = snapshot["url"]
    match = re.search(r"(/web/(\d+))/", archive_url)
    if match:
        archive_url = archive_url.replace(match.group(1), f"{match.group(1)}id_")
    r2 = _get_with_retry(archive_url)
    return BeautifulSoup(r2.text, "html.parser"), archive_url


def fetch_soup_with_fallback(url):
    """Intenta fetch_soup(url) y si falla con 403 usa Wayback Machine.

    Devuelve (soup, base_url) donde base_url es la URL original si la
    peticion directa funciono, o la URL de archive.org si se uso el
    fallback. base_url se usa para resolver enlaces relativos.
    """
    try:
        return fetch_soup(url), url
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            print(f"403 en {url}, probando Wayback Machine...")
            try:
                soup, archive_url = fetch_soup_via_wayback(url)
                return soup, url
            except Exception as wayback_error:
                print(f"Fallback a Wayback Machine tambien fallo para {url}: {wayback_error}")
                raise
        raise


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
    """Scrape MOFA website for Diplomatic Bluebooks in EN and JA.

    Usa fetch_soup_with_fallback porque MOFA bloquea con 403 las peticiones
    desde runners de GitHub Actions; en ese caso se recurre a Wayback Machine.
    """
    documents = []
    url_en = "https://www.mofa.go.jp/policy/other/bluebook/index.html"
    try:
        soup, _ = fetch_soup_with_fallback(url_en)
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
        soup, _ = fetch_soup_with_fallback(url_ja)
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
    """Discover ODA (Official Development Assistance) White Papers.

    Usa fetch_soup_with_fallback porque MOFA bloquea con 403 las peticiones
    desde runners de GitHub Actions.
    """
    documents = []
    url = "https://www.mofa.go.jp/policy/oda/white/index.html"
    try:
        soup, _ = fetch_soup_with_fallback(url)
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
    keizai_anzen_hosyo, que es la ruta real usada por cas.go.jp. La pagina
    lista reuniones "第N回" con fechas en era Reiwa; se extraen como
    documentos los enlaces a las actas (gijisidai.html).
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
    """Discover Free and Open Indo-Pacific (FOIP) related documents (MOFA),
    incluyendo el "New Plan for a Free and Open Indo-Pacific" (FOIP 3.0, 2023)
    y las actualizaciones posteriores (FOIP evolucionado 2026).

    Usa fetch_soup_with_fallback porque MOFA bloquea con 403 las peticiones
    desde runners de GitHub Actions.
    """
    documents = []
    url = "https://www.mofa.go.jp/policy/page25e_000278.html"
    try:
        soup, _ = fetch_soup_with_fallback(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            if ("Free and Open Indo-Pacific" in link_text or "FOIP" in link_text or
                    "New Plan" in link_text or "自由で開かれたインド太平洋" in link_text or
                    "新しいプラン" in link_text):
                match = re.search(r"(20\d{2})", link_text)
                year = int(match.group(1)) if match else 0
                href = link.get("href", "")
                if not href:
                    continue
                url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                lang = "ja" if "インド太平洋" in link_text or "プラン" in link_text else "en"
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


def discover_meti_trade_white_papers():
    """Discover METI's White Paper on International Economy and Trade.

    La pagina indice usa un acordeon por anio con enlaces del tipo
    /english/report/data/gIT{year}maine.html.
    """
    documents = []
    url = "https://www.meti.go.jp/english/report/index_whitepaper.html"
    try:
        soup = fetch_soup(url)
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            href = link.get("href", "")
            if re.fullmatch(r"20\d{2}", link_text) and "gIT" in href:
                year = int(link_text)
                url_doc = href if href.startswith("http") else f"https://www.meti.go.jp{href}"
                if not any(d["year"] == year for d in documents):
                    documents.append({
                        "year": year,
                        "url": url_doc,
                        "title": f"White Paper on International Economy and Trade {year}",
                        "lang": "en",
                        "organization": "METI",
                        "category": "trade_white_paper"
                    })
    except Exception as e:
        print(f"Error scraping METI Trade White Papers: {e}")
    return documents


STATIC_STRATEGIC_DOCUMENTS = [
    {
        "year": 2022,
        "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
        "title": "National Security Strategy of Japan (2022)",
        "lang": "en",
        "organization": "Cabinet Secretariat",
        "category": "national_security_strategy"
    },
    {
        "year": 2018,
        "url": "https://www.cas.go.jp/jp/siryou/pdf/2019boueikeikaku_e.pdf",
        "title": "National Defense Program Guidelines for FY 2019 and beyond (2018)",
        "lang": "en",
        "organization": "Cabinet Secretariat",
        "category": "national_defense_program_guidelines"
    },
    {
        "year": 2022,
        "url": "https://japan.kantei.go.jp/content/000120033.pdf",
        "title": "National Defense Strategy (2022)",
        "lang": "en",
        "organization": "Ministry of Defense",
        "category": "national_defense_strategy"
    },
    {
        "year": 2022,
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/plan/pdf/program_en.pdf",
        "title": "Defense Buildup Program (2022)",
        "lang": "en",
        "organization": "Ministry of Defense",
        "category": "defense_buildup_program"
    },
    {
        "year": 2023,
        "url": "https://www.mofa.go.jp/fp/pc/page3e_001336.html",
        "title": "New Plan for a \u201cFree and Open Indo-Pacific (FOIP)\u201d (FOIP 3.0, 2023)",
        "lang": "en",
        "organization": "MOFA",
        "category": "foip"
    },
    {
        "year": 2022,
        "url": "https://www.japaneselawtranslation.go.jp/en/laws/view/4716/en",
        "title": "Act on the Promotion of Ensuring National Security through Integrated Implementation of Economic Measures (Economic Security Promotion Act, Act No. 43 of 2022)",
        "lang": "en",
        "organization": "Cabinet Secretariat",
        "category": "economic_security_law"
    },
]


def discover_static_strategic_documents():
    """Devuelve la lista curada de documentos estrategicos con URLs estables.

    Ver docstring del modulo para el listado completo y su justificacion.
    """
    return list(STATIC_STRATEGIC_DOCUMENTS)


ALL_DISCOVERERS = [
    discover_defense_white_papers,
    discover_diplomatic_bluebooks,
    discover_nids_china_reports,
    discover_oda_white_papers,
    discover_cybersecurity_strategy,
    discover_economic_security,
    discover_gender_equality_plans,
    discover_foip,
    discover_meti_trade_white_papers,
    discover_static_strategic_documents,
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
