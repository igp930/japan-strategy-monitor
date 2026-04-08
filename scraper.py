#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper
Monitorea documentos estratégicos de MOD, MOFA, Kantei, METI y NISC.
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
    "NISC": "https://www.nisc.go.jp/policy/index.html"
}

# Documentos semilla conocidos
KNOWN_DOCS = [
    {
        "title": "National Security Strategy of Japan (2022)",
        "organization": "Kantei",
        "date": "2022-12-16",
        "category": "Estratégico",
        "description": "Marco estratégico integrado",
        "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"
    },
    {
        "title": "National Defense Strategy (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Estratégico",
        "description": "Estrategia de defensa nacional",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"
    },
    {
        "title": "Defense Buildup Program (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Estratégico",
        "description": "Programa de refuerzo de capacidades",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/plan/index.html"
    },
    {
        "title": "Economic Security Promotion Act",
        "organization": "METI",
        "date": "2022-05-11",
        "category": "Estratégico",
        "description": "Cadenas de suministro y tecnologías estratégicas",
        "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"
    },
    {
        "title": "Diplomatic Bluebook 2025",
        "organization": "MOFA",
        "date": "2025-03-01",
        "category": "Estratégico",
        "description": "Política exterior y alianzas",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/index.html"
    }
]

def fetch_page(url):
    """Descarga una página web"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_mod():
    """Busca documentos estratégicos del MOD"""
    docs = []
    html = fetch_page(SOURCES["MOD"])
    if not html:
        return docs
    
    soup = BeautifulSoup(html, 'html.parser')
    # Buscar enlaces con palabras clave
    keywords = ['defense', 'strategy', '防衛', '戦略', 'guideline', 'white paper']
    
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if any(kw in text for kw in keywords):
            docs.append({
                "title": link.get_text().strip(),
                "organization": "MOD",
                "url": link['href'] if link['href'].startswith('http') else f"https://www.mod.go.jp{link['href']}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "category": "Estratégico"
            })
    
    return docs[:5]  # Limitar a 5 más recientes

def scrape_mofa():
    """Busca documentos estratégicos del MOFA"""
    docs = []
    html = fetch_page(SOURCES["MOFA"])
    if not html:
        return docs
    
    soup = BeautifulSoup(html, 'html.parser')
    keywords = ['bluebook', 'diplomatic', 'white paper', '外交', '青書']
    
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        if any(kw in text for kw in keywords):
            docs.append({
                "title": link.get_text().strip(),
                "organization": "MOFA",
                "url": link['href'] if link['href'].startswith('http') else f"https://www.mofa.go.jp{link['href']}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "category": "Estratégico"
            })
    
    return docs[:5]

def scrape_all():
    """Ejecuta todos los scrapers"""
    all_docs = KNOWN_DOCS.copy()  # Comenzar con documentos conocidos
    
    print("Scraping MOD...")
    all_docs.extend(scrape_mod())
    
    print("Scraping MOFA...")
    all_docs.extend(scrape_mofa())
    
    # Eliminar duplicados por título
    seen = set()
    unique_docs = []
    for doc in all_docs:
        if doc['title'] not in seen:
            seen.add(doc['title'])
            unique_docs.append(doc)
    
    return unique_docs

def main():
    """Función principal"""
    print("Japan Strategy Monitor - Starting scraper...")
    
    docs = scrape_all()
    
    # Guardar en documents.json
    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": docs
    }
    
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Scraping completed. Found {len(docs)} documents.")
    print(f"✓ Saved to documents.json")

if __name__ == "__main__":
    main()
