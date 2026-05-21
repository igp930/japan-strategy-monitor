import json
from datetime import datetime, timezone

documents = []


def add_document(title, organization, date, categories, description, url, status="vigente", lang="en"):
    documents.append({
        "title": title,
        "organization": organization,
        "date": date,
        "categories": categories if isinstance(categories, list) else [categories],
        "description": description,
        "url": url,
        "status": status,
        "lang": lang
    })


def build_documents():
    # 2025
    add_document(
        "Cybersecurity Strategy (2025)",
        "NISC",
        "2025-12-01",
        ["Ciberseguridad", "Estrategia"],
        "Fourth national cybersecurity strategy.",
        "https://www.cyber.go.jp/pdf/policy/kihon-s/cs_strategy2025_abstract_english.pdf",
        "vigente",
        "en"
    )
    add_document(
        "サイバーセキュリティ戦略（2025年）",
        "NISC",
        "2025-12-01",
        ["Ciberseguridad", "Estrategia"],
        "第4次サイバーセキュリティ戦略（日本語版）。",
        "https://www.cyber.go.jp/pdf/policy/kihon-s/cs_strategy2025.pdf",
        "vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2025",
        "MOFA",
        "2025-09-30",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2025.",
        "https://www.mofa.go.jp/policy/other/bluebook/2025/pdf/pdfs/2025_all.pdf",
        "vigente",
        "en"
    )
    add_document(
        "外交青書2025",
        "MOFA",
        "2025-09-30",
        ["Política Exterior"],
        "2025年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2025/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "Defense of Japan 2025 (White Paper)",
        "MOD",
        "2025-07-14",
        ["Defensa", "Estrategia"],
        "Latest Defense White Paper 2025.",
        "https://www.mod.go.jp/j/press/wp/wp2025/pdf/DOJ2025_Digest_EN.pdf",
        "vigente",
        "en"
    )
    add_document(
        "防衛白書2025",
        "MOD",
        "2025-07-14",
        ["Defensa", "Estrategia"],
        "令和7年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2025/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "White Paper on Development Cooperation 2024",
        "MOFA",
        "2025-03-14",
        ["Cooperación Internacional", "Política Exterior"],
        "Annual ODA white paper 2024.",
        "https://www.mofa.go.jp/policy/oda/white/2024/index.html",
        "vigente",
        "en"
    )

    # 2024
    add_document(
        "NIDS China Security Report 2025",
        "NIDS",
        "2024-12-16",
        ["Inteligencia", "Defensa", "Política Exterior"],
        "Annual analysis of China's military trends.",
        "https://www.nids.mod.go.jp/english/publication/chinareport/index.html",
        "vigente",
        "en"
    )
    add_document(
        "Defense of Japan 2024 (White Paper)",
        "MOD",
        "2024-07-12",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2024.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Full.pdf",
        "vigente",
        "en"
    )
    add_document(
        "防衛白書2024",
        "MOD",
        "2024-07-12",
        ["Defensa", "Estrategia"],
        "令和6年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2024/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2024",
        "MOFA",
        "2024-04-16",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2024.",
        "https://www.mofa.go.jp/policy/other/bluebook/2024/pdf/pdfs/2024_all.pdf",
        "vigente",
        "en"
    )
    add_document(
        "外交青書2024",
        "MOFA",
        "2024-04-16",
        ["Política Exterior"],
        "2024年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2024/index.html",
        "vigente",
        "ja"
    )

    # 2023
    add_document(
        "Defense of Japan 2023 (White Paper)",
        "MOD",
        "2023-07-28",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2023.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2023/DOJ2023_EN_Full.pdf",
        "vigente",
        "en"
    )
    add_document(
        "防衛白書2023",
        "MOD",
        "2023-07-28",
        ["Defensa", "Estrategia"],
        "令和5年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2023/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2023",
        "MOFA",
        "2023-04-15",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2023.",
        "https://www.mofa.go.jp/policy/other/bluebook/2023/pdf/pdfs/2023_all.pdf",
        "vigente",
        "en"
    )
    add_document(
        "外交青書2023",
        "MOFA",
        "2023-04-15",
        ["Política Exterior"],
        "2023年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2023/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "New Plan for Free and Open Indo-Pacific (2023)",
        "MOFA",
        "2023-03-20",
        ["Política Exterior", "Estrategia"],
        "Japan's updated FOIP vision.",
        "https://www.mofa.go.jp/files/100477153.pdf",
        "vigente",
        "en"
    )
    add_document(
        "「自由で開かれたインド太平洋」のための新たなプラン（2023年）",
        "MOFA",
        "2023-03-20",
        ["Política Exterior", "Estrategia"],
        "FOIP（自由で開かれたインド太平洋）の新構想（日本語版）。",
        "https://www.mofa.go.jp/mofaj/files/100477004.pdf",
        "vigente",
        "ja"
    )

    # 2022
    add_document(
        "National Security Strategy of Japan (2022)",
        "Kantei",
        "2022-12-16",
        ["Estrategia", "Defensa", "Política Exterior"],
        "Supreme national security document revised Dec 2022.",
        "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
        "vigente",
        "en"
    )
    add_document(
        "国家安全保障戦略（2022年）",
        "Kantei",
        "2022-12-16",
        ["Estrategia", "Defensa", "Política Exterior"],
        "2022年12月改定の国家安全保障戦略（日本語版）。",
        "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-j.pdf",
        "vigente",
        "ja"
    )
    add_document(
        "National Defense Strategy (2022)",
        "MOD",
        "2022-12-16",
        ["Estrategia", "Defensa"],
        "Defense strategy replacing NDPG, Dec 2022.",
        "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/pdf/strategy_en.pdf",
        "vigente",
        "en"
    )
    add_document(
        "国家防衛戦略（2022年）",
        "MOD",
        "2022-12-16",
        ["Estrategia", "Defensa"],
        "2022年12月策定の国家防衛戦略（日本語版）。",
        "https://www.mod.go.jp/j/policy/agenda/guideline/strategy/pdf/strategy.pdf",
        "vigente",
        "ja"
    )
    add_document(
        "Defense Buildup Program (2022)",
        "MOD",
        "2022-12-16",
        ["Estrategia", "Defensa"],
        "Long-term defense procurement plan Dec 2022.",
        "https://www.mod.go.jp/j/policy/agenda/guideline/plan/pdf/program_en.pdf",
        "vigente",
        "en"
    )
    add_document(
        "防衛力整備計画（2022年）",
        "MOD",
        "2022-12-16",
        ["Estrategia", "Defensa"],
        "2022年12月策定の防衛力整備計画（日本語版）。",
        "https://www.mod.go.jp/j/policy/agenda/guideline/plan/pdf/program.pdf",
        "vigente",
        "ja"
    )
    add_document(
        "Defense of Japan 2022 (White Paper)",
        "MOD",
        "2022-07-22",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2022.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2022/DOJ2022_EN_Full_02.pdf",
        "vigente",
        "en"
    )
    add_document(
        "防衛白書2022",
        "MOD",
        "2022-07-22",
        ["Defensa", "Estrategia"],
        "令和4年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2022/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "Economic Security Promotion Act (2022)",
        "Legislación",
        "2022-05-11",
        ["Seguridad Económica", "Estrategia"],
        "Legal framework for economic security.",
        "https://www.meti.go.jp/policy/economy/economic_security/index.html",
        "vigente",
        "en"
    )
    add_document(
        "経済安全保障推進法（2022年）",
        "Legislación",
        "2022-05-11",
        ["Seguridad Económica", "Estrategia"],
        "経済安全保障推進に関する法律（日本語版）。",
        "https://www.meti.go.jp/policy/economy/economic_security/index.html",
        "vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2022",
        "MOFA",
        "2022-04-12",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2022.",
        "https://www.mofa.go.jp/policy/other/bluebook/2022/pdf/pdfs/2022_all.pdf",
        "vigente",
        "en"
    )
    add_document(
        "外交青書2022",
        "MOFA",
        "2022-04-12",
        ["Política Exterior"],
        "2022年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2022/index.html",
        "vigente",
        "ja"
    )

    # 2021
    add_document(
        "Cybersecurity Strategy (2021)",
        "NISC",
        "2021-09-28",
        ["Ciberseguridad", "Estrategia"],
        "Third national cybersecurity strategy.",
        "https://www.cyber.go.jp/pdf/policy/kihon-s/cs-senryaku2021-en-booklet.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "サイバーセキュリティ戦略（2021年）",
        "NISC",
        "2021-09-28",
        ["Ciberseguridad", "Estrategia"],
        "第3次サイバーセキュリティ戦略（日本語版）。",
        "https://www.cyber.go.jp/pdf/policy/kihon-s/cs-senryaku2021.pdf",
        "no_vigente",
        "ja"
    )
    add_document(
        "Defense of Japan 2021 (White Paper)",
        "MOD",
        "2021-07-13",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2021.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2021/DOJ2021_Digest_EN.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2021",
        "MOD",
        "2021-07-13",
        ["Defensa", "Estrategia"],
        "令和3年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2021/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2021",
        "MOFA",
        "2021-04-20",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2021.",
        "https://www.mofa.go.jp/policy/other/bluebook/2021/pdf/pdfs/2021_all.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "外交青書2021",
        "MOFA",
        "2021-04-20",
        ["Política Exterior"],
        "2021年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2021/index.html",
        "no_vigente",
        "ja"
    )

    # 2020
    add_document(
        "Fifth Basic Plan for Gender Equality (2020)",
        "Gabinete",
        "2020-12-25",
        ["Género/LGBT+", "Estrategia"],
        "Fifth national plan for gender equality.",
        "https://www.gender.go.jp/about_danjo/basic_plans/5th/index.html",
        "no_vigente",
        "en"
    )
    add_document(
        "Defense of Japan 2020 (White Paper)",
        "MOD",
        "2020-07-14",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2020.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2020/DOJ2020_Digest_EN.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2020",
        "MOD",
        "2020-07-14",
        ["Defensa", "Estrategia"],
        "令和2年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2020/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2020",
        "MOFA",
        "2020-05-19",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2020.",
        "https://www.mofa.go.jp/policy/other/bluebook/2020/pdf/pdfs/2020_all.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "外交青書2020",
        "MOFA",
        "2020-05-19",
        ["Política Exterior"],
        "2020年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2020/index.html",
        "no_vigente",
        "ja"
    )

    # 2019
    add_document(
        "Defense of Japan 2019 (White Paper)",
        "MOD",
        "2019-09-27",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2019.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2019/DOJ2019_Digest_EN.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2019",
        "MOD",
        "2019-09-27",
        ["Defensa", "Estrategia"],
        "平成31年/令和元年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2019/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2019",
        "MOFA",
        "2019-04-23",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2019.",
        "https://www.mofa.go.jp/policy/other/bluebook/2019/pdf/pdfs/2019_all.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "外交青書2019",
        "MOFA",
        "2019-04-23",
        ["Política Exterior"],
        "2019年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2019/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "National Defense Program Guidelines (2018)",
        "MOD",
        "2018-12-18",
        ["Estrategia", "Defensa"],
        "Previous defense planning document (replaced 2022).",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2019/pdf/20181218_e.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛計画の大綱（2018年）",
        "MOD",
        "2018-12-18",
        ["Estrategia", "Defensa"],
        "2018年12月策定の防衛計画の大綱（日本語版）。2022年に改廃。",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2019/pdf/20181218.pdf",
        "no_vigente",
        "ja"
    )

    # 2018
    add_document(
        "Defense of Japan 2018 (White Paper)",
        "MOD",
        "2018-08-28",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2018.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2018/DOJ2018_Full_1130.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2018",
        "MOD",
        "2018-08-28",
        ["Defensa", "Estrategia"],
        "平成30年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2018/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2018",
        "MOFA",
        "2018-07-01",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2018.",
        "https://www.mofa.go.jp/policy/other/bluebook/2018/html/index.html",
        "no_vigente",
        "en"
    )
    add_document(
        "外交青書2018",
        "MOFA",
        "2018-07-01",
        ["Política Exterior"],
        "2018年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2018/index.html",
        "no_vigente",
        "ja"
    )

    # 2017
    add_document(
        "Defense of Japan 2017 (White Paper)",
        "MOD",
        "2017-08-08",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2017.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2017/DOJ2017_Full_1218.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2017",
        "MOD",
        "2017-08-08",
        ["Defensa", "Estrategia"],
        "平成29年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2017/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2017",
        "MOFA",
        "2017-07-01",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2017.",
        "https://www.mofa.go.jp/policy/other/bluebook/2017/html/index.html",
        "no_vigente",
        "en"
    )

    # 2016
    add_document(
        "Defense of Japan 2016 (White Paper)",
        "MOD",
        "2016-08-02",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2016.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2016/DOJ2016_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2016",
        "MOD",
        "2016-08-02",
        ["Defensa", "Estrategia"],
        "平成28年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2016/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2016",
        "MOFA",
        "2016-07-01",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2016.",
        "https://www.mofa.go.jp/policy/other/bluebook/2016/html/index.html",
        "no_vigente",
        "en"
    )

    # 2015
    add_document(
        "Defense of Japan 2015 (White Paper)",
        "MOD",
        "2015-07-21",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2015.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2015/DOJ2015_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2015",
        "MOD",
        "2015-07-21",
        ["Defensa", "Estrategia"],
        "平成27年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2015/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2015",
        "MOFA",
        "2015-07-01",
        ["Política Exterior"],
        "Annual report on Japan's foreign policy 2015.",
        "https://www.mofa.go.jp/policy/other/bluebook/2015/html/index.html",
        "no_vigente",
        "en"
    )
    add_document(
        "外交青書2015",
        "MOFA",
        "2015-07-01",
        ["Política Exterior"],
        "2015年版外交青書（日本語版）。",
        "https://www.mofa.go.jp/mofaj/gaiko/bluebook/2015/index.html",
        "no_vigente",
        "ja"
    )

    # 2014
    add_document(
        "Defense of Japan 2014 (White Paper)",
        "MOD",
        "2014-08-05",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2014.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2014/DOJ2014_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2014",
        "MOD",
        "2014-08-05",
        ["Defensa", "Estrategia"],
        "平成26年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2014/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2014 (Summary)",
        "MOFA",
        "2014-07-01",
        ["Política Exterior"],
        "Summary of Japan's foreign policy activities 2014.",
        "https://www.mofa.go.jp/policy/other/bluebook/2014/html/index.html",
        "no_vigente",
        "en"
    )

    # 2013
    add_document(
        "National Security Strategy (2013)",
        "Kantei",
        "2013-12-17",
        ["Estrategia", "Defensa", "Política Exterior"],
        "Japan's first-ever National Security Strategy (replaced by 2022 version).",
        "https://www.cas.go.jp/jp/siryou/131217anzenhoshou/nss-e.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "国家安全保障戦略（2013年）",
        "Kantei",
        "2013-12-17",
        ["Estrategia", "Defensa", "Política Exterior"],
        "日本初の国家安全保障戦略（日本語版）。2022年に改廃。",
        "https://www.cas.go.jp/jp/siryou/131217anzenhoshou/nss-j.pdf",
        "no_vigente",
        "ja"
    )
    add_document(
        "National Defense Program Guidelines (2013)",
        "MOD",
        "2013-12-17",
        ["Estrategia", "Defensa"],
        "NDPG for FY2014 and beyond (replaced by 2018 and 2022 revisions).",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2014/pdf/20131217_e2.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛計画の大綱（2013年）",
        "MOD",
        "2013-12-17",
        ["Estrategia", "Defensa"],
        "平成26年度以降に係る防衛計画の大綱（日本語版）。",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2014/pdf/20131217.pdf",
        "no_vigente",
        "ja"
    )
    add_document(
        "Defense of Japan 2013 (White Paper)",
        "MOD",
        "2013-07-26",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2013.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2013/DOJ2013_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2013",
        "MOD",
        "2013-07-26",
        ["Defensa", "Estrategia"],
        "平成25年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2013/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2013 (Summary)",
        "MOFA",
        "2013-07-01",
        ["Política Exterior"],
        "Summary of Japan's foreign policy activities 2013.",
        "https://www.mofa.go.jp/policy/other/bluebook/2013/html/index.html",
        "no_vigente",
        "en"
    )

    # 2012
    add_document(
        "Defense of Japan 2012 (White Paper)",
        "MOD",
        "2012-07-31",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2012.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2012/DOJ2012_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2012",
        "MOD",
        "2012-07-31",
        ["Defensa", "Estrategia"],
        "平成24年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2012/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2012 (Summary)",
        "MOFA",
        "2012-07-01",
        ["Política Exterior"],
        "Summary of Japan's foreign policy activities 2012.",
        "https://www.mofa.go.jp/policy/other/bluebook/2012/html/index.html",
        "no_vigente",
        "en"
    )

    # 2011
    add_document(
        "National Defense Program Guidelines (2010)",
        "MOD",
        "2010-12-17",
        ["Estrategia", "Defensa"],
        "NDPG for FY2011 and beyond. Introduced 'Dynamic Defense Force' concept (replaced by 2013 revision).",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2011/pdf/20101217_e.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛計画の大綱（2010年）",
        "MOD",
        "2010-12-17",
        ["Estrategia", "Defensa"],
        "平成23年度以降に係る防衛計画の大綱（日本語版）。「動的防衛力」概念を初導入。2013年改廃。",
        "https://www.mod.go.jp/j/approach/agenda/guideline/2011/pdf/20101217.pdf",
        "no_vigente",
        "ja"
    )
    add_document(
        "Defense of Japan 2011 (White Paper)",
        "MOD",
        "2011-08-02",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2011.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2011/DOJ2011_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2011",
        "MOD",
        "2011-08-02",
        ["Defensa", "Estrategia"],
        "平成23年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2011/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2011 (Summary)",
        "MOFA",
        "2011-07-01",
        ["Política Exterior"],
        "Summary of Japan's foreign policy activities 2011.",
        "https://www.mofa.go.jp/policy/other/bluebook/2011/html/index.html",
        "no_vigente",
        "en"
    )

    # 2010
    add_document(
        "Defense of Japan 2010 (White Paper)",
        "MOD",
        "2010-08-10",
        ["Defensa", "Estrategia"],
        "Annual Defense White Paper 2010.",
        "https://www.mod.go.jp/en/publ/w_paper/wp2010/DOJ2010_Full.pdf",
        "no_vigente",
        "en"
    )
    add_document(
        "防衛白書2010",
        "MOD",
        "2010-08-10",
        ["Defensa", "Estrategia"],
        "平成22年版防衛白書（日本語版）。",
        "https://www.mod.go.jp/j/press/wp/wp2010/index.html",
        "no_vigente",
        "ja"
    )
    add_document(
        "Diplomatic Bluebook 2010 (Summary)",
        "MOFA",
        "2010-07-01",
        ["Política Exterior"],
        "Summary of Japan's foreign policy activities 2010.",
        "https://www.mofa.go.jp/policy/other/bluebook/2010/html/index.html",
        "no_vigente",
        "en"
    )


def main():
    build_documents()

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "documents": sorted(documents, key=lambda x: x["date"], reverse=True)
    }

    with open("documents.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated documents.json with {len(data['documents'])} documents.")


if __name__ == "__main__":
    main()
