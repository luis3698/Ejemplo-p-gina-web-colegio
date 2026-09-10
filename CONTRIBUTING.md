# Contribuir a esta plantilla

Gracias por tu interés. Este proyecto es una **plantilla de sitio web escolar**
de código abierto (ver [LICENSE](LICENSE)): cualquiera puede adaptarla,
mejorarla y reutilizarla, y las contribuciones son bienvenidas.

## Antes de empezar

Lee la sección "Estructura del proyecto" del [README](README.md): las páginas
HTML de la raíz y de `en/` son **generadas** por `tools/build.py` a partir del
contenido editable en `src/es/` y `src/en/`. No edites los `.html` generados
directamente — los cambios se perderían en la próxima compilación.

## Cómo contribuir

- **Reportar un error**: abre un [issue](../../issues/new/choose) describiendo
  qué esperabas, qué pasó, en qué página, y en qué navegador.
- **Proponer una mejora**: abre un issue explicando el caso de uso antes de
  ponerte a programar, sobre todo si es un cambio grande — así evitamos que
  trabajes en algo que termine sin encajar con el proyecto.
- **Enviar un cambio (pull request)**:
  1. Haz tus cambios en `src/es/` / `src/en/`, `assets/`, o `tools/` según
     corresponda — nunca en los `.html` generados.
  2. Corre `python tools/build.py` para regenerar las páginas y confirma que
     el sitio sigue viéndose bien en español e inglés (`python -m http.server
     5173`).
  3. Describe en el PR qué cambia y por qué, y cómo lo probaste.

## Código de conducta

Este proyecto sigue el [Código de conducta](CODE_OF_CONDUCT.md); se espera que
toda interacción en issues y pull requests lo respete.
