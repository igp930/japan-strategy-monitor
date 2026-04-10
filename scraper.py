#!/usr/bin/env python3
"""
Japan Strategy Monitor - Scraper & RSS Generator
Monitorea documentos actuales e históricos del gobierno de Japón.
Genera JSON y RSS para seguimiento automático.
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

# --- DOCUMENTOS CRÍTICOS (BASE DE DATOS INICIAL) ---
KNOWN_DOCS = [
    # --- DEFENSA ---
    {"title": "Defense of Japan 2024 (White Paper)", "organization": "MOD", "date": "2024-07-12", "category": "Defensa", "description": "Latest Defense White Paper.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_Full_1016.pdf"},
    {"title": "Defense of Japan 2023 (White Paper)", "organization": "MOD", "date": "2023-07-28", "category": "Defensa", "description": "Annual report 2023.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_Full_1016.pdf"},
    {"title": "Defense of Japan 2022 (White Paper)", "organization": "MOD", "date": "2022-07-22", "category": "Defensa", "description": "Annual report 2022.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_EN_Full_02.pdf"},
    {"title": "National Security Strategy of Japan (2022)", "organization": "Kantei", "date": "2022-12-16", "category": "Estrategia", "description": "Core security strategy document.", "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"},
    {"title": "National Defense Strategy (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Updated defense strategy.", "url": "https://www.mod.go.jp/en/d_act/d_policy/pdf/strategy20221216_en.pdf"},
    {"title": "Defense Buildup Program (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Long-term defense procurement and force structure.", "url": "https://www.mod.go.jp/en/d_act/d_policy/pdf/program20221216_en.pdf"},
    
    # --- POLÍTICA EXTERIOR ---
    {"title": "Diplomatic Bluebook 2024", "organization": "MOFA", "date": "2024-04-16", "category": "Política Exterior", "description": "Annual report on foreign policy 2024.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf"},
    {"title": "Diplomatic Bluebook 2023", "organization": "MOFA", "date": "2023-04-15", "category": "Política Exterior", "description": "Annual report on foreign policy 2023.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/pdfs/2023_all.pdf"},
    {"title": "Diplomatic Bluebook 2022", "organization": "MOFA", "date": "2022-04-12", "category": "Política Exterior", "description": "Annual report on foreign policy 2022.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/pdfs/2022_all.pdf"},

    # --- SEGURIDAD ECONÓMICA ---
    {"title": "Economic Security Promotion Act (2022)", "organization": "Legislación", "date": "2022-05-11", "category": "Seguridad Económica", "description": "Legal framework for resilience.", "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html"},
    
    # --- OTROS / GÉNERO ---
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print("Japan Strategy Monitor - Initiating comprehensive scan...")
    all_docs = KNOWN_DOCS.copy()
    
    # Intento de descubrimiento simple en MOD (White Papers)
    mod_html = fetch_page(SOURCES["MOD"])
    if mod_html:
        soup = BeautifulSoup(mod_html, 'html.parser')
        # Buscar enlaces que digan "Defense of Japan 20XX" o similar
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
                            "date": f"{year}-01-01",
                            "category": "Defensa",
                            "description": f"Automatically discovered white paper for {year}.",
                            "url": full_url
                        })

    # Filtrado y Limpieza
    seen = set()
    final_list = []
    all_docs.sort(key=lambda x: x['date'], reverse=True)
    
    for d in all_docs:
        if d['url'] not in seen:
            seen.add(d['url'])
            year_val = int(d['date'].split('-')[0])
            if year_val < 2022:
                d['category'] = "Archivo Histórico"
            final_list.append(d)

    output = {
        "last_updated": datetime.now().isoformat(),
        "documents": final_list
    }

    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(generate_rss(final_list))
    print(f"✓ Success: {len(final_list)} documents tracked and updated.")

if __name__ == "__main__":
    main()
