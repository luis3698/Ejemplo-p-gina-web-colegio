# Política de seguridad

## Alcance

Este proyecto es un sitio estático (HTML/CSS/JS sin backend propio); no
almacena datos ni credenciales. Los formularios de admisiones y contacto
envían los datos por `fetch()` al endpoint que cada institución configure —
ese backend externo queda fuera del alcance de este repositorio. Aun así, se
consideran reportes de seguridad válidos:

- vulnerabilidades de XSS o inyección de contenido en las páginas o en
  `assets/js/main.js`,
- problemas en el service worker (`sw.js`) que expongan o cacheen contenido
  indebidamente,
- cualquier forma de que el formulario o su "trampa antispam" puedan usarse
  para abusar del endpoint configurado por quien despliega el sitio.

## Cómo reportar una vulnerabilidad

**No abras un issue público.** Escribe directamente a
**luisgerardomancilla3698@gmail.com** con una descripción del problema, los
pasos para reproducirlo y su impacto potencial. Se confirmará la recepción en
un plazo razonable y se trabajará en una corrección antes de cualquier
divulgación pública.
