"""Funciones de auto-descubrimiento para documentos japoneses.

Este módulo contiene scrapers automáticos que buscan nuevos documentos
en las páginas oficiales del gobierno japonés.
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
    """Scrape MOD website for Defense White Papers.
    
    Returns:
        list: Lista de dict con {"year": int, "url_en": str, "url_ja": str}
    """
    url = "https://www.mod.go.jp/en/publ/w_paper/index.html"
    soup = fetch_soup(url)
    documents = []
    
    # Buscar el título "DEFENSE OF JAPAN XXXX"
    for heading in soup.find_all(["h2", "h3"]):
        text = heading.get_text(strip=True)
        match = re.search(r"DEFENSE OF JAPAN (\d{4})", text)
        if match:
            year = int(match.group(1))
            # Buscar enlaces PDF cercanos
            section = heading.find_parent(["div", "section"])
            if section:
                links = section.find_all("a", href=re.compile(r"DOJ.*\.pdf|wp.*index\.html"))
                url_en = None
                for link in links:
                    href = link.get("href", "")
                    if "_EN" in href or "english" in href.lower():
                        url_en = href if href.startswith("http") else f"https://www.mod.go.jp{href}"
                        break
                
                if url_en:
                    documents.append({
                        "year": year,
                        "url_en": url_en,
                        "title_en": f"Defense of Japan {year} (White Paper)",
                        "organization": "MOD"
                    })
    
    return documents

def discover_diplomatic_bluebooks():
    """Scrape MOFA website for Diplomatic Bluebooks.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str}
    """
    url = "https://www.mofa.go.jp/policy/other/bluebook/index.html"
    soup = fetch_soup(url)
    documents = []
    
    # Buscar en tabla
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header
            cells = row.find_all("td")
            if len(cells) >= 2:
                title_cell = cells[0]
                title_text = title_cell.get_text(strip=True)
                
                # Extraer año
                match = re.search(r"BLUEBOOK (\d{4})", title_text, re.IGNORECASE)
                if match:
                    year = int(match.group(1))
                    
                    # Buscar enlaces PDF o HTML
                    links = title_cell.find_all("a")
                    url_en = None
                    for link in links:
                        text = link.get_text(strip=True).lower()
                        href = link.get("href", "")
                        if ("english" in text or "pdf" in text) and href:
                            url_en = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                            break
                    
                    if url_en:
                        documents.append({
                            "year": year,
                            "url": url_en,
                            "title": f"Diplomatic Bluebook {year}",
                            "organization": "MOFA"
                        })
    
    return documents

def discover_nids_china_reports():
    """Scrape NIDS website for China Security Reports.
    
    Returns:
        list: Lista de dict con {"year": int, "url": str, "subtitle": str}
    """
    url = "https://www.nids.mod.go.jp/english/publication/chinareport/index.html"
    soup = fetch_soup(url)
    documents = []
    
    # Buscar headings "China Security Report XXXX"
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = heading.get_text(strip=True)
        match = re.search(r"China Security Report (\d{4})", text)
        if match:
            year = int(match.group(1))
            
            # Buscar subtítulo
            next_elem = heading.find_next_sibling()
            subtitle = ""
            if next_elem and next_elem.name in ["p", "h4", "h5"]:
                subtitle = next_elem.get_text(strip=True)
            
            # Buscar enlace PDF en sección
            section = heading.find_next(["div", "section", "ul"])
            if section:
                links = section.find_all("a", href=re.compile(r".*_EN_.*\.pdf|.*english.*\.pdf"))
                for link in links:
                    href = link.get("href", "")
                    if "_EN_" in href or "english" in href.lower():
                        url_doc = href if href.startswith("http") else f"https://www.nids.mod.go.jp{href}"
                        documents.append({
                            "year": year,
                            "url": url_doc,
                            "title": f"NIDS China Security Report {year}",
                            "subtitle": subtitle,
                            "organization": "NIDS"
                        })
                        break
    
    return documents

def discover_oda_white_papers():
    """Scrape MOFA website for ODA White Papers (Development Cooperation).
    
    Returns:
        list: Lista de dict con {"year": int, "url": str}
    """
    url = "https://www.mofa.go.jp/policy/oda/page_000017.html"
    try:
        soup = fetch_soup(url)
        documents = []
        
        # Buscar enlaces con "White Paper" y años
        links = soup.find_all("a", href=re.compile(r"white.*\d{4}", re.IGNORECASE))
        for link in links:
            text = link.get_text(strip=True)
            href = link.get("href", "")
            
            # Extraer año del enlace o texto
            year_match = re.search(r"(\d{4})", href + text)
            if year_match:
                year = int(year_match.group(1))
                url_doc = href if href.startswith("http") else f"https://www.mofa.go.jp{href}"
                
                documents.append({
                    "year": year,
                    "url": url_doc,
                    "title": f"White Paper on Development Cooperation {year}",
                    "organization": "MOFA"
                })
        
        return documents
    except:
        # Si falla, intentar con URL alternativo
        return []

def get_latest_years():
    """Detecta los últimos años disponibles para cada tipo de documento.
    
    Returns:
        dict: Diccionario con {"defense_wp": int, "bluebook": int, "nids": int}
    """
    latest = {
        "defense_wp": 2025,
        "bluebook": 2025,
        "nids_china": 2025
    }
    
    try:
        defense_docs = discover_defense_white_papers()
        if defense_docs:
            latest["defense_wp"] = max(doc["year"] for doc in defense_docs)
    except:
        pass
    
    try:
        bluebook_docs = discover_diplomatic_bluebooks()
        if bluebook_docs:
            latest["bluebook"] = max(doc["year"] for doc in bluebook_docs)
    except:
        pass
    
    try:
        nids_docs = discover_nids_china_reports()
        if nids_docs:
            latest["nids_china"] = max(doc["year"] for doc in nids_docs)
    except:
        pass
    
    return latest

if __name__ == "__main__":
    print("=== Auto-discovering Japanese Strategy Documents ===")
    print("\n1. Defense White Papers:")
    defense = discover_defense_white_papers()
    for doc in defense[:3]:  # Mostrar solo los 3 más recientes
        print(f"  - {doc['year']}: {doc['title_en']}")
    
    print("\n2. Diplomatic Bluebooks:")
    bluebooks = discover_diplomatic_bluebooks()
    for doc in bluebooks[:3]:
        print(f"  - {doc['year']}: {doc['title']}")
    
    print("\n3. NIDS China Reports:")
    nids = discover_nids_china_reports()
    for doc in nids[:3]:
        print(f"  - {doc['year']}: {doc['title']} - {doc.get('subtitle', '')[:50]}...")
    
    print("\n4. Latest Years Detected:")
    latest = get_latest_years()
    for key, year in latest.items():
        print(f"  - {key}: {year}")
