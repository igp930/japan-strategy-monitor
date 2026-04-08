#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper
Monitorea documentos estratégicos incluyendo defensa, política exterior,
seguridad económica, género y LGBT+.
"""

import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# URLs oficiales a monitorear
SOURCES = {
    "MOD": "https://www.mod.go.jp/j/publication/index.html",
    "MOFA": "https://www.mofa.go.jp/policy/index.html",
    "Kantei": "https://www.kantei.go.jp/jp/headline/index.html",
    "METI": "https://www.meti.go.jp/policy/index.html",
    "NISC": "https://www.nisc.go.jp/policy/index.html",
    "Gender_Equality": "https://www.gender.go.jp/about_danjo/basic_plans/index.html"
}

# Documentos semilla conocidos (Ampliados)
KNOWN_DOCS = [
    {
        "title": "National Security Strategy of Japan (2022)",
        "organization": "Kantei",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Marco estratégico integrado de seguridad nacional.",
        "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"
    },
    {
        "title": "Fifth Basic Plan for Gender Equality",
        "organization": "Cabinet Office",
        "date": "2020-12-25",
        "category": "Género/LGBT+",
        "description": "Plan fundamental para promover la igualdad de género en Japón.",
        "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html"
    },
    {
        "title": "Act on Promotion of Public Understanding of LGBTQ+",
        "organization": "Kantei",
        "date": "2023-06-23",
        "category": "Género/LGBT+",
        "description": "Ley para promover la comprensión pública de la diversidad sexual.",
        "url": "https://www.cas.go.jp/jp/hourei/index.html"
    },
    {
        "title": "Economic Security Promotion Act",
        "organization": "METI",
        "date": "2022-05-11",
        "category": "Seguridad Económica",
        "description": "Protección de cadenas de suministro y tecnologías críticas.",
        "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"
    },
    {
        "title": "National Defense Strategy (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Estrategia de defensa nacional a medio y largo plazo.",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"
    },
    {
        "title": "Diplomatic Bluebook 2025",
        "organization": "MOFA",
        "date": "2025-03-01",
        "category": "Política Exterior",
        "description": "Informe anual sobre la política exterior y situación internacional.",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/index.html"
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

def scrape_generic(org, url, keywords, category):
    docs = []
    html = fetch_page(url)
    if not html: return docs
    
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if any(kw in text for kw in keywords):
            href = link['href']
            full_url = href if href.startswith('http') else f"{url.split('/jp/')[0]}{href}" if '/jp/' in url else href
            docs.append({
                "title": link.get_text().strip(),
                "organization": org,
                "url": full_url,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "category": category,
                "description": "Documento detectado automáticamente."
            })
    return docs[:3]

def scrape_all():
    all_docs = KNOWN_DOCS.copy()
    
    # Defensa
    all_docs.extend(scrape_generic("MOD", SOURCES["MOD"], ['defense', 'strategy', '防衛', '戦略'], "Defensa"))
    
    # Política Exterior
    all_docs.extend(scrape_generic("MOFA", SOURCES["MOFA"], ['diplomatic', 'foreign', '外交', '青書'], "Política Exterior"))
    
    # Seguridad Económica
    all_docs.extend(scrape_generic("METI", SOURCES["METI"], ['economic security', 'supply chain', '経済安保'], "Seguridad Económica"))
    
    # Género / LGBT+
    all_docs.extend(scrape_generic("Gender Equality", SOURCES["Gender_Equality"], ['gender', 'equality', 'lgbt', '男女共同参画'], "Género/LGBT+"))
    
    # Eliminar duplicados
    seen = set()
    unique_docs = []
    for doc in all_docs:
        if doc['title'] not in seen:
            seen.add(doc['title'])
            unique_docs.append(doc)
            
    return unique_docs

def main():
    print("Japan Strategy Monitor - Scraping...")
    docs = scrape_all()
    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": docs
    }
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✓ Found {len(docs)} documents.")

if __name__ == "__main__":
    main()
