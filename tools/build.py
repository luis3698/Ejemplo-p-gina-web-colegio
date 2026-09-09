# -*- coding: utf-8 -*-
"""
Generador estático del sitio web escolar (plantilla genérica y bilingüe).

Toma los fragmentos de contenido de `src/<idioma>/*.html`, los envuelve en la
plantilla común (cabecera, navegación, pie, metadatos SEO) y escribe los
archivos HTML finales:

    español  ->  /*.html
    inglés   ->  /en/*.html

Uso:
    python tools/build.py

No requiere dependencias externas.
"""
import io
import os
import json
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
PHOTO_DIR = os.path.join(ROOT, "assets", "img", "photos")

# ==========================================================================
# 1. CONFIGURACIÓN — edita solo esta sección para adaptar el sitio
# ==========================================================================
SITE = {
    # --- Identidad ---------------------------------------------------------
    "name": "Colegio Ejemplo",
    "short": "Colegio Ejemplo",
    "url": "https://www.colegioejemplo.edu.co",   # dominio real, sin barra final

    # --- Contacto ----------------------------------------------------------
    "address": "Calle 00 # 00 - 00",
    "city": "Ciudad",
    "region": "Departamento",
    "country": "Colombia",
    "postal": "000000",
    "phone_1": "+57 300 000 0000",
    "phone_1_raw": "+573000000000",
    "phone_2": "+57 (60) 000 0000",
    "phone_2_raw": "+576000000000",
    "email": "admisiones@colegioejemplo.edu.co",
    "email_info": "info@colegioejemplo.edu.co",

    # --- Datos institucionales --------------------------------------------
    "dane": "000000000000",
    "nit": "000.000.000-0",
    "founded": "1995",
    "lat": "4.7110",
    "lon": "-74.0721",

    # --- Redes sociales (usa "#" si aún no aplica) -------------------------
    "instagram": "#",
    "facebook": "#",
    "youtube": "#",

    # --- MEJORA 1: envío real de formularios -------------------------------
    # Pega aquí el endpoint de Formspree, Web3Forms, Getform o tu propio
    # backend. Mientras diga PENDIENTE, los formularios funcionan en modo
    # demostración (validan, muestran el mensaje de éxito y no envían nada).
    "form_endpoint": "PENDIENTE",
    # Para Web3Forms, pon aquí tu access key; para Formspree déjalo vacío.
    "form_access_key": "",
}

# Anchos generados por tools/optimize_images.py (MEJORA 2)
PHOTO_WIDTHS = [480, 768, 1200, 1600]

# ==========================================================================
# 2. IDIOMAS (MEJORA 6)
# ==========================================================================
LANGS = {
    "es": {
        "code": "es",
        "html_lang": "es-CO",
        "og_locale": "es_CO",
        "dir": "",            # carpeta de salida (raíz)
        "base": "",           # prefijo hacia assets/
        "label": "Español",
        "switch_label": "English",
        "switch_short": "EN",
        "tagline": "Educación con propósito",
        "nav": [
            ("index.html", "Inicio"),
            ("nosotros.html", "Nosotros"),
            ("proyecto-educativo.html", "Proyecto educativo"),
            ("niveles.html", "Niveles"),
            ("vida-escolar.html", "Vida escolar"),
            ("noticias.html", "Noticias"),
            ("contacto.html", "Contacto"),
        ],
        "cta_nav": "Solicitar cupo",
        "cta_header": "Admisiones",
        "skip": "Saltar al contenido principal",
        "search_aria": "Buscar en el sitio (Ctrl + K)",
        "theme_aria": "Cambiar de tema",
        "menu_aria": "Abrir menú",
        "home_aria": "Inicio",
        "footer": {
            "about": "Institución educativa de calendario A que acompaña a niñas, niños y "
                     "jóvenes desde preescolar hasta grado 11º, con un modelo pedagógico "
                     "propio y formación integral.",
            "col1": "El colegio",
            "col2": "Familias",
            "col3": "Contacto",
            "hours": "Lun a vie · 7:00 a.m. – 3:30 p.m.",
            "rights": "Todos los derechos reservados.",
            "legal": "Política de tratamiento de datos",
            "contact": "Contacto",
            "top": "Volver arriba",
            "links1": [
                ("nosotros.html", "Quiénes somos"),
                ("nosotros.html#historia", "Nuestra historia"),
                ("proyecto-educativo.html", "Proyecto educativo"),
                ("niveles.html", "Niveles educativos"),
                ("vida-escolar.html", "Vida escolar"),
            ],
            "links2": [
                ("admisiones.html", "Admisiones"),
                ("admisiones.html#costos", "Costos educativos"),
                ("admisiones.html#faq", "Preguntas frecuentes"),
                ("noticias.html", "Noticias y circulares"),
                ("vida-escolar.html#calendario", "Calendario escolar"),
            ],
        },
        "wa_text": "Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20admisiones",
        "wa_label": "WhatsApp",
        "top_aria": "Volver arriba",
        "i18n": {
            "searchPlaceholder": "Buscar: admisiones, proyecto educativo, costos…",
            "searchAria": "Buscar en el sitio",
            "searchEmpty": "Sin resultados para “{q}”. Prueba con «admisiones» o «niveles».",
            "sending": "Enviando…",
            "formError": "No pudimos enviar el mensaje. Inténtalo de nuevo o escríbenos por WhatsApp.",
            "formDemo": "Modo demostración: el formulario se validó correctamente, pero aún no hay "
                        "un destinatario configurado. Ver README.md, sección «Conectar los formularios».",
            "closeMenu": "Cerrar menú",
            "openMenu": "Abrir menú",
            "themeLight": "Cambiar a tema claro",
            "themeDark": "Cambiar a tema oscuro",
        },
    },
    "en": {
        "code": "en",
        "html_lang": "en",
        "og_locale": "en_US",
        "dir": "en",
        "base": "../",
        "label": "English",
        "switch_label": "Español",
        "switch_short": "ES",
        "tagline": "Education with purpose",
        "nav": [
            ("index.html", "Home"),
            ("nosotros.html", "About us"),
            ("proyecto-educativo.html", "Our approach"),
            ("niveles.html", "Programs"),
            ("vida-escolar.html", "School life"),
            ("noticias.html", "News"),
            ("contacto.html", "Contact"),
        ],
        "cta_nav": "Request a place",
        "cta_header": "Admissions",
        "skip": "Skip to main content",
        "search_aria": "Search the site (Ctrl + K)",
        "theme_aria": "Switch theme",
        "menu_aria": "Open menu",
        "home_aria": "Home",
        "footer": {
            "about": "A calendar-A school supporting children and young people from preschool "
                     "through eleventh grade, with its own pedagogical model and an education "
                     "that develops the whole person.",
            "col1": "The school",
            "col2": "Families",
            "col3": "Contact",
            "hours": "Mon to Fri · 7:00 a.m. – 3:30 p.m.",
            "rights": "All rights reserved.",
            "legal": "Data protection policy",
            "contact": "Contact",
            "top": "Back to top",
            "links1": [
                ("nosotros.html", "About us"),
                ("nosotros.html#historia", "Our history"),
                ("proyecto-educativo.html", "Our approach"),
                ("niveles.html", "Programs"),
                ("vida-escolar.html", "School life"),
            ],
            "links2": [
                ("admisiones.html", "Admissions"),
                ("admisiones.html#costos", "Tuition and fees"),
                ("admisiones.html#faq", "Frequently asked questions"),
                ("noticias.html", "News and circulars"),
                ("vida-escolar.html#calendario", "School calendar"),
            ],
        },
        "wa_text": "Hello%2C%20I%27d%20like%20information%20about%20admissions",
        "wa_label": "WhatsApp",
        "top_aria": "Back to top",
        "i18n": {
            "searchPlaceholder": "Search: admissions, approach, tuition…",
            "searchAria": "Search the site",
            "searchEmpty": "No results for “{q}”. Try “admissions” or “programs”.",
            "sending": "Sending…",
            "formError": "We couldn't send your message. Please try again or reach us on WhatsApp.",
            "formDemo": "Demo mode: the form validated correctly, but no recipient is configured yet. "
                        "See README.md, section “Connecting the forms”.",
            "closeMenu": "Close menu",
            "openMenu": "Open menu",
            "themeLight": "Switch to light theme",
            "themeDark": "Switch to dark theme",
        },
    },
}

# ==========================================================================
# 3. PÁGINAS (título y descripción por idioma)
# ==========================================================================
PAGES = [
    ("index.html", {
        "es": ("Institución educativa de formación integral",
               "Colegio de calendario A con preescolar, primaria, secundaria y media. "
               "Modelo pedagógico propio, grupos reducidos y formación integral."),
        "en": ("A school for the whole person",
               "Calendar-A school offering preschool, primary, lower and upper secondary "
               "education, with small groups and its own pedagogical model."),
    }),
    ("nosotros.html", {
        "es": ("Quiénes somos",
               "Historia, misión, visión, principios y equipo de la institución educativa."),
        "en": ("About us",
               "History, mission, vision, principles and team of the school."),
    }),
    ("proyecto-educativo.html", {
        "es": ("Proyecto educativo (PEI)",
               "Modelo pedagógico, pilares de formación, ambientes de aprendizaje y "
               "sistema institucional de evaluación."),
        "en": ("Our educational approach",
               "Pedagogical model, pillars of learning, learning environments and the "
               "institutional assessment system."),
    }),
    ("niveles.html", {
        "es": ("Niveles educativos",
               "Preescolar, básica primaria, básica secundaria y educación media. "
               "Calendario A, jornada completa y grupos reducidos."),
        "en": ("Programs",
               "Preschool, primary, lower secondary and upper secondary education. "
               "Calendar A, full-day schedule and small groups."),
    }),
    ("vida-escolar.html", {
        "es": ("Vida escolar",
               "Campus, programas complementarios, galería, calendario escolar y servicios."),
        "en": ("School life",
               "Campus, co-curricular programs, gallery, school calendar and services."),
    }),
    ("admisiones.html", {
        "es": ("Admisiones",
               "Proceso de admisión paso a paso, requisitos, costos educativos, becas y "
               "formulario de solicitud de cupo."),
        "en": ("Admissions",
               "Step-by-step admissions process, requirements, tuition, financial aid and "
               "the application form."),
    }),
    ("noticias.html", {
        "es": ("Noticias y agenda",
               "Novedades, circulares y agenda de la comunidad educativa."),
        "en": ("News and calendar",
               "Updates, circulars and the calendar of the school community."),
    }),
    ("contacto.html", {
        "es": ("Contacto",
               "Teléfonos, correo electrónico, ubicación y formulario de contacto."),
        "en": ("Contact",
               "Phone numbers, email, location and contact form."),
    }),
    ("404.html", {
        "es": ("Página no encontrada", "La página que buscas no existe o cambió de dirección."),
        "en": ("Page not found", "The page you are looking for doesn't exist or has moved."),
    }),
]

# ==========================================================================
# 4. Iconos SVG reutilizables
# ==========================================================================
ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "sun": '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "moon": '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 14 6-6 6 6"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2Zm5.5 14.2c-.2.6-1.2 1.2-1.7 1.2-.5.1-1 .1-1.6-.1-.4-.1-.9-.3-1.5-.6-2.6-1.1-4.3-3.7-4.4-3.9-.1-.2-1-1.4-1-2.6s.6-1.8.9-2.1c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.7 1.2 1.6 2 1.1.9 2 1.2 2.3 1.4.3.1.4.1.6-.1l.9-1c.2-.2.4-.2.6-.1l1.8.9c.3.1.5.2.5.3.1.2.1.7-.1 1.3Z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 22v-8h2.7l.4-3.1h-3.1V8.9c0-.9.25-1.5 1.55-1.5H16.7V4.6c-.3 0-1.3-.13-2.45-.13-2.4 0-4.05 1.47-4.05 4.17v2.26H7.5V14h2.7v8Z"/></svg>',
    "yt": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8ZM10 15V9l5.2 3Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="2.5" y="4.5" width="19" height="15" rx="3"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 5.2 2 2 0 0 1 6 3Z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m4 12.5 5 5L20 6.5"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18Z"/></svg>',
}

# ==========================================================================
# 5. MEJORA 2 — sistema de fotografía responsiva
# ==========================================================================
_manifest_cache = None


def photo_manifest():
    """Lee assets/img/photos/manifest.json si tools/optimize_images.py ya corrió."""
    global _manifest_cache
    if _manifest_cache is None:
        path = os.path.join(PHOTO_DIR, "manifest.json")
        try:
            _manifest_cache = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            _manifest_cache = {}
    return _manifest_cache


def photo(slug, alt, fallback, base="", sizes="100vw", priority=False, ratio=None):
    """Devuelve un <picture> responsivo si existen las fotos optimizadas del
    slug; si no, devuelve la ilustración de marcador de posición.

    Así el sitio nunca muestra imágenes rotas: en cuanto el colegio deje sus
    fotos en assets/img/originals/ y ejecute tools/optimize_images.py, el
    generador empieza a emitir <picture> automáticamente."""
    entry = photo_manifest().get(slug)
    loading = 'loading="eager" fetchpriority="high"' if priority else 'loading="lazy"'
    alt_attr = alt.replace('"', "&quot;")

    if not entry:
        return ('<img src="{b}assets/img/{f}" alt="{a}" width="1000" height="750" '
                '{l} decoding="async">').format(b=base, f=fallback, a=alt_attr, l=loading)

    widths = entry.get("widths", PHOTO_WIDTHS)
    w, h = entry.get("width", 1600), entry.get("height", 1200)
    lqip = entry.get("lqip", "")

    def srcset(ext):
        return ", ".join("{b}assets/img/photos/{s}-{w}.{e} {w}w".format(b=base, s=slug, w=x, e=ext)
                         for x in widths)

    style = ' style="background-image:url({0});background-size:cover;background-position:center"'.format(lqip) if lqip else ""
    return (
        '<picture{st}>'
        '<source type="image/avif" srcset="{avif}" sizes="{sz}">'
        '<source type="image/webp" srcset="{webp}" sizes="{sz}">'
        '<img src="{b}assets/img/photos/{s}-{last}.jpg" srcset="{jpg}" sizes="{sz}" '
        'alt="{a}" width="{w}" height="{h}" {l} decoding="async">'
        '</picture>'
    ).format(st=style, avif=srcset("avif"), webp=srcset("webp"), jpg=srcset("jpg"),
             sz=sizes, b=base, s=slug, last=widths[-1], a=alt_attr, w=w, h=h, l=loading)


# ==========================================================================
# 6. Plantilla HTML
# ==========================================================================
HEAD = """<!doctype html>
<html lang="{html_lang}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {name}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es" href="{alt_es}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="x-default" href="{alt_es}">
<meta name="theme-color" content="#2E6B3E" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14100C" media="(prefers-color-scheme: dark)">
<meta name="author" content="{name}">
<meta name="robots" content="index, follow">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:title" content="{title} · {name}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{url}/assets/img/logo.svg">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="{base}assets/img/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{base}assets/img/logo.svg">
<link rel="manifest" href="{base}manifest.webmanifest">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{base}assets/css/style.css">

{bootstrap}
<script>window.SITE_I18N = {i18n};</script>
{schema}
</head>
<body>
<a class="skip" href="#main">{skip}</a>
<div class="progress" aria-hidden="true"></div>
"""

BOOTSTRAP = (
    "<script>\n"
    "/* Aplica el tema guardado antes de pintar, para evitar el parpadeo inicial. */\n"
    "(function(){try{var t=localStorage.getItem('site-theme');"
    "if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';"
    "document.documentElement.setAttribute('data-theme',t);}catch(e){}})();\n"
    "</script>"
)

SCHEMA = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "School",
  "name": "{name}",
  "url": "{url}",
  "logo": "{url}/assets/img/logo.svg",
  "description": "Institución educativa de calendario A con preescolar, básica primaria, básica secundaria y educación media.",
  "foundingDate": "{founded}",
  "telephone": "{phone_1}",
  "email": "{email_info}",
  "identifier": [
    {{"@type": "PropertyValue", "name": "Código DANE", "value": "{dane}"}},
    {{"@type": "PropertyValue", "name": "NIT", "value": "{nit}"}}
  ],
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{address}",
    "addressLocality": "{city}",
    "addressRegion": "{region}",
    "postalCode": "{postal}",
    "addressCountry": "CO"
  }},
  "geo": {{"@type": "GeoCoordinates", "latitude": "{lat}", "longitude": "{lon}"}},
  "inLanguage": ["es", "en"]
}}
</script>"""


def header_html(lang, current):
    """Cabecera con navegación, buscador, tema y selector de idioma."""
    L = LANGS[lang]
    other = LANGS["en" if lang == "es" else "es"]
    base = L["base"]

    links = "".join(
        '<li><a class="nav__link" href="{h}"{cur}>{t}</a></li>'.format(
            h=h, t=t, cur=' aria-current="page"' if h == current else "")
        for h, t in L["nav"])

    # Enlace a la misma página en el otro idioma.
    if lang == "es":
        switch_href = "en/" + current
    else:
        switch_href = "../" + current

    return """<header class="header">
  <div class="wrap header__bar">
    <a class="brand" href="index.html" aria-label="{name} — {home}">
      <img class="brand__mark" src="{base}assets/img/logo.svg" alt="" width="46" height="46">
      <span class="brand__text">
        <span class="brand__name">{name}</span>
        <span class="brand__tag">{tagline}</span>
      </span>
    </a>
    <nav class="nav" id="nav-principal" aria-label="{home}">
      <ul class="nav__list">{links}</ul>
      <div class="nav__cta">
        <a class="btn btn--accent" href="admisiones.html">{cta_nav}</a>
        <a class="lang-switch lang-switch--block" href="{switch}" hreflang="{ocode}" lang="{ocode}">{globe}<span>{olabel}</span></a>
      </div>
    </nav>
    <div class="header__actions">
      <a class="lang-switch" href="{switch}" hreflang="{ocode}" lang="{ocode}"
         aria-label="{olabel}">{globe}<span>{oshort}</span></a>
      <button class="icon-btn" data-open-search aria-label="{search_aria}">{search}</button>
      <button class="icon-btn theme-btn" aria-label="{theme_aria}">{sun}{moon}</button>
      <a class="btn btn--accent btn--sm header__cta" href="admisiones.html">{cta_header}</a>
      <button class="icon-btn nav-toggle" aria-label="{menu_aria}" aria-expanded="false" aria-controls="nav-principal">{menu}</button>
    </div>
  </div>
</header>
<main id="main">""".format(
        name=SITE["name"], tagline=L["tagline"], links=links, base=base,
        home=L["home_aria"], cta_nav=L["cta_nav"], cta_header=L["cta_header"],
        search_aria=L["search_aria"], theme_aria=L["theme_aria"], menu_aria=L["menu_aria"],
        switch=switch_href, olabel=other["label"], oshort=other["switch_short"], ocode=other["code"],
        search=ICONS["search"], sun=ICONS["sun"], moon=ICONS["moon"],
        menu=ICONS["menu"], globe=ICONS["globe"])


FOOTER = """</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="index.html">
          <img class="brand__mark" src="{base}assets/img/logo.svg" alt="" width="46" height="46">
          <span class="brand__text">
            <span class="brand__name">{name}</span>
            <span class="brand__tag">{tagline}</span>
          </span>
        </a>
        <p>{about}</p>
        <div class="socials">
          <a href="{instagram}" target="_blank" rel="noopener noreferrer" aria-label="Instagram">{ig}</a>
          <a href="{facebook}" target="_blank" rel="noopener noreferrer" aria-label="Facebook">{fb}</a>
          <a href="{youtube}" target="_blank" rel="noopener noreferrer" aria-label="YouTube">{yt}</a>
          <a href="mailto:{email_info}" aria-label="{email_info}">{mail}</a>
        </div>
      </div>
      <div>
        <h4>{col1}</h4>
        <ul class="footer__list">{links1}</ul>
      </div>
      <div>
        <h4>{col2}</h4>
        <ul class="footer__list">{links2}</ul>
      </div>
      <div>
        <h4>{col3}</h4>
        <ul class="footer__list">
          <li>{address}<br>{city}, {region}</li>
          <li><a href="tel:{phone_1_raw}">{phone_1}</a></li>
          <li><a href="mailto:{email_info}">{email_info}</a></li>
          <li>{hours}</li>
          <li>DANE {dane} · NIT {nit}</li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <p>© <span data-year>2026</span> {name}. {rights}</p>
      <nav aria-label="{legal}">
        <a href="contacto.html#legal">{legal}</a>
        <a href="contacto.html">{contact}</a>
        <a href="#main">{top}</a>
      </nav>
    </div>
  </div>
</footer>

<a class="wa" href="https://wa.me/{phone_1_clean}?text={wa_text}"
   target="_blank" rel="noopener noreferrer" aria-label="{wa_label}">{wa}<span>{wa_label}</span></a>
<button class="to-top" aria-label="{top_aria}">{up}</button>
<script src="{base}assets/js/main.js" defer></script>
</body>
</html>
"""


def footer_html(lang):
    L = LANGS[lang]
    F = L["footer"]
    ctx = dict(SITE)
    ctx["phone_1_clean"] = SITE["phone_1_raw"].lstrip("+")
    li = lambda pairs: "".join('<li><a href="{0}">{1}</a></li>'.format(h, t) for h, t in pairs)
    return FOOTER.format(
        base=L["base"], tagline=L["tagline"], about=F["about"],
        col1=F["col1"], col2=F["col2"], col3=F["col3"],
        links1=li(F["links1"]), links2=li(F["links2"]),
        hours=F["hours"], rights=F["rights"], legal=F["legal"],
        contact=F["contact"], top=F["top"],
        wa_text=L["wa_text"], wa_label=L["wa_label"], top_aria=L["top_aria"],
        ig=ICONS["ig"], fb=ICONS["fb"], yt=ICONS["yt"], mail=ICONS["mail"],
        wa=ICONS["wa"], up=ICONS["up"], **ctx)


# ==========================================================================
# 7. Índice del buscador interno (por idioma)
# ==========================================================================
SEARCH = {
    "es": [
        ("Inicio", "Presentación general de la institución educativa.", "index.html"),
        ("Quiénes somos", "Historia, misión, visión, principios y equipo.", "nosotros.html"),
        ("Nuestra historia", "Línea de tiempo de la institución.", "nosotros.html#historia"),
        ("Misión y visión", "Horizonte institucional.", "nosotros.html#horizonte"),
        ("Equipo directivo", "Rectoría, coordinación y docentes.", "nosotros.html#equipo"),
        ("Datos institucionales", "NIT, código DANE, calendario y jornadas.", "nosotros.html#datos"),
        ("Proyecto educativo", "Modelo pedagógico y PEI.", "proyecto-educativo.html"),
        ("Modelo pedagógico", "Cómo aprenden nuestros estudiantes.", "proyecto-educativo.html#modelo"),
        ("Ambientes de aprendizaje", "Aulas, laboratorios, biblioteca y espacios abiertos.", "proyecto-educativo.html#ambientes"),
        ("Evaluación", "Sistema institucional de evaluación (SIEE).", "proyecto-educativo.html#evaluacion"),
        ("Documentos institucionales", "PEI, manual de convivencia, SIEE y PRAE.", "proyecto-educativo.html#documentos"),
        ("Niveles educativos", "Preescolar, primaria, secundaria y media.", "niveles.html"),
        ("Preescolar", "Pre-jardín, jardín y transición.", "niveles.html#preescolar"),
        ("Básica primaria", "Grados 1º a 5º.", "niveles.html#primaria"),
        ("Básica secundaria", "Grados 6º a 9º.", "niveles.html#secundaria"),
        ("Educación media", "Grados 10º y 11º y preparación Saber 11.", "niveles.html#media"),
        ("Resultados Saber 11", "Promedios institucionales por área.", "niveles.html#resultados"),
        ("Vida escolar", "Campus, programas, galería y calendario.", "vida-escolar.html"),
        ("Campus", "Instalaciones y espacios del colegio.", "vida-escolar.html#campus"),
        ("Galería", "Fotografías de la vida cotidiana.", "vida-escolar.html#galeria"),
        ("Calendario escolar", "Fechas clave del año.", "vida-escolar.html#calendario"),
        ("Admisiones", "Proceso, requisitos y costos.", "admisiones.html"),
        ("Proceso de admisión", "Cinco pasos hasta la matrícula.", "admisiones.html#proceso"),
        ("Requisitos y documentos", "Qué necesitas para matricularte.", "admisiones.html#requisitos"),
        ("Costos educativos", "Matrícula, pensión, becas y descuentos.", "admisiones.html#costos"),
        ("Preguntas frecuentes", "Transporte, alimentación, uniformes y más.", "admisiones.html#faq"),
        ("Formulario de admisión", "Solicita tu cupo en línea.", "admisiones.html#formulario"),
        ("Noticias y agenda", "Novedades y circulares.", "noticias.html"),
        ("Contacto", "Teléfonos, correo, mapa y formulario.", "contacto.html"),
        ("Cómo llegar", "Ubicación y rutas de acceso.", "contacto.html#mapa"),
        ("Tratamiento de datos", "Política de protección de datos personales.", "contacto.html#legal"),
    ],
    "en": [
        ("Home", "General presentation of the school.", "index.html"),
        ("About us", "History, mission, vision, principles and team.", "nosotros.html"),
        ("Our history", "Timeline of the institution.", "nosotros.html#historia"),
        ("Mission and vision", "Institutional horizon.", "nosotros.html#horizonte"),
        ("Leadership team", "Head of school, coordinators and teachers.", "nosotros.html#equipo"),
        ("Institutional data", "Tax ID, ministry code, calendar and schedules.", "nosotros.html#datos"),
        ("Our approach", "Pedagogical model and institutional project.", "proyecto-educativo.html"),
        ("Pedagogical model", "How our students learn.", "proyecto-educativo.html#modelo"),
        ("Learning environments", "Classrooms, labs, library and open spaces.", "proyecto-educativo.html#ambientes"),
        ("Assessment", "Institutional assessment system.", "proyecto-educativo.html#evaluacion"),
        ("Institutional documents", "Educational project, code of conduct and more.", "proyecto-educativo.html#documentos"),
        ("Programs", "Preschool, primary, lower and upper secondary.", "niveles.html"),
        ("Preschool", "Pre-kindergarten, kindergarten and transition.", "niveles.html#preescolar"),
        ("Primary school", "Grades 1 to 5.", "niveles.html#primaria"),
        ("Lower secondary", "Grades 6 to 9.", "niveles.html#secundaria"),
        ("Upper secondary", "Grades 10 and 11, and national exam preparation.", "niveles.html#media"),
        ("Exam results", "Institutional averages by subject.", "niveles.html#resultados"),
        ("School life", "Campus, programs, gallery and calendar.", "vida-escolar.html"),
        ("Campus", "Facilities and school spaces.", "vida-escolar.html#campus"),
        ("Gallery", "Photographs of daily school life.", "vida-escolar.html#galeria"),
        ("School calendar", "Key dates of the year.", "vida-escolar.html#calendario"),
        ("Admissions", "Process, requirements and tuition.", "admisiones.html"),
        ("Admissions process", "Five steps to enrolment.", "admisiones.html#proceso"),
        ("Requirements", "What you need to enrol.", "admisiones.html#requisitos"),
        ("Tuition and fees", "Enrolment, monthly fees, aid and discounts.", "admisiones.html#costos"),
        ("Frequently asked questions", "Transport, meals, uniforms and more.", "admisiones.html#faq"),
        ("Application form", "Request a place online.", "admisiones.html#formulario"),
        ("News and calendar", "Updates and circulars.", "noticias.html"),
        ("Contact", "Phone, email, map and form.", "contacto.html"),
        ("Getting here", "Location and access routes.", "contacto.html#mapa"),
        ("Data protection", "Personal data protection policy.", "contacto.html#legal"),
    ],
}


# ==========================================================================
# 8. Construcción
# ==========================================================================
def build():
    ctx = dict(SITE)
    ctx["phone_1_clean"] = SITE["phone_1_raw"].lstrip("+")
    schema = SCHEMA.format(**SITE)
    today = datetime.date.today().isoformat()
    made = []

    for lang, L in LANGS.items():
        out_dir = os.path.join(ROOT, L["dir"]) if L["dir"] else ROOT
        if L["dir"] and not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        i18n = dict(L["i18n"])
        i18n["formEndpoint"] = SITE["form_endpoint"]
        i18n["formAccessKey"] = SITE["form_access_key"]
        i18n["search"] = [{"t": t, "d": d, "u": u} for t, d, u in SEARCH[lang]]
        i18n_json = json.dumps(i18n, ensure_ascii=False, separators=(",", ":"))

        footer = footer_html(lang)

        for slug, titles in PAGES:
            frag = os.path.join(SRC, lang, slug)
            if not os.path.exists(frag):
                print("  (falta) src/%s/%s" % (lang, slug))
                continue
            title, desc = titles[lang]
            body = io.open(frag, encoding="utf-8").read()

            # Marcadores de datos institucionales e iconos.
            for k, v in ctx.items():
                body = body.replace("{{%s}}" % k, str(v))
            for k, v in ICONS.items():
                body = body.replace("{{icon:%s}}" % k, v)
            body = body.replace("{{base}}", L["base"])
            # Marcador de fotografía: {{photo:slug|alt|fallback.svg|sizes|priority}}
            body = expand_photos(body, L["base"])

            canonical = "%s/%s%s" % (SITE["url"], (L["dir"] + "/") if L["dir"] else "", slug)
            head = HEAD.format(
                title=title, desc=desc, canonical=canonical,
                alt_es="%s/%s" % (SITE["url"], slug),
                alt_en="%s/en/%s" % (SITE["url"], slug),
                html_lang=L["html_lang"], og_locale=L["og_locale"], base=L["base"],
                bootstrap=BOOTSTRAP, i18n=i18n_json, skip=L["skip"],
                schema=schema if slug == "index.html" else "",
                name=SITE["name"], url=SITE["url"])

            html = head + header_html(lang, slug) + body + footer
            with io.open(os.path.join(out_dir, slug), "w", encoding="utf-8", newline="\n") as f:
                f.write(html)
            made.append((lang, slug))
            print("  ok  %s%s (%d KB)" % ((L["dir"] + "/") if L["dir"] else "", slug, len(html) // 1024))

    write_sitemap(made, today)
    print("\nSitio generado: %d páginas (%d idiomas)." % (len(made), len(LANGS)))
    if SITE["form_endpoint"] == "PENDIENTE":
        print("Aviso: los formularios están en modo demostración. "
              "Configura SITE['form_endpoint'] para activar el envío real.")
    if not photo_manifest():
        print("Aviso: no hay fotografías optimizadas. Se usan las ilustraciones de marcador "
              "de posición. Ejecuta tools/optimize_images.py cuando tengas fotos reales.")


def expand_photos(body, base):
    """Sustituye {{photo:slug|alt|fallback|sizes|priority}} por <picture> o <img>."""
    out, i = [], 0
    token = "{{photo:"
    while True:
        j = body.find(token, i)
        if j == -1:
            out.append(body[i:])
            break
        k = body.find("}}", j)
        if k == -1:
            out.append(body[i:])
            break
        out.append(body[i:j])
        parts = body[j + len(token):k].split("|")
        slug = parts[0].strip()
        alt = parts[1].strip() if len(parts) > 1 else ""
        fallback = parts[2].strip() if len(parts) > 2 else "escena-aula.svg"
        sizes = parts[3].strip() if len(parts) > 3 else "(min-width: 920px) 50vw, 100vw"
        priority = len(parts) > 4 and parts[4].strip() == "priority"
        out.append(photo(slug, alt, fallback, base=base, sizes=sizes, priority=priority))
        i = k + 2
    return "".join(out)


def write_sitemap(made, today):
    """Sitemap con alternates hreflang para las dos versiones de cada página."""
    slugs = []
    for slug, _ in PAGES:
        if slug == "404.html":
            continue
        slugs.append(slug)

    rows = []
    for lang, L in LANGS.items():
        prefix = (L["dir"] + "/") if L["dir"] else ""
        for slug in slugs:
            if (lang, slug) not in made:
                continue
            alts = "".join(
                '\n    <xhtml:link rel="alternate" hreflang="{c}" href="{u}/{p}{s}"/>'.format(
                    c=LANGS[l2]["code"], u=SITE["url"],
                    p=(LANGS[l2]["dir"] + "/") if LANGS[l2]["dir"] else "", s=slug)
                for l2 in LANGS)
            rows.append(
                '  <url>\n    <loc>{u}/{p}{s}</loc>\n    <lastmod>{d}</lastmod>'
                '\n    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>{a}\n  </url>'
                .format(u=SITE["url"], p=prefix, s=slug, d=today,
                        c="weekly" if slug in ("index.html", "noticias.html") else "monthly",
                        pr="1.0" if slug == "index.html" and not prefix else "0.8",
                        a=alts))

    with io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
                '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + "\n".join(rows) + "\n</urlset>\n")
    print("  ok  sitemap.xml")


if __name__ == "__main__":
    print("Construyendo el sitio...")
    build()
