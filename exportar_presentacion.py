"""
Exporta la presentación en dos formatos:
  · docs/ → web para GitHub Pages (index.html + imágenes WebP que se cargan al hacer scroll)
  · EDA_CambioClimaticoEuskalHerria_compartir.html → un único archivo con las imágenes
    incrustadas, para enviarlo sin la carpeta img/
Ejecutar con: python exportar_presentacion.py
"""
import base64
import io
import json
import re
import shutil
from pathlib import Path

from PIL import Image

ORIGEN    = Path("EDA_CambioClimaticoEuskalHerria.html")
DESTINO   = Path("EDA_CambioClimaticoEuskalHerria_compartir.html")
WEB       = Path("docs")
CIUDADES  = ["bilbo", "donostia", "gasteiz", "iruna", "baiona", "arrasate", "maule"]
ANCHO_MAX = 2000   # px — de sobra para pantallas retina al ancho de la presentación
CALIDAD   = 90     # WebP: texto nítido con mucho menos peso que el PNG original


def a_webp(ruta: str) -> bytes:
    """Convierte una imagen a WebP, limitando el ancho."""
    img = Image.open(ruta)
    if img.width > ANCHO_MAX:
        alto = round(img.height * ANCHO_MAX / img.width)
        img = img.resize((ANCHO_MAX, alto), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=CALIDAD, method=6)
    return buf.getvalue()


def ruta_webp(ruta: str) -> str:
    return Path(ruta).with_suffix(".webp").as_posix()


html = ORIGEN.read_text(encoding="utf-8")

# Rutas usadas: fondos CSS, <img> visibles al cargar y plantillas por ciudad del selector
rutas_css = set(re.findall(r"url\('(img/[^']+)'\)", html))
rutas_src = set(re.findall(r'src="(img/[^"]+)"', html))
rutas_tpl = set()
for tpl in re.findall(r'data-tpl="([^"]+)"', html):
    rutas_tpl |= {tpl.replace("{c}", c) for c in CIUDADES}

faltan = sorted(r for r in rutas_css | rutas_src | rutas_tpl if not Path(r).exists())
if faltan:
    raise SystemExit("❌ Faltan imágenes:\n  " + "\n  ".join(faltan))

webps = {r: a_webp(r) for r in sorted(rutas_css | rutas_src | rutas_tpl)}


# ── Web para GitHub Pages ─────────────────────────────────────────────────────
shutil.rmtree(WEB / "img", ignore_errors=True)
for r, datos in webps.items():
    destino = WEB / ruta_webp(r)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(datos)

web = re.sub(r"img/[^\"')]+\.(?:png|jpe?g)", lambda m: ruta_webp(m.group(0)), html)
web = web.replace("<img ", '<img loading="lazy" ')
(WEB / "index.html").write_text(web, encoding="utf-8")
(WEB / ".nojekyll").touch()   # servir los archivos tal cual, sin procesar con Jekyll

peso_web = sum(f.stat().st_size for f in WEB.rglob("*") if f.is_file())
print(f"✅ {WEB}/ — {len(webps)} imágenes, {peso_web / 1e6:.1f} MB en total")


# ── Archivo único para compartir ──────────────────────────────────────────────
uris = {r: "data:image/webp;base64," + base64.b64encode(d).decode() for r, d in webps.items()}

# Fondos CSS e <img> → data URI directamente en el HTML, para que se vean también
# en las vistas previas del móvil (WhatsApp, Mail, Archivos), que no ejecutan JS
unico = re.sub(r"url\('(img/[^']+)'\)", lambda m: f"url('{uris[m.group(1)]}')", html)
unico = re.sub(r'src="(img/[^"]+)"',
               lambda m: f'src="{uris[m.group(1)]}" data-ruta="{m.group(1)}"', unico)

# Resto de ciudades del selector → window.IMGS, que ruta() consulta al cambiar de ciudad.
# Las imágenes ya incrustadas en un <img> se registran desde el DOM para no duplicarlas.
imgs = {r: uris[r] for r in sorted(rutas_tpl - rutas_src)}
carga = (
    "<script>\n"
    f"  window.IMGS = {json.dumps(imgs)};\n"
    "  document.querySelectorAll('img[data-ruta]').forEach(img => {\n"
    "    window.IMGS[img.dataset.ruta] = img.src;\n"
    "  });\n"
    "</script>\n"
)
i = unico.rindex("<script>")
unico = unico[:i] + carga + unico[i:]

DESTINO.write_text(unico, encoding="utf-8")
print(f"✅ {DESTINO} — {len(uris)} imágenes, {DESTINO.stat().st_size / 1e6:.1f} MB")
