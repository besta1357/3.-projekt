Elections Scraper – Volby do poslanecké sněmovny v rokku 2017

Tento Python projekt slouží ke stažení a zpracování volebních výsledků z webu https://www.volby.cz pro volby do Poslanecké sněmovny v roce 2017. Výsledky z vybraného okresu jsou zpracovány a uloženy do CSV souboru.

---

## Požadavky

Projekt vyžaduje Python 3.7+ a následující knihovny:

- `requests`
- `beautifulsoup4`

Doporučený způsob instalace je pomocí `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Jak spustit skript

Skript se spouští z příkazové řádky a očekává **2 argumenty**:

1. URL adresa okresu z webu volby.cz
2. Název výstupního `.csv` souboru

```bash
python vysledky.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=10&xnumnuts=6203" vysledky.csv
```

---

## Kontroly a validace

- První argument musí být platná URL začínající na `http://`, `https://` nebo `www.`
- Musí jít o odkaz na server `https://www.volby.cz/pls/ps2017nss/`
- Druhý argument musí končit příponou `.csv`
- Při chybě síťového spojení, neexistujícím odkazu nebo zápisu do souboru skript zobrazí odpovídající chybovou hlášku a ukončí se.

---

## Ukázka použití

```bash
python vysledky.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" Benesov_vysledky.csv
```

Výstup v konzoli:

```
Hotovo. Výsledky uloženy do: vysledky.csv
```

Ukázka obsahu `Benesov_vysledky.csv` (zkrácená):

| code   | location         | registered | envelopes | valid  | ODS      | Řád národa - Vlastenecká unie    | ... |
|--------|------------------|------------|-----------|--------|----------|----------------------------------|-----|
| 529303 | Benešov          | 13104      | 8485      | 8437   | 1052     | 10                               | ... |
| 532568 | Bernatice        | 191        | 148       | 148    | 4        | 0                                | ... |
| ...    | ...              | ...        | ...       | ...    | ...      | ...                              | ... |

---

## Struktura projektu

```
projekt/
├── main.py
├── requirements.txt
└── README.md
```


