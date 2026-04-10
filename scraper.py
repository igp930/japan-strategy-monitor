#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper & RSS Generator
Monitorea documentos actuales e históricos del gobierno de Japón.
Genera JSON y RSS para seguimiento automático.
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

# --- DOCUMENTOS CRÍTICOS ---
KNOWN_DOCS = [
    {"title": "Defense of Japan 2024 (White Paper)", "organization": "MOD", "date": "2024-07-12", "category": "Defensa", "description": "Latest Defense White Paper.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_Full_1016.pdf"},
    {"title": "Defense of Japan 2023 (White Paper)", "organization": "MOD", "date": "2023-07-28", "category": "Defensa", "description": "White Paper 2023.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_Full_1016.pdf"},
    {"title": "Diplomatic Bluebook 2024", "organization": "MOFA", "date": "2024-04-16", "category": "Política Exterior", "description": "Annual report on foreign policy 2024.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf"},
    {"title": "National Security Strategy of Japan (2022)", "organization": "Kantei", "date": "2022-12-16", "category": "Estrategia", "description": "Core security strategy document.", "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"},
    {"title": "National Defense Strategy (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Updated defense strategy.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/index.html"},
    {"title": "Economic Security Promotion Act (2022)", "organization": "Legislación", "date": "2022-05-11", "category": "Seguridad Económica", "description": "Legal framework for resilience.", "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"},
    {"title": "Fifth Basic Plan for Gender Equality (2020)", "organization": "Gabinete", "date": "2020-12-25", "category": "Género/LGBT+", "description": "Fundamental plan for gender equality.", "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html"}
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
    <guid>{link}</guid>
  </item>"""

    items = []
    for doc in documents[:20]:  # Top 20 for RSS
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
            pub_date=pub_date
        ))

    build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    return rss_template.format(build_date=build_date, items="".join(items))

def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None

def main():
    print("Japan Strategy Monitor - Scraping...")
    all_docs = KNOWN_DOCS.copy()
    
    seen = set()
    final_list = []
    
    all_docs.sort(key=lambda x: x['date'], reverse=True)

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

    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(generate_rss(final_list))

    print(f"✓ Success: {len(final_list)} documents tracked.")

if __name__ == "__main__":
    main()
