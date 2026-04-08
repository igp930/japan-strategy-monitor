# 🇯🇵 Japan Strategy Monitor

**Monitoreo automático de documentos estratégicos del gobierno de Japón**

[![Scraper Status](https://github.com/igp930/japan-strategy-monitor/actions/workflows/scraper.yml/badge.svg)](https://github.com/igp930/japan-strategy-monitor/actions/workflows/scraper.yml)
[![GitHub Pages](https://img.shields.io/badge/web-online-brightgreen)](https://igp930.github.io/japan-strategy-monitor/)

## 📋 Descripción

Este proyecto monitorea y centraliza documentos estratégicos publicados por diferentes agencias del gobierno japonés:

- **MOD** (Ministry of Defense) - Ministerio de Defensa
- **MOFA** (Ministry of Foreign Affairs) - Ministerio de Asuntos Exteriores  
- **Kantei** (Cabinet Office) - Gabinete del Primer Ministro
- **METI** (Ministry of Economy, Trade and Industry) - Ministerio de Economía
- **NISC** (National Center of Incident Readiness and Strategy for Cybersecurity) - Ciberseguridad

## 🌐 Acceso Web

**👉 [https://igp930.github.io/japan-strategy-monitor/](https://igp930.github.io/japan-strategy-monitor/)**

La página web se actualiza automáticamente cada 6 horas con nuevos documentos detectados.

## 🔄 Funcionamiento

### Sistema de Monitoreo Automático

1. **Scraper Python** (`scraper.py`)
   - Visita las páginas oficiales de cada agencia
   - Busca documentos estratégicos usando palabras clave
   - Genera un archivo `documents.json` con los resultados

2. **GitHub Actions** (`.github/workflows/scraper.yml`)
   - Se ejecuta automáticamente cada 6 horas
   - También se puede ejecutar manualmente desde la pestaña Actions
   - Si detecta cambios, actualiza automáticamente el repositorio

3. **Interfaz Web** (`index.html`)
   - Lee dinámicamente desde `documents.json`
   - Muestra la fecha de última actualización
   - Interfaz moderna y responsive

## 📄 Documentos Monitoreados

Actualmente el sistema rastrea:

- National Security Strategy of Japan (2022)
- National Defense Strategy (2022)
- Defense Buildup Program (2022)
- Economic Security Promotion Act
- Diplomatic Bluebook 2025
- Y nuevos documentos que se publiquen en el futuro

## 🛠️ Uso Local

### Requisitos

```bash
pip install requests beautifulsoup4
```

### Ejecutar el Scraper

```bash
python scraper.py
```

Esto generará un archivo `documents.json` con todos los documentos encontrados.

### Ver la Web Localmente

Simplemente abre `index.html` en tu navegador después de ejecutar el scraper.

## 🔧 Configuración

### Modificar Frecuencia de Actualización

Edita `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Cada 6 horas (puedes cambiar esto)
```

### Añadir Nuevas Fuentes

Edita `scraper.py` y añade nuevas URLs en el diccionario `SOURCES`:

```python
SOURCES = {
    "MOD": "https://www.mod.go.jp/j/publication/index.html",
    "NUEVA_AGENCIA": "https://...",
}
```

## 📊 Estructura del Proyecto

```
japan-strategy-monitor/
├── .github/
│   └── workflows/
│       └── scraper.yml          # GitHub Actions workflow
├── index.html                    # Interfaz web
├── scraper.py                    # Script de scraping
├── documents.json                # Datos generados (auto-actualizado)
└── README.md                     # Este archivo
```

## 🚀 Despliegue

El sitio se despliega automáticamente en GitHub Pages:

1. Cada commit a `main` activa un deployment
2. GitHub Pages sirve `index.html`
3. La web lee `documents.json` para mostrar los datos

## 📝 Formato de Datos

El archivo `documents.json` tiene la siguiente estructura:

```json
{
  "last_updated": "2026-04-08T13:35:00",
  "documents": [
    {
      "title": "National Security Strategy of Japan (2022)",
      "organization": "Kantei",
      "date": "2022-12-16",
      "category": "Estratégico",
      "description": "Marco estratégico integrado",
      "url": "https://..."
    }
  ]
}
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🔗 Enlaces Útiles

- [Web del Proyecto](https://igp930.github.io/japan-strategy-monitor/)
- [GitHub Actions](https://github.com/igp930/japan-strategy-monitor/actions)
- [MOD Japan](https://www.mod.go.jp/)
- [MOFA Japan](https://www.mofa.go.jp/)
- [Kantei](https://www.kantei.go.jp/)

---

**Última actualización del README:** Abril 2026
