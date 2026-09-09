# -*- coding: utf-8 -*-
"""
Genera las ilustraciones SVG de marcador de posición del sitio.

Son las imágenes que se ven mientras la institución no ha subido sus
fotografías reales. En cuanto existan fotos optimizadas (ver
tools/optimize_images.py), tools/build.py deja de usarlas automáticamente.

    python tools/make_placeholders.py
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
W, H = 1000, 750

C = ["#2F80A8", "#E8792B", "#F2B705", "#4E9B45", "#C0492E", "#7E5A3C"]


def person(x, y, s, c):
    return (
        f'<g stroke="{c}" stroke-width="{5.2*s:.1f}" stroke-linecap="round" fill="none">'
        f'<circle cx="{x}" cy="{y}" r="{7*s:.1f}" fill="{c}" stroke="none"/>'
        f'<path d="M{x} {y+7*s:.1f}V{y+22*s:.1f}"/>'
        f'<path d="M{x-9*s:.1f} {y+34*s:.1f}L{x} {y+22*s:.1f}l{9*s:.1f} {12*s:.1f}"/>'
        f'<path d="M{x-10*s:.1f} {y+13*s:.1f}h{20*s:.1f}"/></g>'
    )


def tree(x, y, s):
    return (
        f'<g><path d="M{x} {y}V{y-26*s:.1f}" stroke="#7E5A3C" stroke-width="{7*s:.1f}" stroke-linecap="round"/>'
        f'<circle cx="{x}" cy="{y-44*s:.1f}" r="{24*s:.1f}" fill="#4E9B45"/>'
        f'<circle cx="{x-16*s:.1f}" cy="{y-33*s:.1f}" r="{16*s:.1f}" fill="#3C8544"/>'
        f'<circle cx="{x+16*s:.1f}" cy="{y-33*s:.1f}" r="{16*s:.1f}" fill="#2E6B3E"/></g>'
    )


def building(x, y, w, h, floors=2, windows=4):
    """Edificio escolar sencillo, de tejado plano y ventanas regulares."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#FBF5E8" stroke="#3B2F26" stroke-width="3"/>',
           f'<rect x="{x-10}" y="{y-16}" width="{w+20}" height="{18}" rx="4" fill="#C0492E" stroke="#9B3A22" stroke-width="3"/>']
    fw = w / (windows + 1.0)
    fh = h / (floors + 0.8)
    for r in range(floors):
        for cix in range(windows):
            wx = x + fw * (cix + 0.5) + fw * 0.1
            wy = y + fh * (r + 0.35)
            out.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="{fw*0.62:.0f}" height="{fh*0.5:.0f}" rx="2" fill="#2F80A8" stroke="#3B2F26" stroke-width="2.2"/>')
    dw, dh = w * 0.16, h * 0.34
    out.append(f'<rect x="{x+w/2-dw/2:.0f}" y="{y+h-dh:.0f}" width="{dw:.0f}" height="{dh:.0f}" rx="3" fill="#F2B705" stroke="#3B2F26" stroke-width="2.5"/>')
    return "<g>" + "".join(out) + "</g>"


def header(a, b):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="img">'
        f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
        f'<linearGradient id="grd" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#8FBE7E"/><stop offset="1" stop-color="#5E9A4C"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    )


BACKDROP = (
    '<g fill="#FFFFFF" opacity=".7">'
    '<ellipse cx="190" cy="120" rx="70" ry="29"/><ellipse cx="243" cy="112" rx="46" ry="23"/>'
    '<ellipse cx="705" cy="92" rx="56" ry="23"/><ellipse cx="751" cy="86" rx="38" ry="19"/></g>'
    '<circle cx="855" cy="118" r="56" fill="#F2B705" opacity=".95"/>'
    '<path d="M0 470 150 400l130 50 140-70 150 80 160-40 270 60v230H0z" fill="#CFDCC6" opacity=".7"/>'
)


def ground(y=560):
    return f'<path d="M0 {y}q250 -44 500 -10t500 -16v{H-y+40}H0z" fill="url(#grd)"/>'


def scene(name, a, b, body, backdrop=True):
    svg = header(a, b) + (BACKDROP if backdrop else "") + ground() + body + "</svg>"
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("  ok  " + name)


def interior(wall="#F3EADA", floor="#D9C7A8"):
    """Fondo de interior para las escenas de aula, biblioteca y laboratorio."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="img">'
        f'<rect width="{W}" height="{H}" fill="{wall}"/>'
        f'<rect y="560" width="{W}" height="{H-560}" fill="{floor}"/>'
        f'<rect x="60" y="120" width="250" height="180" rx="6" fill="#CFE6F0" stroke="#3B2F26" stroke-width="4"/>'
        f'<path d="M185 120v180M60 210h250" stroke="#3B2F26" stroke-width="4"/>'
    )


def scene_interior(name, body):
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(interior() + body + "</svg>")
    print("  ok  " + name)


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    # 1. Campus / fachada
    scene("escena-campus.svg", "#CFE6F0", "#EDF3E6",
          building(330, 400, 360, 190, floors=2, windows=4)
          + tree(140, 640, 1.6) + tree(880, 650, 1.5)
          + person(250, 600, 1.1, C[0]) + person(760, 606, 1.05, C[3]))

    # 2. Patio / recreo
    scene("escena-patio.svg", "#D6E9F2", "#F0F4E6",
          '<path d="M120 700V520h150" stroke="#B0B7BD" stroke-width="10" fill="none" stroke-linecap="round"/>'
          '<circle cx="640" cy="678" r="24" fill="#FFFDF6" stroke="#3B2F26" stroke-width="4"/>'
          '<path d="M640 654l13 19-13 17-13-17z" fill="#3B2F26"/>'
          + person(300, 570, 1.25, C[1]) + person(400, 590, 1.15, C[0])
          + person(740, 580, 1.2, C[3]) + person(840, 598, 1.05, C[2])
          + tree(960, 660, 1.2))

    # 3. Comunidad / familias
    scene("escena-comunidad.svg", "#F3E7D3", "#F1F4E7",
          person(240, 545, 1.6, C[5]) + person(330, 556, 1.55, C[0])
          + person(412, 584, 1.05, C[2]) + person(472, 588, 1.0, C[1])
          + person(700, 550, 1.6, C[3]) + person(790, 582, 1.05, C[4])
          + tree(95, 625, 1.3) + tree(950, 638, 1.4))

    # 4. Deporte
    scene("escena-deporte.svg", "#D3E7F3", "#EEF4E5",
          '<path d="M700 700V470h180v230" stroke="#B0B7BD" stroke-width="11" fill="none"/>'
          '<path d="M700 470h180v70H700z" fill="#FFFFFF" opacity=".45"/>'
          '<circle cx="430" cy="640" r="30" fill="#E8792B" stroke="#B3591B" stroke-width="4"/>'
          '<path d="M400 640h60M430 610v60" stroke="#B3591B" stroke-width="3.4"/>'
          + person(300, 545, 1.3, C[0]) + person(560, 560, 1.25, C[4])
          + person(880, 585, 1.05, C[3]))

    # 5. Aula
    scene_interior("escena-aula.svg",
                   '<rect x="430" y="150" width="480" height="230" rx="8" fill="#2E6B3E" stroke="#1F4D2E" stroke-width="6"/>'
                   '<path d="M480 230h240M480 280h300M480 330h180" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round" opacity=".85"/>'
                   + "".join(
                       f'<g><rect x="{120+i*230}" y="590" width="180" height="20" rx="5" fill="#B98E55"/>'
                       f'<path d="M{140+i*230} 610v70M{280+i*230} 610v70" stroke="#8A6A45" stroke-width="9" stroke-linecap="round"/></g>'
                       for i in range(3))
                   + person(200, 500, 1.25, C[0]) + person(430, 500, 1.25, C[2]) + person(660, 500, 1.25, C[3]))

    # 6. Biblioteca
    scene_interior("escena-biblioteca.svg",
                   '<g><rect x="420" y="180" width="520" height="330" rx="8" fill="#C7A97E" stroke="#8A6A45" stroke-width="5"/>'
                   '<path d="M420 290h520M420 400h520" stroke="#8A6A45" stroke-width="5"/>'
                   + "".join(
                       f'<rect x="{440+i*32}" y="{205+row*110}" width="22" height="{70 if i%3 else 60}" rx="3" '
                       f'fill="{["#C0492E","#2F80A8","#F2B705","#4E9B45","#E8792B"][i%5]}"/>'
                       for row in range(3) for i in range(15))
                   + '</g>'
                   '<rect x="120" y="560" width="230" height="18" rx="5" fill="#B98E55"/>'
                   + person(190, 480, 1.3, C[4]) + person(290, 490, 1.15, C[3]))

    # 7. Laboratorio
    scene_interior("escena-laboratorio.svg",
                   '<rect x="380" y="540" width="540" height="22" rx="6" fill="#B0B7BD"/>'
                   '<g><path d="M470 540V450h-14v-30h50v30h-14v90z" fill="#CFE6F0" stroke="#3B2F26" stroke-width="4"/>'
                   '<path d="M456 505h50v35h-50z" fill="#4E9B45" opacity=".8"/></g>'
                   '<g><path d="M600 540l34-90h-48l34 90z" fill="#CFE6F0" stroke="#3B2F26" stroke-width="4"/>'
                   '<path d="M586 505h62l-24 35h-14z" fill="#C0492E" opacity=".75"/></g>'
                   '<circle cx="760" cy="500" r="36" fill="#CFE6F0" stroke="#3B2F26" stroke-width="4"/>'
                   '<path d="M736 512a36 36 0 0 0 48 0z" fill="#F2B705" opacity=".85"/>'
                   + person(200, 470, 1.35, C[0]) + person(320, 486, 1.2, C[2]))

    # 8. Arte y cultura
    scene("escena-arte.svg", "#F5E6CF", "#F7F2E4",
          '<g><path d="M300 700l60-160M470 700l-60-160M330 620h110" stroke="#8A6A45" stroke-width="10" stroke-linecap="round"/>'
          '<rect x="312" y="430" width="146" height="126" fill="#FFFDF6" stroke="#3B2F26" stroke-width="4"/>'
          '<circle cx="358" cy="482" r="24" fill="#F2B705"/>'
          '<path d="M328 540q42 -48 104 -10" stroke="#4E9B45" stroke-width="9" fill="none" stroke-linecap="round"/>'
          '<path d="M400 464l32 32" stroke="#C0492E" stroke-width="8" stroke-linecap="round"/></g>'
          '<g><path d="M640 692a70 52 0 1 0 140 0 70 52 0 1 0 -140 0" fill="#D8B98A" stroke="#8A6A45" stroke-width="4"/>'
          '<circle cx="672" cy="678" r="11" fill="#C0492E"/><circle cx="706" cy="668" r="11" fill="#2F80A8"/>'
          '<circle cx="742" cy="678" r="11" fill="#F2B705"/><circle cx="710" cy="704" r="11" fill="#4E9B45"/></g>'
          + person(540, 572, 1.2, C[1]) + person(600, 592, 1.0, C[3]) + tree(930, 636, 1.3))

    # Elimina las ilustraciones de la versión anterior del proyecto.
    for old in ("escena-huerta.svg", "escena-bosque.svg", "escena-taller.svg",
                "escena-campamento.svg"):
        p = os.path.join(OUT, old)
        if os.path.exists(p):
            os.remove(p)
            print("  -   eliminada " + old)


if __name__ == "__main__":
    print("Generando ilustraciones de marcador de posición...")
    main()
    print("Listo.")
