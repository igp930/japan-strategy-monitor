# 🇯🇵 Japan Strategy Monitor

**Monitoreo automático de documentos estratégicos del gobierno de Japón**

[![Scraper Status](https://github.com/igp930/japan-strategy-monitor/actions/workflows/scraper.yml/badge.svg)](https://github.com/igp930/japan-strategy-monitor/actions/workflows/scraper.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-blue)](https://igp930.github.io/japan-strategy-monitor/)

## 📋 Descripción

Este proyecto monitorea, organiza y centraliza documentos estratégicos publicados por diferentes agencias del gobierno japonés, con cobertura histórica desde 2010 y soporte para documentos en inglés y japonés.

Fuentes principales:

- **MOD** (Ministry of Defense)
- **MOFA** (Ministry of Foreign Affairs)
- **Kantei / CAS** (Cabinet Secretariat / Prime Minister's Office)
- **METI** (Ministry of Economy, Trade and Industry)
- **NISC** (National Center of Incident Readiness and Strategy for Cybersecurity)
- **Gender Equality Bureau / Cabinet Office**

El sistema está pensado para seguir documentos de defensa, estrategia, política exterior, seguridad económica, ciberseguridad y derechos, teniendo en cuenta que un mismo documento puede pertenecer a varias categorías simultáneamente.

## 🌐 Acceso web

**👉 [https://igp930.github.io/japan-strategy-monitor/](https://igp930.github.io/japan-strategy-monitor/)**

La página web se actualiza automáticamente a partir del archivo `documents.json`, regenerado por `scraper.py` y publicado en GitHub Pages.

## 🔄 Funcionamiento

### 1. Scraper Python (`scraper.py`)

El script:

- genera un archivo `documents.json`
- organiza los documentos por fecha
- asigna múltiples categorías por documento mediante el campo `categories`
- distingue entre documentos vigentes y no vigentes
- diferencia idioma (`en` / `ja`)
- conserva una base histórica desde 2010

### 2. GitHub Actions (`.github/workflows/scraper.yml`)

El workflow:

- se ejecuta automáticamente cada 6 horas
- también puede ejecutarse manualmente desde la pestaña **Actions**
- regenera `documents.json`
- hace commit automático si detecta cambios

### 3. Interfaz web (`index.html`)

La web:

- lee dinámicamente los datos desde `documents.json`
- muestra la fecha de última actualización
- permite filtrar por texto
- permite filtrar por categoría
- permite filtrar por idioma
- permite filtrar por vigencia
- soporta documentos con múltiples categorías

## 📄 Tipos de documentos incluidos

El sistema puede incluir, entre otros:

- **Defense of Japan / 防衛白書**
- **Diplomatic Bluebook / 外交青書**
- **National Security Strategy / 国家安全保障戦略**
- **National Defense Strategy / 国家防衛戦略**
- **Defense Buildup Program / 防衛力整備計画**
- **National Defense Program Guidelines / 防衛計画の大綱**
- **Economic Security Promotion Act / 経済安全保障推進法**
- **Cybersecurity Strategy / サイバーセキュリティ戦略**
- **Planes de igualdad y otros documentos estratégicos transversales**

## 🛠️ Uso local

### Requisitos

Instala Python 3 y, si en el futuro amplías el scraper con scraping real, las dependencias necesarias.

Ejemplo:

```bash
pip install requests beautifulsoup4
```

### Ejecutar el scraper

```bash
python scraper.py
```

Esto generará o actualizará `documents.json`.

### Ver la web localmente

Abre `index.html` en tu navegador después de generar `documents.json`.

## 🔧 Configuración

### Modificar frecuencia de actualización

Edita `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'
```

Eso ejecuta el workflow cada 6 horas.

### Añadir nuevas fuentes o documentos

Edita `scraper.py` para:

- añadir nuevas agencias
- añadir nuevas familias documentales
- ampliar categorías
- ajustar idiomas
- marcar vigencia histórica

## 📊 Estructura del proyecto

```text
japan-strategy-monitor/
├── .github/
│   └── workflows/
│       └── scraper.yml
├── index.html
├── scraper.py
├── documents.json
└── README.md
```

## 📝 Formato de datos

El archivo `documents.json` tiene esta estructura:

```json
{
  "last_updated": "2026-05-21T08:00:00+00:00",
  "documents": [
    {
      "title": "National Security Strategy of Japan (2022)",
      "organization": "Kantei",
      "date": "2022-12-16",
      "categories": ["Estrategia", "Defensa", "Política Exterior"],
      "description": "Supreme national security document revised Dec 2022.",
      "url": "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
      "status": "vigente",
      "lang": "en"
    }
  ]
}
```

### Campos

- `title`: título del documento
- `organization`: institución responsable
- `date`: fecha del documento en formato `YYYY-MM-DD`
- `categories`: lista de categorías asignadas al documento
- `description`: breve descripción
- `url`: enlace al documento o página oficial
- `status`: `vigente` o `no_vigente`
- `lang`: idioma del documento, normalmente `en` o `ja`

## 🧭 Categorías sugeridas

Las categorías actualmente previstas son:

- `Defensa`
- `Política Exterior`
- `Estrategia`
- `Seguridad Económica`
- `Ciberseguridad`
- `Cooperación Internacional`
- `Inteligencia`
- `Género/LGBT+`

Un mismo documento puede pertenecer a una o varias de ellas.

## 🚀 Despliegue

El sitio se despliega automáticamente en GitHub Pages:

1. cada commit a `main` puede activar un deployment
2. GitHub Pages sirve `index.html`
3. la web carga `documents.json`
4. los cambios en el JSON se reflejan directamente en la interfaz

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. haz un fork del proyecto
2. crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. haz commit (`git commit -m "Añadir nueva funcionalidad"`)
4. sube la rama (`git push origin feature/nueva-funcionalidad`)
5. abre un Pull Request

## 📜 Licencia

Este proyecto está disponible bajo licencia MIT.

## 🔗 Enlaces útiles

- [Web del proyecto](https://igp930.github.io/japan-strategy-monitor/)
- [GitHub Actions](https://github.com/igp930/japan-strategy-monitor/actions)
- [MOD Japan](https://www.mod.go.jp/)
- [MOFA Japan](https://www.mofa.go.jp/)
- [Kantei / CAS](https://www.cas.go.jp/)
- [METI](https://www.meti.go.jp/)
- [NISC](https://www.cyber.go.jp/)

---

**Última actualización del README:** Mayo 2026
