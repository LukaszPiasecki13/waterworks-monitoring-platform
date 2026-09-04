# Źródło Artifactu z rekomendacjami

Artifact „Dwanaście zmian we froncie” towarzyszy dokumentowi
[`../01_analiza_ux_konkurencji.md`](../01_analiza_ux_konkurencji.md).

| Plik | Co to |
|---|---|
| `rekomendacje-ux.template.html` | pełne źródło strony z placeholderami `{{IMG:slug}}` w miejscach zrzutów |
| `build.py` | podstawia zrzuty z `../assets/` jako `data:` URI i zapisuje gotowy plik |

Gotowego `rekomendacje-ux.html` (~800 KB, obrazy w base64) **nie trzymamy w repo** — powstaje
z szablonu i zrzutów, które już tu są. Slug w placeholderze odpowiada nazwie pliku w
[`../assets/index.json`](../assets/index.json).

Wymaga `Pillow`. Republikacja: narzędziem Artifact na ten sam adres, żeby link w dokumencie
pozostał aktualny.
