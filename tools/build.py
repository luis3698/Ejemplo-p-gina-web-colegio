# -*- coding: utf-8 -*-
"""
Generador estático del sitio de la Fundación Reserva para la Infancia.

Toma los fragmentos de contenido de `src/*.html`, los envuelve en la
plantilla común (cabecera, navegación, pie, metadatos SEO) y escribe los
archivos HTML finales en la raíz del proyecto.

    python tools/build.py

No requiere dependencias externas.
"""
import io
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

# --------------------------------------------------------------------------
# Datos institucionales (fuente única de verdad)
# --------------------------------------------------------------------------
SITE = {
    "name": "Fundación Reserva para la Infancia",
    "short": "FundaReserva Barichara",
    "tagline": "Educamos por naturaleza",
    "url": "https://www.fundareservabarichara.edu.co",  # cambiar por el dominio real
    "address": "Vía Barichara – San Gil, km 4, vereda El Llano",
    "city": "Barichara",
    "region": "Santander",
    "country": "Colombia",
    "postal": "684041",
    "phone_1": "+57 310 566 4719",
    "phone_1_raw": "+573105664719",
    "phone_2": "+57 318 877 6538",
    "phone_2_raw": "+573188776538",
    "email": "admisiones@fundareservabarichara.edu.co",
    "email_info": "info@fundareservabarichara.edu.co",
    "dane": "368079000334",
    "nit": "804.014.897-7",
    "instagram": "https://www.instagram.com/fundareserva/",
    "facebook": "https://www.facebook.com/FundaReserBarichara/",
    "lat": "6.6355",
    "lon": "-73.2236",
}

NAV = [
    ("index.html", "Inicio"),
    ("nosotros.html", "Nosotros"),
    ("proyecto-educativo.html", "Proyecto educativo"),
    ("niveles.html", "Niveles"),
    ("vida-escolar.html", "Vida escolar"),
    ("noticias.html", "Noticias"),
    ("contacto.html", "Contacto"),
]

PAGES = [
    ("index.html", "Colegio de pedagogía viva en Barichara",
     "Colegio campestre en Barichara, Santander. Preescolar, primaria, secundaria y media "
     "con pedagogía viva y aprendizaje en la naturaleza. 25 años educando por naturaleza."),
    ("nosotros.html", "Quiénes somos",
     "Historia, misión, visión, principios y equipo de la Fundación Reserva para la Infancia, "
     "colegio campestre en Barichara con 25 años de trayectoria."),
    ("proyecto-educativo.html", "Proyecto educativo (PEI)",
     "Pedagogía viva, ambientes de aprendizaje al aire libre, evaluación por procesos y "
     "bilingüismo: así aprendemos en FundaReserva Barichara."),
    ("niveles.html", "Niveles educativos",
     "Preescolar, básica primaria, básica secundaria y educación media. Calendario A, "
     "jornada completa, grupos pequeños en Barichara, Santander."),
    ("vida-escolar.html", "Vida escolar",
     "Campus de reserva natural, huerta escolar, arte, deporte, campamentos y galería "
     "de la vida cotidiana del colegio."),
    ("admisiones.html", "Admisiones 2027",
     "Proceso de admisión paso a paso, requisitos, costos educativos, becas y formulario "
     "de solicitud de cupo para el año escolar 2027."),
    ("noticias.html", "Noticias y agenda",
     "Novedades, circulares y agenda de la comunidad educativa de la Fundación Reserva "
     "para la Infancia en Barichara."),
    ("contacto.html", "Contacto",
     "Teléfonos, correo electrónico, ubicación y formulario de contacto del colegio "
     "FundaReserva en Barichara, Santander."),
    ("404.html", "Página no encontrada",
     "La página que buscas no existe o cambió de dirección."),
]

# --------------------------------------------------------------------------
# Iconos SVG reutilizables
# --------------------------------------------------------------------------
ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "sun": '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "moon": '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 14 6-6 6 6"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2Zm5.5 14.2c-.2.6-1.2 1.2-1.7 1.2-.5.1-1 .1-1.6-.1-.4-.1-.9-.3-1.5-.6-2.6-1.1-4.3-3.7-4.4-3.9-.1-.2-1-1.4-1-2.6s.6-1.8.9-2.1c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.7 1.2 1.6 2 1.1.9 2 1.2 2.3 1.4.3.1.4.1.6-.1l.9-1c.2-.2.4-.2.6-.1l1.8.9c.3.1.5.2.5.3.1.2.1.7-.1 1.3Z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 22v-8h2.7l.4-3.1h-3.1V8.9c0-.9.25-1.5 1.55-1.5H16.7V4.6c-.3 0-1.3-.13-2.45-.13-2.4 0-4.05 1.47-4.05 4.17v2.26H7.5V14h2.7v8Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="2.5" y="4.5" width="19" height="15" rx="3"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 5.2 2 2 0 0 1 6 3Z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m4 12.5 5 5L20 6.5"/></svg>',
}

# --------------------------------------------------------------------------
# Plantilla
# --------------------------------------------------------------------------
HEAD = """<!doctype html>
<html lang="es-CO" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {name}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}/{slug}">
<meta name="theme-color" content="#2E6B3E" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14100C" media="(prefers-color-scheme: dark)">
<meta name="author" content="{name}">
<meta name="robots" content="index, follow">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:locale" content="es_CO">
<meta property="og:title" content="{title} · {name}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}/{slug}">
<meta property="og:image" content="{url}/assets/img/logo.svg">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="assets/img/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/logo.svg">
<link rel="manifest" href="manifest.webmanifest">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/css/style.css">

{bootstrap}
{schema}
</head>
<body>
<a class="skip" href="#main">Saltar al contenido principal</a>
<div class="progress" aria-hidden="true"></div>
"""

BOOTSTRAP = (
    "<script>\n"
    "/* Aplica el tema guardado antes de pintar, para evitar el parpadeo inicial. */\n"
    "(function(){try{var t=localStorage.getItem('fri-theme');"
    "if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';"
    "document.documentElement.setAttribute('data-theme',t);}catch(e){}})();\n"
    "</script>"
)

SCHEMA = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "School",
  "name": "{name}",
  "alternateName": "{short}",
  "slogan": "{tagline}",
  "url": "{url}",
  "logo": "{url}/assets/img/logo.svg",
  "description": "Colegio campestre de pedagogía viva en Barichara, Santander. Preescolar, básica primaria, básica secundaria y educación media. Calendario A.",
  "foundingDate": "2000",
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
  "sameAs": ["{instagram}", "{facebook}"],
  "areaServed": "Barichara, San Gil y la provincia Guanentá",
  "numberOfStudents": 170
}}
</script>"""


def header_html(current):
    links = "".join(
        '<li><a class="nav__link" href="{h}"{cur}>{t}</a></li>'.format(
            h=h, t=t, cur=' aria-current="page"' if h == current else "")
        for h, t in NAV)
    return """<header class="header">
  <div class="wrap header__bar">
    <a class="brand" href="index.html" aria-label="{name} — inicio">
      <img class="brand__mark" src="assets/img/logo.svg" alt="" width="46" height="46">
      <span class="brand__text">
        <span class="brand__name">Reserva para la Infancia</span>
        <span class="brand__tag">{tagline}</span>
      </span>
    </a>
    <nav class="nav" id="nav-principal" aria-label="Navegación principal">
      <ul class="nav__list">{links}</ul>
      <div class="nav__cta"><a class="btn btn--accent" href="admisiones.html">Solicitar cupo 2027</a></div>
    </nav>
    <div class="header__actions">
      <button class="icon-btn" data-open-search aria-label="Buscar en el sitio (Ctrl + K)">{search}</button>
      <button class="icon-btn theme-btn" aria-label="Cambiar de tema">{sun}{moon}</button>
      <a class="btn btn--accent btn--sm header__cta" href="admisiones.html">Admisiones</a>
      <button class="icon-btn nav-toggle" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav-principal">{menu}</button>
    </div>
  </div>
</header>
<main id="main">""".format(name=SITE["name"], tagline=SITE["tagline"], links=links, **{
        "search": ICONS["search"], "sun": ICONS["sun"], "moon": ICONS["moon"], "menu": ICONS["menu"]})


FOOTER = """</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="index.html">
          <img class="brand__mark" src="assets/img/logo.svg" alt="" width="46" height="46">
          <span class="brand__text">
            <span class="brand__name">Reserva para la Infancia</span>
            <span class="brand__tag">{tagline}</span>
          </span>
        </a>
        <p>Colegio campestre de pedagogía viva en Barichara, Santander. Entidad sin ánimo de lucro que
        acompaña a más de 170 niñas, niños y jóvenes desde preescolar hasta grado 11º.</p>
        <div class="socials">
          <a href="{instagram}" target="_blank" rel="noopener noreferrer" aria-label="Instagram">{ig}</a>
          <a href="{facebook}" target="_blank" rel="noopener noreferrer" aria-label="Facebook">{fb}</a>
          <a href="mailto:{email_info}" aria-label="Correo electrónico">{mail}</a>
        </div>
      </div>
      <div>
        <h4>El colegio</h4>
        <ul class="footer__list">
          <li><a href="nosotros.html">Quiénes somos</a></li>
          <li><a href="nosotros.html#historia">Nuestra historia</a></li>
          <li><a href="proyecto-educativo.html">Proyecto educativo</a></li>
          <li><a href="niveles.html">Niveles educativos</a></li>
          <li><a href="vida-escolar.html">Vida escolar</a></li>
        </ul>
      </div>
      <div>
        <h4>Familias</h4>
        <ul class="footer__list">
          <li><a href="admisiones.html">Admisiones 2027</a></li>
          <li><a href="admisiones.html#costos">Costos educativos</a></li>
          <li><a href="admisiones.html#faq">Preguntas frecuentes</a></li>
          <li><a href="noticias.html">Noticias y circulares</a></li>
          <li><a href="vida-escolar.html#calendario">Calendario escolar</a></li>
        </ul>
      </div>
      <div>
        <h4>Contacto</h4>
        <ul class="footer__list">
          <li>{address}<br>{city}, {region}</li>
          <li><a href="tel:{phone_1_raw}">{phone_1}</a></li>
          <li><a href="mailto:{email_info}">{email_info}</a></li>
          <li>Lun a vie · 7:00 a.m. – 3:30 p.m.</li>
          <li>DANE {dane} · NIT {nit}</li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <p>© <span data-year>2026</span> {name}. Todos los derechos reservados.</p>
      <nav aria-label="Enlaces legales">
        <a href="contacto.html#legal">Política de tratamiento de datos</a>
        <a href="contacto.html">Contacto</a>
        <a href="#main">Volver arriba</a>
      </nav>
    </div>
  </div>
</footer>

<a class="wa" href="https://wa.me/{phone_1_clean}?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20admisiones"
   target="_blank" rel="noopener noreferrer" aria-label="Escribir por WhatsApp">{wa}<span>WhatsApp</span></a>
<button class="to-top" aria-label="Volver arriba">{up}</button>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""


def build():
    ctx = dict(SITE)
    ctx["phone_1_clean"] = SITE["phone_1_raw"].lstrip("+")
    footer = FOOTER.format(ig=ICONS["ig"], fb=ICONS["fb"], mail=ICONS["mail"],
                           wa=ICONS["wa"], up=ICONS["up"], **ctx)
    schema = SCHEMA.format(**SITE)

    made = []
    for slug, title, desc in PAGES:
        path = os.path.join(SRC, slug)
        if not os.path.exists(path):
            print("  (falta) src/%s" % slug)
            continue
        body = io.open(path, encoding="utf-8").read()
        # Sustituye marcadores {{clave}} por datos institucionales.
        for k, v in ctx.items():
            body = body.replace("{{%s}}" % k, v)
        for k, v in ICONS.items():
            body = body.replace("{{icon:%s}}" % k, v)

        head = HEAD.format(title=title, desc=desc, slug=slug, bootstrap=BOOTSTRAP,
                           schema=schema if slug == "index.html" else "", **SITE)
        html = head + header_html(slug) + body + footer
        out = os.path.join(ROOT, slug)
        with io.open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        made.append(slug)
        print("  ok  %s (%d KB)" % (slug, len(html) // 1024))

    # sitemap.xml
    today = datetime.date.today().isoformat()
    urls = "".join(
        '  <url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq>'
        '<priority>%s</priority></url>\n'
        % (SITE["url"], s, today,
           "weekly" if s in ("index.html", "noticias.html") else "monthly",
           "1.0" if s == "index.html" else "0.8")
        for s in made if s != "404.html")
    with io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    print("  ok  sitemap.xml")
    print("\nSitio generado: %d páginas." % len(made))


if __name__ == "__main__":
    print("Construyendo el sitio…")
    build()
