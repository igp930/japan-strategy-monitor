#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper (Archive & Failover Support)
Monitorea documentos actuales e históricos del gobierno de Japón.
Incluye soporte de failover con semillas críticas para evitar errores 403 de GitHub.
"""
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# URLs oficiales
SOURCES = {
    "MOD": "https://www.mod.go.jp/en/publ/w_paper/index.html",
    "MOFA": "https://www.mofa.go.jp/policy/other/bluebook/index.html",
    "Kantei": "https://www.cas.go.jp/jp/siryou/index.html",
    "METI": "https://www.meti.go.jp/policy/economy/economic_security/index.html",
    "Cabinet": "https://www.gender.go.jp/about_danjo/basic_plans/index.html"
}

# --- DOCUMENTOS CRÍTICOS (HARDCODED PARA EVITAR BLOQUEOS DE RED) ---
KNOWN_DOCS = [
    # --- DEFENSA (LIBROS BLANCOS / WHITE PAPERS) ---
    {"title": "Defense of Japan 2024 (White Paper)", "organization": "MOD", "date": "2024-07-12", "category": "Defensa", "description": "Edición más reciente del Libro Blanco de Defensa.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_Full_1016.pdf"},
    {"title": "Defense of Japan 2023 (White Paper)", "organization": "MOD", "date": "2023-07-28", "category": "Defensa", "description": "Libro Blanco 2023.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_Full_1016.pdf"},
    {"title": "Defense of Japan 2022 (White Paper)", "organization": "MOD", "date": "2022-07-22", "category": "Archivo Histórico", "description": "Libro Blanco 2022.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_Full_1016.pdf"},
    {"title": "Defense of Japan 2021 (White Paper)", "organization": "MOD", "date": "2021-07-13", "category": "Archivo Histórico", "description": "Libro Blanco 2021.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2021/DOJ2021_Full_1016.pdf"},
    
    # --- POLÍTICA EXTERIOR (BLUEBOOKS) ---
    {"title": "Diplomatic Bluebook 2024", "organization": "MOFA", "date": "2024-04-16", "category": "Política Exterior", "description": "Informe anual sobre política exterior 2024.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf"},
    {"title": "Diplomatic Bluebook 2023", "organization": "MOFA", "date": "2023-04-14", "category": "Política Exterior", "description": "Informe anual 2023.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/pdfs/2023_all.pdf"},
    {"title": "Diplomatic Bluebook 2022", "organization": "MOFA", "date": "2022-04-22", "category": "Archivo Histórico", "description": "Informe anual 2022.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/pdfs/2022_all.pdf"},
    
    # --- ESTRATEGIAS NACIONALES ---
    {"title": "National Security Strategy of Japan (2022)", "organization": "Kantei", "date": "2022-12-16", "category": "Estrategia", "description": "Documento cumbre de seguridad actual.", "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"},
    {"title": "National Defense Strategy (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Sustituye a las NDPG anteriores.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"},
    {"title": "Economic Security Promotion Act (2022)", "organization": "Legislación", "date": "2022-05-11", "category": "Seguridad Económica", "description": "Marco legal para la resiliencia.", "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"},
    
    # --- IGUALDAD DE GÉNERO ---
    {"title": "Fifth Basic Plan for Gender Equality (2020)", "organization": "Gabinete", "date": "2020-12-25", "category": "Género", "description": "Plan fundamental vigente.", "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html"},
    {"title": "Basic Act for Gender Equal Society (1999)", "organization": "Legislación", "date": "1999-06-23", "category": "Género", "description": "Ley fundamental histórica.", "url": "https://www.japaneselawtranslation.go.jp/en/laws/view/2526/en"}
]

def fetch_page(url):
    try:
        # User-agent más agresivo para evitar 403
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None

def scrape_generic(org, url, keywords, category):
    docs = []
    html = fetch_page(url)
    if not html: return docs
    
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if any(kw in text for kw in keywords):
            href = link['href']
            # Construcción de URL
            if href.startswith('http'): full_url = href
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
                "description": f"Encontrado en {org}."
            })
    return docs[:10]

def main():
    print("Japan Strategy Monitor - Running with Archive Failover...")
    all_docs = KNOWN_DOCS.copy()
    
    # Intentar scrape dinámico (con failover silencioso)
    all_docs.extend(scrape_generic("MOD", SOURCES["MOD"], ['white paper', 'defense', 'wp20'], "Defensa"))
    all_docs.extend(scrape_generic("MOFA", SOURCES["MOFA"], ['bluebook', 'diplomatic'], "Política Exterior"))
    
    # Deduplicar por URL
    seen = set()
    final_list = []
    for d in all_docs:
        if d['url'] not in seen:
            seen.add(d['url'])
            final_list.append(d)
    
    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": final_list
    }
    
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Total: {len(final_list)} documents.")

if __name__ == "__main__":
    main()
