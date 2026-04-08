#!/usr/bin/env python3
"""
Japan Strategy Monitor — Scraper
Extrae documentos estratégicos de MOD, MOFA, Kantei, METI y NISC.
Guarda los resultados en data/documents.json.
"""

import json, time, hashlib, re
from datetime import datetime, timezone
from pathlib import Path
import urllib.request, urllib.error
from html.parser import HTMLParser

OUTPUT = Path(__file__).parent / "documents.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JapanStrategyMonitor/3.0)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}

SOURCES = [
    {
        "id": "mod_press",
        "name": "MOD — Press Releases",
        "org": "MOD",
        "url": "https://www.mod.go.jp/en/press-release/",
        "base": "https://www.mod.go.jp",
        "keywords": ["defense","strategy","security","budget","capability",
                     "cyber","missile","deterrence","alliance","hypersonic",
                     "counterstrike","standoff","drone","space"],
        "category": "defensa",
    },
    {
        "id": "mod_policy",
        "name": "MOD — Defense Policy",
        "org": "MOD",
        "url": "https://www.mod.go.jp/en/d_policy/index.html",
        "base": "https://www.mod.go.jp",
        "keywords": ["national defense strategy","defense buildup","nds","nss",
                     "guideline","program","white paper"],
        "category": "defensa",
    },
    {
        "id": "mofa_press",
        "name": "MOFA — Press Releases",
        "org": "MOFA",
        "url": "https://www.mofa.go.jp/press/release/index.html",
        "base": "https://www.mofa.go.jp",
        "keywords": ["security","strategy","defense","diplomacy","sanctions",
                     "alliance","economic","bluebook","quad","g7","nato"],
        "category": "exterior",
    },
    {
        "id": "kantei_decisions",
        "name": "Kantei — Decisions & Policies",
        "org": "Kantei",
        "url": "https://japan.kantei.go.jp/decisions/index.html",
        "base": "https://japan.kantei.go.jp",
        "keywords": ["security","economic","defense","strategy","policy",
                     "semiconductor","supply chain","critical","resilience"],
        "category": "economica",
    },
    {
        "id": "meti_econ_sec",
        "name": "METI — Economic Security",
        "org": "METI",
        "url": "https://www.meti.go.jp/english/policy/economy/economic_security/index.html",
        "base": "https://www.meti.go.jp",
        "keywords": ["economic security","supply chain","technology","critical",
                     "semiconductor","strategic","patent","export control"],
        "category": "economica",
    },
    {
        "id": "nisc",
        "name": "NISC — Cybersecurity",
        "org": "NISC",
        "url": "https://www.nisc.go.jp/eng/index.html",
        "base": "https://www.nisc.go.jp",
        "keywords": ["cyber","security","active defense","infrastructure",
                     "incident","strategy","guidelines","resilience"],
        "category": "seguridad",
    },
    {
        "id": "mod_news",
        "name": "MOD — Latest News",
        "org": "MOD",
        "url": "https://www.mod.go.jp/en/timeline/index.html",
        "base": "https://www.mod.go.jp",
        "keywords": ["defense","security","exercise","alliance","cyber",
                     "budget","acquisition","missile","satellite"],
        "category": "defensa",
    },
]

CORPUS = [
    {"id":"nss2022","title":"National Security Strategy of Japan (2022)","category":"seguridad","source":"Kantei","date":"2022-12-16","desc":"Marco estratégico integrado: diplomacia, defensa, ciberseguridad, inteligencia y seguridad económica.","url":"https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf","tags":["nss","national security strategy","cyber","economic security"],"isStrategic":True},
    {"id":"nds2022","title":"National Defense Strategy (2022)","category":"defensa","source":"MOD","date":"2022-12-16","desc":"Estrategia de defensa nacional: objetivos, capacidades y arquitectura de fuerza.","url":"https://www.mod.go.jp/en/d_policy/index.html","tags":["national defense strategy","capabilities","alliance"],"isStrategic":True},
    {"id":"dbp2022","title":"Defense Buildup Program (2022)","category":"defensa","source":"MOD","date":"2022-12-16","desc":"Programa de refuerzo de capacidades con partidas presupuestarias y plazos.","url":"https://www.mod.go.jp/en/d_policy/index.html","tags":["defense buildup","budget","procurement"],"isStrategic":True},
    {"id":"esa2022","title":"Economic Security Promotion Act","category":"economica","source":"METI","date":"2022-05-11","desc":"Cadenas de suministro, infraestructura crítica y tecnologías estratégicas.","url":"https://www.meti.go.jp/english/policy/economy/economic_security/index.html","tags":["economic security","supply chain","critical infrastructure"],"isStrategic":True},
    {"id":"bb2025","title":"Diplomatic Bluebook 2025","category":"exterior","source":"MOFA","date":"2025-03-01","desc":"Síntesis de política exterior, alianzas y prioridades diplomáticas de Japón.","url":"https://www.mofa.go.jp/policy/other/bluebook/2025/en_html/chapter3/c030101.html","tags":["bluebook","foreign policy","alliances","diplomacy"],"isStrategic":True},
    {"id":"doj2024","title":"Defense of Japan 2024 (White Paper)","category":"defensa","source":"MOD","date":"2024-07-12","desc":"Libro Blanco anual 2024: entorno de seguridad, capacidades y política de defensa.","url":"https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Reference.pdf","tags":["white paper","annual report","2024"],"isStrategic":True},
    {"id":"fy2026bgt","title":"FY2026 Defense Budget Overview","category":"defensa","source":"MOD","date":"2025-12-26","desc":"Presupuesto de defensa FY2026 con asignaciones por categoría de capacidad.","url":"https://www.mod.go.jp/en/d_act/d_budget/pdf/fy2026_20251226a.pdf","tags":["budget","fy2026","defense spending"],"isStrategic":False},
    {"id":"bp2026","title":"Basic Policy 2026","category":"economica","source":"Kantei","date":"2026-02-17","desc":"Política básica 2026: inversiones estratégicas y resiliencia económica.","url":"https://japan.kantei.go.jp/105/decisions/2026/_00001.html","tags":["basic policy","2026","economic resilience"],"isStrategic":False},
    {"id":"eco2025","title":"Council for Economic Security — Nov 2025","category":"economica","source":"Kantei","date":"2025-11-06","desc":"Sesión del consejo de seguridad económica. Resiliencia, tecnologías críticas e inversión.","url":"https://japan.kantei.go.jp/104/actions/202511/07keizaianpo.html","tags":["economic security","council","resilience"],"isStrategic":False},
    {"id":"cyber2025","title":"Cybersecurity Strategy 2025","category":"seguridad","source":"NISC","date":"2025-06-01","desc":"Active Cyber Defense, protección de infraestructura crítica y coordinación nacional.","url":"https://www.nisc.go.jp/eng/index.html","tags":["cyber","active cyber defense","critical infrastructure"],"isStrategic":True},
]


class LinkParser(HTMLParser):
    def __init__(self, base_url, keywords):
        super().__init__()
        self.base_url = base_url
        self.keywords = [k.lower() for k in keywords]
        self.links = []
        self._current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, val in attrs:
                if name == "href" and val:
                    self._current_href = val.strip()

    def handle_data(self, data):
        text = data.strip()
        if not text or not self._current_href:
            return
        combined = (text + " " + self._current_href).lower()
        if any(kw in combined for kw in self.keywords) and len(text) > 14:
            href = self._current_href
            if href.startswith("http"):
                abs_url = href
            elif href.startswith("/"):
                abs_url = self.base_url.rstrip("/") + href
            else:
                abs_url = self.base_url
            self.links.append({"text": text, "url": abs_url})
        self._current_href = None

    def handle_endtag(self, tag):
        if tag == "a":
            self._current_href = None


def fetch_html(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            charset = "utf-8"
            ct = r.headers.get_content_charset()
            if ct:
                charset = ct
            return r.read().decode(charset, errors="replace")
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return None


def doc_id(source_id, text):
    h = hashlib.md5(text.encode()).hexdigest()[:10]
    return f"live-{source_id}-{h}"


def scrape_source(source):
    print(f"  Scraping {source['name']}…")
    html = fetch_html(source["url"])
    if not html:
        return []

    parser = LinkParser(source["base"], source["keywords"])
    parser.feed(html)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []
    seen = set()

    for link in parser.links:
        text = re.sub(r"\s+", " ", link["text"]).strip()
        if len(text) < 15 or len(text) > 300:
            continue
        key = text[:60].lower()
        if key in seen:
            continue
        seen.add(key)

        matched_kw = [kw for kw in source["keywords"] if kw in (text + " " + link["url"]).lower()]

        results.append({
            "id": doc_id(source["id"], text),
            "title": text,
            "category": source["category"],
            "source": source["org"],
            "date": today,
            "desc": f"Publicación detectada en {source['name']}. Palabras clave: {', '.join(matched_kw[:3])}.",
            "url": link["url"],
            "tags": matched_kw[:5],
            "isStrategic": False,
            "isNew": True,
        })

    print(f"    → {len(results[:8])} entradas relevantes")
    return results[:8]


def load_existing():
    if OUTPUT.exists():
        with open(OUTPUT) as f:
            data = json.load(f)
        return {d["id"]: d for d in data.get("documents", [])}
    return {}


def main():
    print("\n=== Japan Strategy Monitor — Scraper ===")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    existing = load_existing()

    # Preserve corpus (always)
    for doc in CORPUS:
        existing[doc["id"]] = doc

    new_count = 0
    for source in SOURCES:
        docs = scrape_source(source)
        for doc in docs:
            if doc["id"] not in existing:
                existing[doc["id"]] = doc
                new_count += 1
        time.sleep(1.5)  # polite crawl delay

    all_docs = sorted(existing.values(), key=lambda d: d["date"], reverse=True)

    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "updated": datetime.now(timezone.utc).isoformat(),
            "total": len(all_docs),
            "new_this_run": new_count,
            "documents": all_docs,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✓ {len(all_docs)} documentos totales ({new_count} nuevos)")
    print(f"✓ Guardado en {OUTPUT}")


if __name__ == "__main__":
    main()
