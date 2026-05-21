#!/usr/bin/env python3
"""
Japan Strategy Monitor - Enhanced Scraper v2.0
Monitorea documentos actuales e historicos del gobierno de Japon.
Etiqueta automaticamente documentos no vigentes (<2022).
"""

import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

SOURCES = {
    "MOD": "https://www.mod.go.jp/en/publ/w_paper/index.html",
    "MOFA": "https://www.mofa.go.jp/policy/other/bluebook/index.html",
    "MOFA_ODA": "https://www.mofa.go.jp/policy/oda/white/index.html",
    "MOFA_FOIP": "https://www.mofa.go.jp/policy/page25e_000278.html",
    "Kantei": "https://www.cas.go.jp/jp/siryou/index.html",
    "METI": "https://www.meti.go.jp/policy/economy/economic_security/index.html",
    "NISC": "https://www.cyber.go.jp/eng/",
    "NIDS": "https://www.nids.mod.go.jp/english/publication/chinareport/index.html"
}

KNOWN_DOCS = [
    {"title": "Defense of Japan 2025 (White Paper)", "organization": "MOD", "date": "2025-07-14", "category": "Defensa", "description": "Latest Defense White Paper 2025.", "url": "https://www.mod.go.jp/j/press/wp/wp2025/pdf/DOJ2025_Digest_EN.pdf", "status": "vigente"},
    {"title": "Defense of Japan 2024 (White Paper)", "organization": "MOD", "date": "2024-07-12", "category": "Defensa", "description": "Annual Defense White Paper 2024.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Full.pdf", "status": "vigente"},
    {"title": "Defense of Japan 2023 (White Paper)", "organization": "MOD", "date": "2023-07-28", "category": "Defensa", "description": "Annual Defense White Paper 2023.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_EN_Full.pdf", "status": "vigente"},
    {"title": "Defense of Japan 2022 (White Paper)", "organization": "MOD", "date": "2022-07-22", "category": "Defensa", "description": "Annual Defense White Paper 2022.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_EN_Full_02.pdf", "status": "vigente"},
    {"title": "Defense of Japan 2021 (White Paper)", "organization": "MOD", "date": "2021-07-13", "category": "Defensa", "description": "Annual Defense White Paper 2021.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2021/DOJ2021_Digest_EN.pdf", "status": "no_vigente"},
    {"title": "Defense of Japan 2020 (White Paper)", "organization": "MOD", "date": "2020-07-14", "category": "Defensa", "description": "Annual Defense White Paper 2020.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2020/DOJ2020_Digest_EN.pdf", "status": "no_vigente"},
    {"title": "Defense of Japan 2019 (White Paper)", "organization": "MOD", "date": "2019-09-27", "category": "Defensa", "description": "Annual Defense White Paper 2019.", "url": "https://www.mod.go.jp/en/publ/w_paper/wp2019/DOJ2019_Digest_EN.pdf", "status": "no_vigente"},
    {"title": "National Security Strategy of Japan (2022)", "organization": "Kantei", "date": "2022-12-16", "category": "Estrategia", "description": "Supreme national security document revised Dec 2022.", "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf", "status": "vigente"},
    {"title": "National Defense Strategy (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Defense strategy replacing NDPG, Dec 2022.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/pdf/strategy_en.pdf", "status": "vigente"},
    {"title": "Defense Buildup Program (2022)", "organization": "MOD", "date": "2022-12-16", "category": "Estrategia", "description": "Long-term defense procurement plan Dec 2022.", "url": "https://www.mod.go.jp/j/policy/agenda/guideline/plan/pdf/program_en.pdf", "status": "vigente"},
    {"title": "National Defense Program Guidelines (2018)", "organization": "MOD", "date": "2018-12-18", "category": "Estrategia", "description": "Previous defense planning document (replaced 2022).", "url": "https://www.mod.go.jp/j/approach/agenda/guideline/2019/pdf/20181218_e.pdf", "status": "no_vigente"},
    {"title": "Diplomatic Bluebook 2025", "organization": "MOFA", "date": "2025-09-30", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2025.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2025/pdf/pdfs/2025_all.pdf", "status": "vigente"},
    {"title": "Diplomatic Bluebook 2024", "organization": "MOFA", "date": "2024-04-16", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2024.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf", "status": "vigente"},
    {"title": "Diplomatic Bluebook 2023", "organization": "MOFA", "date": "2023-04-15", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2023.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/pdfs/2023_all.pdf", "status": "vigente"},
    {"title": "Diplomatic Bluebook 2022", "organization": "MOFA", "date": "2022-04-12", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2022.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/pdfs/2022_all.pdf", "status": "vigente"},
    {"title": "Diplomatic Bluebook 2021", "organization": "MOFA", "date": "2021-04-20", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2021.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2021/pdf/pdfs/2021_all.pdf", "status": "no_vigente"},
    {"title": "Diplomatic Bluebook 2020", "organization": "MOFA", "date": "2020-05-19", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2020.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2020/pdf/pdfs/2020_all.pdf", "status": "no_vigente"},
    {"title": "Diplomatic Bluebook 2019", "organization": "MOFA", "date": "2019-04-23", "category": "Politica Exterior", "description": "Annual report on Japan's foreign policy 2019.", "url": "https://www.mofa.go.jp/policy/other/bluebook/2019/pdf/pdfs/2019_all.pdf", "status": "no_vigente"},
    {"title": "New Plan for Free and Open Indo-Pacific (2023)", "organization": "MOFA", "date": "2023-03-20", "category": "Politica Exterior", "description": "Japan's updated FOIP vision.", "url": "https://www.mofa.go.jp/files/100477153.pdf", "status": "vigente"},
    {"title": "White Paper on Development Cooperation 2024", "organization": "MOFA", "date": "2025-03-14", "category": "Cooperacion Internacional", "description": "Annual ODA white paper 2024.", "url": "https://www.mofa.go.jp/policy/oda/white/2024/index.html", "status": "vigente"},
    {"title": "Cybersecurity Strategy (2025)", "organization": "NISC", "date": "2025-12-01", "category": "Ciberseguridad", "description": "Fourth national cybersecurity strategy.", "url": "https://www.cyber.go.jp/pdf/policy/kihon-s/cs_strategy2025_abstract_english.pdf", "status": "vigente"},
    {"title": "Cybersecurity Strategy (2021)", "organization": "NISC", "date": "2021-09-28", "category": "Ciberseguridad", "description": "Third national cybersecurity strategy.", "url": "https://www.cyber.go.jp/pdf/policy/kihon-s/cs-senryaku2021-en-booklet.pdf", "status": "no_vigente"},
    {"title": "NIDS China Security Report 2025", "organization": "NIDS", "date": "2024-12-16", "category": "Inteligencia", "description": "Annual analysis of China's military trends.", "url": "https://www.nids.mod.go.jp/english/publication/chinareport/index.html", "status": "vigente"},
    {"title": "Economic Security Promotion Act (2022)", "organization": "Legislacion", "date": "2022-05-11", "category": "Seguridad Economica", "description": "Legal framework for economic security.", "url": "https://www.meti.go.jp/policy/economy/economic_security/index.html", "status": "vigente"},
    {"title": "Fifth Basic Plan for Gender Equality (2020)", "organization": "Gabinete", "date": "2020-12-25", "category": "Archivo Historico", "description": "Fifth national plan for gender equality.", "url": "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html", "status": "no_vigente"}
]

def generate_rss(documents):
    rss_template = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Japan Strategy Monitor Feed</title>
    <link>https://igp930.github.io/japan-strategy-monitor/</link>
    <description>Latest strategic documents from Japan</description>
    <language>en-us</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    {items}
  </channel>
</rss>"""
    item_template = """    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{desc} ({org})</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{guid}</guid>
    </item>"""
    items = []
    for doc in documents[:30]:
        try:
            dt = datetime.strptime(doc['date'], '%Y-%m-%d')
            pub_date = dt.strftime('%a, %d %b %Y 00:00:00 +0000')
        except:
            pub_date = datetime.now().strftime('%a, %d %b %Y 00:00:00 +0000')
        items.append(item_template.format(title=doc['title'], link=doc['url'], desc=doc.get('description', ''), org=doc['organization'], pub_date=pub_date, guid=doc['url']))
    build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    return rss_template.format(build_date=build_date, items="\n".join(items))

def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def auto_mark_status(doc):
    if 'status' not in doc:
        try:
            year = int(doc['date'].split('-')[0])
            doc['status'] = 'no_vigente' if year < 2022 else 'vigente'
        except:
            doc['status'] = 'vigente'
    return doc

def main():
    print("Japan Strategy Monitor - Enhanced v2.0 scan...")
    all_docs = [auto_mark_status(d.copy()) for d in KNOWN_DOCS]
    mod_html = fetch_page(SOURCES["MOD"])
    if mod_html:
        soup = BeautifulSoup(mod_html, 'html.parser')
        for link in soup.find_all('a', href=True):
            if "Defense of Japan" in link.text or "DEFENSE OF JAPAN" in link.text:
                year_match = re.search(r'20\d{2}', link.text)
                if year_match:
                    year = year_match.group()
                    url = link['href'] if link['href'].startswith('http') else "https://www.mod.go.jp" + link['href']
                    if not any(d['url'] == url for d in all_docs):
                        all_docs.append(auto_mark_status({"title": f"Defense of Japan {year}", "organization": "MOD", "date": f"{year}-07-01", "category": "Defensa", "description": f"White paper {year}.", "url": url}))
    mofa_html = fetch_page(SOURCES["MOFA"])
    if mofa_html:
        soup = BeautifulSoup(mofa_html, 'html.parser')
        for link in soup.find_all('a', href=True):
            if "Bluebook" in link.text or "BLUEBOOK" in link.text:
                year_match = re.search(r'20\d{2}', link.text)
                if year_match and 'pdf' in link['href'].lower():
                    year = year_match.group()
                    url = link['href'] if link['href'].startswith('http') else f"https://www.mofa.go.jp{link['href']}"
                    if not any(d['url'] == url for d in all_docs):
                        all_docs.append(auto_mark_status({"title": f"Diplomatic Bluebook {year}", "organization": "MOFA", "date": f"{year}-04-15", "category": "Politica Exterior", "description": f"Bluebook {year}.", "url": url}))
    seen = set()
    final_list = []
    all_docs.sort(key=lambda x: x['date'], reverse=True)
    for d in all_docs:
        if d['url'] not in seen:
            seen.add(d['url'])
            final_list.append(auto_mark_status(d))
    output = {"last_updated": datetime.now().isoformat(), "documents": final_list}
    with open('documents.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(generate_rss(final_list))
    vigentes = sum(1 for d in final_list if d.get('status') == 'vigente')
    no_vigentes = sum(1 for d in final_list if d.get('status') == 'no_vigente')
    print(f"✓ Success: {len(final_list)} docs ({vigentes} vigentes, {no_vigentes} archivo)")

if __name__ == "__main__":
    main()
