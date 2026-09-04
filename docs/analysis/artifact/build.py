"""Buduje samodzielny plik Artifactu z szablonu, osadzając zrzuty jako data: URI.

Uruchomienie (z katalogu głównego repozytorium):
    python3 docs/analysis/artifact/build.py

Wynik: docs/analysis/artifact/rekomendacje-ux.html (nieśledzony przez git — ~800 KB).
Publikacja: narzędziem Artifact, na ten sam adres co poprzednio, żeby link z
docs/analysis/01_analiza_ux_konkurencji.md pozostał aktualny.
"""

import base64
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
MAX_WIDTH = 900
MAX_BYTES = 95 * 1024


def encode(slug: str) -> str:
    from PIL import Image

    src = ASSETS / f"{slug}.jpg"
    image = Image.open(src).convert("RGB")
    if image.width > MAX_WIDTH:
        image = image.resize((MAX_WIDTH, round(image.height * MAX_WIDTH / image.width)), Image.LANCZOS)
    tmp = HERE / f".{slug}.tmp.jpg"
    quality = 74
    while True:
        image.save(tmp, "JPEG", quality=quality, optimize=True)
        if tmp.stat().st_size <= MAX_BYTES or quality <= 40:
            break
        quality -= 8
    data = base64.b64encode(tmp.read_bytes()).decode()
    tmp.unlink()
    return data


def main() -> None:
    index = {r["slug"]: r for r in json.loads((ASSETS / "index.json").read_text(encoding="utf-8"))}
    template = (HERE / "rekomendacje-ux.template.html").read_text(encoding="utf-8")

    def replace(match: "re.Match[str]") -> str:
        slug = match.group(1)
        alt = index[slug]["opis"].replace('"', "&quot;")
        return f'<img src="data:image/jpeg;base64,{encode(slug)}" alt="{alt}" loading="lazy">'

    html = re.sub(r"\{\{IMG:([a-z0-9-]+)\}\}", replace, template)
    if "{{IMG" in html:
        raise SystemExit("nie podstawiono wszystkich obrazów")
    out = HERE / "rekomendacje-ux.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out} — {out.stat().st_size // 1024} KB")


main()
