#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper (Enhanced Archive Support)
Monitorea documentos actuales e históricos del gobierno de Japón.
"""
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# URLs oficiales optimizadas para archivos
SOURCES = {
    "MOD": "https://www.mod.go.jp/j/press/wp/index.html", # Página específica de White Papers
    "MOFA": "https://www.mofa.go.jp/policy/other/bluebook/index.html", # Página de Bluebooks
    "Kantei": "https://www.kantei.go.jp/jp/headline/index.html",
    "METI": "https://www.meti.go.jp/policy/economy/economic_security/index.html",
    "NISC": "https://www.nisc.go.jp/policy/index.html",
    "Gender_Equality": "https://www.gender.go.jp/about_danjo/basic_plans/index.html"
}

# Documentos conocidos y de archivo (Semillas críticas)
KNOWN_DOCS = [
    # --- DEFENSA (WHITE PAPERS) ---
    {
        "title": "Defense of Japan 2024 (White Paper)",
        "organization": "MOD",
        "date": "2024-07-12",
        "category": "Defensa",
        "description": "Libro Blanco de Defensa 2024.",
        "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_Full_1016.pdf"
    },
    {
        "title": "Defense of Japan 2023 (White Paper)",
        "organization": "MOD",
        "date": "2023-07-28",
        "category": "Archivo Histórico",
        "description": "Libro Blanco de Defensa 2023.",
        "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_Full_1016.pdf"
    },
    {
        "title": "Defense of Japan 2022 (White Paper)",
        "organization": "MOD",
        "date": "2022-07-22",
        "category": "Archivo Histórico",
        "description": "Libro Blanco de Defensa 2022.",
        "url": "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_Full_1016.pdf"
    },
    # --- POLÍTICA EXTERIOR (BLUEBOOKS) ---
    {
        "title": "Diplomatic Bluebook 2024",
        "organization": "MOFA",
        "date": "2024-04-16",
        "category": "Política Exterior",
        "description": "Informe anual sobre política exterior 2024.",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/en_index.html"
    },
    {
        "title": "Diplomatic Bluebook 2023",
        "organization": "MOFA",
        "date": "2023-04-11",
        "category": "Archivo Histórico",
        "description": "Informe anual sobre política exterior 2023.",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/en_index.html"
    },
    {
        "title": "Diplomatic Bluebook 2022",
        "organization": "MOFA",
        "date": "2022-04-22",
        "category": "Archivo Histórico",
        "description": "Informe anual sobre política exterior 2022.",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/en_index.html"
    },
    # --- ESTRATEGIAS CUMBRE ---
    {
        "title": "National Security Strategy of Japan (2022)",
        "organization": "Kantei",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Estrategia de Seguridad Nacional vigente.",
        "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"
    },
    {
        "title": "National Defense Strategy (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Estrategia de defensa a 10 años.",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"
    }
]

def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_generic(org, url, keywords, category, limit=20):
    docs = []
    html = fetch_page(url)
    if not html: return docs
    
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if any(kw in text for kw in keywords):
            href = link['href']
            # Construcción inteligente de URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                domain = url.split('//')[0] + '//' + url.split('//')[1].split('/')[0]
                full_url = domain + href
            else:
                base = url.rsplit('/', 1)[0]
                full_url = f"{base}/{href}"
            
            docs.append({
                "title": link.get_text().strip(),
                "organization": org,
                "url": full_url,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "category": category,
                "description": "Documento detectado automáticamente."
            })
    return docs[:limit]

def scrape_all():
    all_docs = KNOWN_DOCS.copy()
    
    # Defensa (Priorizando White Papers y Estrategia)
    all_docs.extend(scrape_generic("MOD", SOURCES["MOD"], ['white paper', '白書', 'defense', 'strategy'], "Defensa", limit=20))
    
    # Política Exterior (Priorizando Bluebooks)
    all_docs.extend(scrape_generic("MOFA", SOURCES["MOFA"], ['bluebook', '青書', 'diplomatic'], "Política Exterior", limit=20))
    
    # Seguridad Económica
    all_docs.extend(scrape_generic("METI", SOURCES["METI"], ['economic security', 'supply chain', '経済安保'], "Seguridad Económica"))
    
    # Eliminar duplicados por URL para mayor precisión
    seen_urls = set()
    unique_docs = []
    for doc in all_docs:
        if doc['url'] not in seen_urls:
            seen_urls.add(doc['url'])
            unique_docs.append(doc)
    
    return unique_docs

def main():
    print("Japan Strategy Monitor - Scraping (Enhanced Archive Support)...")
    docs = scrape_all()
    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": docs
    }
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✓ Found {len(docs)} unique documents.")

if __name__ == "__main__":
    main()
