#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper & RSS Generator
Monitorea documentos actuales e historicos del gobierno de Japon.
Genera JSON y RSS para seguimiento automatico.
"""
import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# URLs oficiales para monitoreo
SOURCES = {
    "MOD": "https://www.mod.go.jp/en/publ/w_paper/index.html",
    "MOFA": "https://www.mofa.go.jp/policy/other/bluebook/index.html",
    "Kantei": "https://www.cas.go.jp/jp/siryou/index.html",
    "METI": "https://www.meti.go.jp/policy/economy/economic_security/index.html"
}

# --- DOCUMENTOS CRITICOS (BASE DE DATOS INICIAL) ---
KNOWN_DOCS = [
    # --- DEFENSA ---
    {"title": "Defense of Japan 2025 (White Paper)", "organization": "MOD", "date": "2025-07-14", "category": "Defensa", "description": "Latest Defense White Paper 2025.", "url": "https://www.mod.go.jp/j/press/wp/wp2025/pdf/DOJ2025_Digest_EN.pdf"},
    {"title": "Defense of Japan 2024 (White Paper)", "organization": "MOD", "date": "2024-07-12", "category": "Defensa", "description": "Annual Defense White Paper 2024.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Full.pdf"},
    {"title": "Defense of Japan 2023 (White Paper)", "organization": "MOD", "date": "2023-07-28", "category": "Defensa", "description": "Annual Defense White Paper 2023.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_EN_Full.pdf"},
    {"title": "Defense of Japan 2022 (White Paper)", "organization": "MOD", "date": "2022-07-22", "category": "Defensa", "description": "Annual Defense White Paper 2022.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_EN_Full_02.pdf"},
    {"title": "National Security Strategy of Japan (2022)", "organization": "Kantei", "date": "2022-12-16", "category": "Estrategia", "description": "Supreme national security document revised Dec 2022.", "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"},
    {"title": "National Defense Strategy (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Defense strategy replacing NDPG, Dec 2022.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/pdf/strategy_en.pdf"},
    {"title": "Defense Buildup Program (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Long-term defense procurement plan Dec 2022.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/plan/pdf/program_en.pdf"},

    # --- POLITICA EXTERIOR ---
    {"title": "Diplomatic Bluebook 2024", "organization": "MOFA", "date": "2024-04-16", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2024.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf"},
    {"title": "Diplomatic Bluebook 2023", "organization": "MOFA", "date": "2023-04-15", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2023.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/pdfs/2023_all.pdf"},
    {"title": "Diplomatic Bluebook 2022", "organization": "MOFA", "date": "2022-04-12", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2022.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/pdfs/2022_all.pdf"},

    # --- SEGURIDAD ECONOMICA ---
    {"title": "Economic Security Promotion Act (2022)", "organization": "Legislacion", "date": "2022-05-11", "category": "Seguridad Economica", "description": "Legal framework for economic security and resilience.", "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"},

    # --- GENERO ---
    {"title": "Fifth Basic Plan for Gender Equality (2020)", "organization": "Gabinete", "date": "2020-12-25", "category": "Genero/LGBT+", "description": "Fifth national plan for gender equality.", "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html"}
]

def generate_rss(documents):
    rss_template = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Japan Strategy Monitor Feed</title>
  <link>https://igp930.github.io/japan-strategy-monitor/</link>
  <description>Latest strategic documents from the Government of Japan</description>
  <language>en-us</language>
  <lastBuildDate>{build_date}</lastBuildDate>
  {items}
</channel>
</rss>"""
    item_template = """
  <item>
    <title>{title}</title>
    <link>{link}</link>
    <description>{desc} ({org})</description>
    <pubDate>{pub_date}</pubDate>
    <guid isPermaLink="false">{guid}</guid>
  </item>"""
    items = []
    for doc in documents[:30]:
        try:
            dt = datetime.strptime(doc['date'], '%Y-%m-%d')
            pub_date = dt.strftime('%a, %d %b %Y 00:00:00 +0000')
        except:
            pub_date = datetime.now().strftime('%a, %d %b %Y 00:00:00 +0000')
        items.append(item_template.format(
            title=doc['title'],
            link=doc['url'],
            desc=doc.get('description', ''),
            org=doc['organization'],
            pub_date=pub_date,
            guid=doc['url']
        ))
    build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    return rss_template.format(build_date=build_date, items="".join(items))

def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print("Japan Strategy Monitor - Initiating comprehensive scan...")
    all_docs = KNOWN_DOCS.copy()

    # Intento de descubrimiento en MOD (White Papers nuevos)
    mod_html = fetch_page(SOURCES["MOD"])
    if mod_html:
        soup = BeautifulSoup(mod_html, 'html.parser')
        for link in soup.find_all('a', href=True):
            text = link.text.strip()
            if "Defense of Japan" in text and "20" in text:
                year_match = re.search(r'20\d{2}', text)
                if year_match:
                    year = year_match.group()
                    full_url = link['href']
                    if not full_url.startswith('http'):
                        full_url = "https://www.mod.go.jp" + full_url
                    if not any(d['url'] == full_url for d in all_docs):
                        all_docs.append({
                            "title": f"Defense of Japan {year} (Discovered)",
                            "organization": "MOD",
                            "date": f"{year}-07-01",
                            "category": "Defensa",
                            "description": f"Auto-discovered white paper page for {year}.",
                            "url": full_url
                        })

    # Filtrado y limpieza
    seen = set()
    final_list = []
    all_docs.sort(key=lambda x: x['date'], reverse=True)

    for d in all_docs:
        if d['url'] not in seen:
            seen.add(d['url'])
            year_val = int(d['date'].split('-')[0])
            if year_val < 2022:
                d['category'] = "Archivo Historico"
            final_list.append(d)

    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": final_list
    }

    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(generate_rss(final_list))
    print(f"Success: {len(final_list)} documents tracked and updated.")

if __name__ == "__main__":
    main()
