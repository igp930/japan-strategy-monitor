#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper (Historical & Development Support)
Monitorea documentos actuales, históricos y de desarrollo estratégico.
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

# Documentos conocidos (Ampliados con histórico y desarrollo)
KNOWN_DOCS = [
    # --- DOCUMENTOS ESTRATÉGICOS ACTUALES ---
    {
        "title": "National Security Strategy of Japan (2022)",
        "organization": "Kantei",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Documento cumbre de la estrategia de seguridad nacional actual.",
        "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"
    },
    {
        "title": "National Defense Strategy (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Estrategia de defensa a 10 años que sustituye a las NDPG.",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"
    },
    {
        "title": "Defense Buildup Program (2022)",
        "organization": "MOD",
        "date": "2022-12-16",
        "category": "Defensa",
        "description": "Plan detallado de desarrollo de capacidades para implementar la NDS.",
        "url": "https://www.mod.go.jp/j/policy/agenda/guideline/plan/index.html"
    },
    {
        "title": "Fifth Basic Plan for Gender Equality (2020)",
        "organization": "Cabinet Office",
        "date": "2020-12-25",
        "category": "Género/LGBT+",
        "description": "Plan fundamental vigente para la igualdad de género (2021-2025).",
        "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html"
    },
    {
        "title": "Economic Security Promotion Act (2022)",
        "organization": "METI",
        "date": "2022-05-11",
        "category": "Seguridad Económica",
        "description": "Marco legal para la resiliencia de suministros y tecnologías.",
        "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"
    },
    {
        "title": "Diplomatic Bluebook 2024",
        "organization": "MOFA",
        "date": "2024-04-16",
        "category": "Política Exterior",
        "description": "Informe anual sobre política exterior y situación global.",
        "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf"
    },
    
    # --- ARCHIVO HISTÓRICO (Documentos no vigentes) ---
    {
        "title": "National Security Strategy of Japan (2013)",
        "organization": "Kantei",
        "date": "2013-12-17",
        "category": "Archivo Histórico",
        "description": "La primera Estrategia de Seguridad Nacional (Sustituida por la de 2022).",
        "url": "https://www.cas.go.jp/jp/siryou/131217anzenhoshou/nss-e.pdf"
    },
    {
        "title": "National Defense Program Guidelines (NDPG 2018)",
        "organization": "MOD",
        "date": "2018-12-18",
        "category": "Archivo Histórico",
        "description": "Directrices de defensa previas enfocadas en defensa multidominio.",
        "url": "https://www.cas.go.jp/jp/siryou/pdf/2019boueikeikaku_e.pdf"
    },
    {
        "title": "National Defense Program Guidelines (NDPG 2010)",
        "organization": "MOD",
        "date": "2010-12-17",
        "category": "Archivo Histórico",
        "description": "Directrices históricas que introdujeron la 'Capacidad de Defensa Dinámica'.",
        "url": "https://japan.kantei.go.jp/kakugikettei/2010/ndpg_e.pdf"
    },
    {
        "title": "Fourth Basic Plan for Gender Equality (2015)",
        "organization": "Gender Equality Bureau",
        "date": "2015-12-25",
        "category": "Archivo Histórico",
        "description": "Plan de igualdad previo (Histórico).",
        "url": "https://www.gender.go.jp/english_contents/pr_act/pub/pamphlet/women-and-men20/pdf/3-3.pdf"
    },
    {
        "title": "Third Basic Plan for Gender Equality (2010)",
        "organization": "Gender Equality Bureau",
        "date": "2010-12-17",
        "category": "Archivo Histórico",
        "description": "Plan de igualdad de la era anterior (Histórico).",
        "url": "https://www.gender.go.jp/english_contents/pr_act/pub/pamphlet/women-and-men12/pdf/2-3.pdf"
    },

    # --- DESARROLLO Y LEYES FUNDAMENTALES ---
    {
        "title": "Basic Act for Gender Equal Society (1999)",
        "organization": "Legislación",
        "date": "1999-06-23",
        "category": "Género/LGBT+",
        "description": "Ley base que establece el marco para todos los planes posteriores.",
        "url": "https://www.japaneselawtranslation.go.jp/en/laws/view/2526/en"
    },
    {
        "title": "Economic Security Study Group Report (2022)",
        "organization": "NPI",
        "date": "2022-03-31",
        "category": "Seguridad Económica",
        "description": "Estudio técnico clave que desarrolló los conceptos de la Ley de 2022.",
        "url": "https://www.npi.or.jp/en/research/data/ba0ab338ab8b9114ba7e102161e869813b953cd7.pdf"
    },
    {
        "title": "Defense of Japan (White Paper) 2023",
        "organization": "MOD",
        "date": "2023-07-28",
        "category": "Defensa",
        "description": "Libro Blanco que desarrolla la implementación de la nueva estrategia.",
        "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_Full_1016.pdf"
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
    print("Japan Strategy Monitor - Scraping (Current & Historical)...")
    docs = scrape_all()
    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": docs
    }
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✓ Found {len(docs)} documents (including historical seeds).")

if __name__ == "__main__":
    main()
