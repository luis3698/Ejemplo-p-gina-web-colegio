# Plantilla de sitio web escolar

Sitio web institucional completo para colegios, en **español e inglés**, sin frameworks ni
dependencias de terceros. Todo el contenido y la identidad son marcadores de posición
genéricos: se adapta a cualquier institución editando un solo archivo de configuración.

---

## 1. Qué incluye

**18 páginas HTML estáticas** — nueve en español (raíz) y nueve en inglés (`/en/`):

| Archivo | Contenido |
|---|---|
| `index.html` | Portada: hero, cifras, diferenciales, enfoque, niveles, campus, resultados, testimonios, noticias, CTA |
| `nosotros.html` | Misión, visión, propósito, 6 principios, línea de tiempo, equipo, datos institucionales |
| `proyecto-educativo.html` | Modelo pedagógico, 6 pilares, ambientes de aprendizaje, evaluación (SIEE), documentos |
| `niveles.html` | Preescolar, primaria, secundaria, media; resultados Saber 11; estructura de la jornada |
| `vida-escolar.html` | Campus, programas, galería con filtros y lightbox, calendario escolar, servicios |
| `admisiones.html` | Proceso en 5 pasos, requisitos, costos, 7 preguntas frecuentes, formulario |
| `noticias.html` | Noticias filtrables por categoría y agenda de eventos |
| `contacto.html` | Datos de contacto, formulario, mapa, política de tratamiento de datos |
| `404.html` | Página de error |

Además: `sitemap.xml` con alternates `hreflang`, `robots.txt`, `manifest.webmanifest` (PWA)
y `sw.js` (service worker).

---

## 2. Cómo verlo

```bash
python -m http.server 5173
```

Luego abre <http://localhost:5173>. La versión en inglés está en `/en/`.

---

## 3. Estructura del proyecto

```
.
├── index.html … 404.html       ← páginas en español (generadas, NO editar a mano)
├── en/                         ← páginas en inglés (generadas)
├── src/
│   ├── es/                     ← contenido editable en español
│   └── en/                     ← contenido editable en inglés
├── tools/
│   ├── build.py                ← generador: configuración + plantilla + idiomas
│   ├── optimize_images.py      ← convierte tus fotos a AVIF/WebP/JPG responsivos
│   └── make_placeholders.py    ← regenera las ilustraciones de marcador de posición
├── assets/
│   ├── css/style.css           ← sistema de diseño completo
│   ├── js/main.js              ← toda la interactividad
│   ├── img/
│   │   ├── logo.svg            ← logotipo (reemplázalo por el real)
│   │   ├── escena-*.svg        ← ilustraciones de marcador de posición
│   │   ├── originals/          ← AQUÍ van tus fotos originales
│   │   └── photos/             ← versiones optimizadas (generadas)
│   └── docs/                   ← aquí van los PDF institucionales
├── manifest.webmanifest · sw.js · robots.txt · sitemap.xml
└── README.md
```

### Cómo editar el contenido

1. Edita el fragmento en `src/es/` y su equivalente en `src/en/`.
2. Ejecuta el generador:

```bash
python tools/build.py
```

Esto reconstruye las 18 páginas y regenera `sitemap.xml`. La cabecera, el menú, el pie, los
metadatos SEO y los textos de interfaz viven en un solo lugar (`tools/build.py`), así que un
cambio se propaga a todo el sitio en ambos idiomas.

### Adaptar la plantilla a tu institución

Abre `tools/build.py` y edita **solo el diccionario `SITE`** (sección 1). Ahí están el nombre,
el dominio, la dirección, los teléfonos, los correos, el NIT, el código DANE, las coordenadas
y las redes sociales. Dentro de `src/` se usan como marcadores: `{{name}}`, `{{phone_1}}`,
`{{email}}`, `{{address}}`, `{{dane}}`, etc.

Para cambiar la paleta, edita los tokens de color de la sección 1 de `assets/css/style.css`.
Todo el sitio los hereda.

---

## 4. Las tres mejoras implementadas

### MEJORA 1 — Formularios conectados de verdad

Los formularios de admisiones y contacto ya no simulan el envío: hacen un `POST` real por
`fetch()` al endpoint que configures, con estado de carga, mensaje de éxito, mensaje de error
recuperable y trampa antispam.

**Para activarlo** (unos 5 minutos, sin necesidad de backend):

1. Crea una cuenta gratuita en [Formspree](https://formspree.io), [Web3Forms](https://web3forms.com)
   o [Getform](https://getform.io) y obtén la URL del endpoint.
2. En `tools/build.py`, en el diccionario `SITE`:

   ```python
   "form_endpoint": "https://formspree.io/f/TU_ID",
   "form_access_key": "",   # solo para Web3Forms
   ```

3. Ejecuta `python tools/build.py`.

Eso es todo. A partir de ahí:

- El `<form>` recibe `action` y `method="POST"` automáticamente.
- Se envían todos los campos más `_subject`, `_language` (es/en) y `_page`, para que sepas
  desde qué idioma y qué página llegó cada solicitud.
- Si la red falla, el usuario ve un mensaje de error en su idioma y el botón se reactiva
  para reintentar.
- El campo trampa `_gotcha` está oculto para las personas: si un robot lo rellena, el envío
  se descarta en silencio.

**Mientras `form_endpoint` diga `PENDIENTE`**, los formularios quedan en modo demostración:
validan correctamente y avisan con claridad que todavía no hay destinatario configurado.
El generador te lo recuerda en cada compilación.

### MEJORA 2 — Sistema de fotografía profesional

No basta con subir fotos bonitas: hay que servirlas en el formato y el tamaño correctos.
El proyecto trae el pipeline completo.

**Cómo usarlo:**

```bash
pip install pillow
# 1. Copia tus fotos en assets/img/originals/ con el nombre del slug (campus.jpg, aula.jpg…)
python tools/optimize_images.py
python tools/build.py
```

Qué hace por cada foto:

- Genera cuatro anchos (480, 768, 1200 y 1600 px) en **AVIF, WebP y JPG**.
- Calcula un **placeholder borroso** incrustado en el HTML, para que no haya saltos de
  maquetación mientras la imagen carga.
- Escribe un manifiesto con las dimensiones reales.

Y entonces `build.py` deja de emitir la ilustración de marcador de posición y emite un
`<picture>` completo con `srcset`, `sizes`, `loading="lazy"`, `decoding="async"` y
`fetchpriority="high"` en la imagen del hero. El navegador descarga solo el archivo que
necesita: un móvil recibe la versión de 480 px en AVIF, un escritorio la de 1600.

**Lo importante:** el sistema es gradual. Puedes subir una sola foto y esa sección pasa a
usar fotografía real mientras el resto sigue con ilustraciones; nunca aparecen imágenes rotas.

Slugs que el sitio ya tiene preparados:

```
portada, campus, patio, aula, biblioteca, laboratorio, arte, deporte, comunidad,
preescolar, primaria, secundaria, media, admisiones,
noticia-1 … noticia-4, equipo-1 … equipo-4
```

> **Antes de publicar fotos de menores de edad** necesitas la autorización escrita, previa y
> expresa de sus padres o acudientes. Es voluntaria, específica y revocable.

### MEJORA 6 — Versión en inglés

El sitio es bilingüe de verdad, no una traducción automática:

- **Contenido independiente** por idioma en `src/es/` y `src/en/`.
- **Selector de idioma** en la cabecera que lleva a la misma página en el otro idioma
  (no a la portada), con su versión a pantalla completa en el menú móvil.
- **`hreflang`** en cada página (`es`, `en`, `x-default`) y alternates en el `sitemap.xml`,
  para que Google indexe cada versión correctamente.
- **Textos de interfaz traducidos**: mensajes del buscador, de los formularios, del menú y
  del conmutador de tema, inyectados por idioma en `window.SITE_I18N`.
- **Buscador propio por idioma**, con su índice de 31 entradas.
- `lang` y `og:locale` correctos en cada documento.

Para añadir un tercer idioma, copia una entrada del diccionario `LANGS` en `tools/build.py`,
crea la carpeta `src/<código>/` y traduce los fragmentos.

---

## 5. Características técnicas

**Diseño**
- Sistema de diseño con variables CSS: verde `#2E6B3E`, teja `#C0492E`, sol `#F2B705`,
  cielo `#2F80A8` y naranja `#E8792B` sobre neutros cálidos.
- Tipografías Fraunces (títulos) + Plus Jakarta Sans (texto), con alternativas del sistema.
- Totalmente responsive, sin desbordamiento horizontal en ningún punto de ruptura.
- **Tema claro y oscuro** con detección automática y conmutador manual persistente.

**Interactividad** (`assets/js/main.js`, sin librerías)
- Menú móvil accesible con bloqueo de scroll y cierre con `Esc`.
- Animaciones de aparición con `IntersectionObserver` y contadores animados.
- Acordeones accesibles (`aria-expanded` / `aria-controls`).
- Galería con filtros por categoría y lightbox con navegación por teclado.
- Carrusel de testimonios con scroll-snap.
- Buscador interno (`Ctrl + K`), insensible a tildes.
- Validación de formularios con mensajes por campo y `aria-invalid`.
- Barra de progreso de lectura, botón «volver arriba» y botón flotante de WhatsApp.

**Accesibilidad**
- HTML semántico, enlace «saltar al contenido», roles y etiquetas ARIA.
- Foco visible en todos los elementos interactivos.
- Textos alternativos en imágenes y `<caption>` en las tablas.
- Respeta `prefers-reduced-motion`.

**SEO y rendimiento**
- Metadatos únicos por página e idioma, canonical, Open Graph y Twitter Card.
- Datos estructurados **Schema.org `School`**.
- `sitemap.xml` con alternates hreflang y `robots.txt`.
- Sin dependencias de JavaScript externas: solo se cargan las fuentes de Google.

**PWA**
- Instalable como aplicación con `manifest.webmanifest`.
- Service worker con estrategia *red primero* para HTML/CSS/JS (los cambios se ven de
  inmediato) y *caché primero* para imágenes. Funciona sin conexión, en ambos idiomas.

---

## 6. Qué reemplazar antes de publicar

Todo lo siguiente está marcado dentro del sitio con recuadros «Nota para el administrador»:

| Elemento | Dónde | Qué hacer |
|---|---|---|
| **Datos de la institución** | `tools/build.py` → `SITE` | Nombre, dominio, dirección, teléfonos, correos, NIT, DANE, coordenadas, redes |
| **Logotipo** | `assets/img/logo.svg` | Reemplazar por el logo real (SVG o PNG de al menos 512 px) |
| **Fotografías** | `assets/img/originals/` | Ver MEJORA 2 más arriba |
| **Misión, visión y principios** | `src/*/nosotros.html` | Poner los textos adoptados en el PEI |
| **Historia** | `src/*/nosotros.html` | Años e hitos reales |
| **Equipo directivo** | `src/*/nosotros.html` | Nombres, cargos y fotos reales |
| **Cifras** | `src/*/index.html` | Años, número de estudiantes y tamaño de grupo reales |
| **Resultados Saber 11** | `src/*/niveles.html` e `index.html` | Resultados oficiales del Icfes, con el año |
| **Costos educativos** | `src/*/admisiones.html` | Valores de la resolución de costos vigente |
| **Noticias** | `src/*/noticias.html` | Noticias reales |
| **Testimonios** | `src/*/index.html` | Testimonios reales, con autorización |
| **Coordenadas del mapa** | `src/*/contacto.html` y `SITE` | Latitud y longitud exactas |
| **Documentos PDF** | `assets/docs/` | PEI, manual de convivencia, SIEE, PRAE, resolución de costos |
| **Política de datos** | `src/*/contacto.html` | Política adoptada por el consejo directivo |
| **Endpoint de formularios** | `tools/build.py` → `SITE` | Ver MEJORA 1 más arriba |

Todas las cifras, noticias y testimonios que trae la plantilla son **ejemplos de estructura**,
señalados como tales en la propia página.

---

## 7. Publicación

El sitio es estático, así que se puede alojar gratis o casi gratis:

- **Netlify / Vercel / Cloudflare Pages**: arrastrar la carpeta o conectar un repositorio Git.
  Despliegue automático, HTTPS y dominio propio incluidos.
- **GitHub Pages**: subir el repositorio y activar Pages.
- **Hosting tradicional**: subir todos los archivos por FTP a `public_html`.

Antes de publicar, cambia `SITE["url"]` por el dominio real y vuelve a generar el sitio, para
que los `canonical`, el `sitemap.xml`, los `hreflang` y las etiquetas Open Graph apunten
correctamente.

---

## 8. Mejoras posibles a futuro

**Corto plazo** — video institucional en la portada, pagos en línea (PSE / Wompi / ePayco),
blog gestionado por el propio colegio con un CMS ligero, analítica (GA4 o Plausible),
ficha verificada de Google Business Profile.

**Mediano plazo** — portal privado para familias (notas, circulares, observador), integración
con la plataforma de gestión escolar, tour virtual 360° del campus, calendario sincronizado
con Google Calendar, boletín por correo, sección de egresados, bolsa de empleo.

**Largo plazo** — matrícula 100 % en línea con firma electrónica, aula virtual, app móvil,
chatbot de admisiones, panel público de indicadores institucionales, plataforma de donaciones.

---

Hecho con HTML, CSS y JavaScript estándar. Sin frameworks, sin rastreadores, sin dependencias
que caduquen. La única dependencia opcional es Pillow, y solo para optimizar fotografías.
