# -*- coding: utf-8 -*-
"""
Optimizador de fotografías del sitio (MEJORA 2 — fotografía profesional).

Toma las fotos originales de `assets/img/originals/` y genera, para cada una,
las versiones responsivas que el sitio necesita:

    assets/img/photos/<nombre>-480.avif   .webp   .jpg
    assets/img/photos/<nombre>-768.avif   .webp   .jpg
    assets/img/photos/<nombre>-1200.avif  .webp   .jpg
    assets/img/photos/<nombre>-1600.avif  .webp   .jpg
    assets/img/photos/manifest.json       (dimensiones + placeholder borroso)

En cuanto existe el manifest, `tools/build.py` deja de emitir la ilustración
de marcador de posición y empieza a emitir un `<picture>` completo con AVIF,
WebP y JPG, `srcset`, `sizes`, carga diferida y placeholder borroso (para que
no haya saltos de maquetación mientras la foto carga).

REQUISITO
---------
    pip install pillow

Para que se generen también los AVIF hace falta Pillow 9.2 o superior con
soporte AVIF; si no está disponible, el script sigue adelante y genera solo
WebP y JPG (el sitio funciona igual: el navegador escoge el mejor formato
disponible).

USO
---
    1. Copia las fotos originales (las de mayor resolución que tengas,
       preferiblemente 2400 px de ancho o más) en assets/img/originals/
    2. Nombra cada archivo con el "slug" que usa la página. Por ejemplo,
       para {{photo:campus|...}} el archivo debe llamarse campus.jpg
    3. python tools/optimize_images.py
    4. python tools/build.py

Slugs que el sitio ya tiene preparados:
    portada, campus, aula, laboratorio, biblioteca, arte, deporte,
    comunidad, primaria, preescolar, secundaria, media, admisiones,
    noticia-1, noticia-2, noticia-3, equipo-1, equipo-2, equipo-3, equipo-4
"""
import io
import json
import os
import sys
import base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "img", "originals")
OUT_DIR = os.path.join(ROOT, "assets", "img", "photos")

WIDTHS = [480, 768, 1200, 1600]
QUALITY = {"jpg": 82, "webp": 80, "avif": 55}
LQIP_WIDTH = 20          # ancho del placeholder borroso incrustado en el HTML
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")


def main():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("ERROR: falta la librería Pillow.\n"
              "Instálala con:  pip install pillow")
        return 1

    if not os.path.isdir(SRC_DIR):
        os.makedirs(SRC_DIR)
        print("Se creó la carpeta assets/img/originals/.")
        print("Copia allí tus fotografías y vuelve a ejecutar este script.")
        return 0

    originals = [f for f in sorted(os.listdir(SRC_DIR))
                 if f.lower().endswith(EXTENSIONS)]
    if not originals:
        print("No hay fotografías en assets/img/originals/.")
        print("Copia allí tus fotos (por ejemplo campus.jpg) y vuelve a ejecutar.")
        return 0

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    # Conserva lo ya generado por ejecuciones anteriores.
    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    try:
        manifest = json.load(io.open(manifest_path, encoding="utf-8"))
    except Exception:
        manifest = {}

    avif_ok = True
    print("Procesando %d fotografía(s)...\n" % len(originals))

    for filename in originals:
        slug = os.path.splitext(filename)[0].lower().replace(" ", "-")
        path = os.path.join(SRC_DIR, filename)

        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)      # respeta la orientación de la cámara
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            ow, oh = im.size
            ratio = oh / float(ow)

            widths = [w for w in WIDTHS if w <= ow] or [ow]
            generated = []

            for w in widths:
                h = int(round(w * ratio))
                resized = im.resize((w, h), Image.LANCZOS)

                resized.save(os.path.join(OUT_DIR, "%s-%d.jpg" % (slug, w)),
                             "JPEG", quality=QUALITY["jpg"], optimize=True, progressive=True)
                resized.save(os.path.join(OUT_DIR, "%s-%d.webp" % (slug, w)),
                             "WEBP", quality=QUALITY["webp"], method=6)
                if avif_ok:
                    try:
                        resized.save(os.path.join(OUT_DIR, "%s-%d.avif" % (slug, w)),
                                     "AVIF", quality=QUALITY["avif"])
                    except Exception:
                        avif_ok = False
                        print("  (aviso) Este Pillow no puede escribir AVIF; "
                              "se generan solo WebP y JPG.")
                generated.append(w)

            # Placeholder borroso incrustado (evita saltos de maquetación).
            lq = im.resize((LQIP_WIDTH, max(1, int(round(LQIP_WIDTH * ratio)))), Image.LANCZOS)
            buf = io.BytesIO()
            lq.save(buf, "JPEG", quality=40)
            lqip = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        manifest[slug] = {
            "widths": generated,
            "width": ow,
            "height": oh,
            "lqip": lqip,
            "avif": avif_ok,
        }
        print("  ok  %-22s %d x %d  ->  %s" % (slug, ow, oh,
              ", ".join(str(w) for w in generated)))

    with io.open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2))

    print("\nManifiesto escrito en assets/img/photos/manifest.json")
    print("Ahora ejecuta:  python tools/build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
