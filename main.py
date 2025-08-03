import csv
import os
import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup as bs
from requests import get, RequestException, HTTPError, ConnectionError


def nacti_stranku(url):         # funkce načte stránku, získa odpověď a html jako text
    try:
        odpoved = get(url)
        odpoved.raise_for_status()  
        return bs(odpoved.text, features="html.parser")
    except HTTPError as e:
        print(f"HTTP chyba: {e}")
    except ConnectionError:
        print("Nelze se připojit k serveru - zkontrolujte připojení k internetu.")
    except RequestException as e:
        print(f"Obecná chyba při požadavku: {e}")
    except Exception as e:
        print(f"Neočekávaná chyba: {e}")
    
    return None
    
def udaje_okresu(url):          # funkce získa z odkazu okresu názvy a kody obcí
    html = nacti_stranku(url)   # a url odkazy na jednotlivé obce v danem okrese
    if not html:
        print("Chyba při načítání stránky.")
        return
    radky = html.find_all("tr")
    odkazy = []
                                # pomocí tagu tr, td a aributu href získame požadované údaje
    for radek in radky:
        cislo_td = radek.find("td", class_="cislo")
        nazev_td = radek.find("td", class_="overflow_name")
        
        if cislo_td and nazev_td:
            odkaz = cislo_td.a["href"]
            url_odkaz = urljoin(url, odkaz)
            kod_obce = cislo_td.get_text(strip=True)
            nazev_obce = nazev_td.get_text(strip=True)
            odkazy.append((nazev_obce, kod_obce, url_odkaz))
    return odkazy

def zpracovani_obci(nazev_obce, kod_obce, url):          # funkce zpracuje vysledky z jednotlivých obcí: 
    html = nacti_stranku(url)                            # počet voličů, počet obálek a počet platných hlasů
    if html is None:                                     # a přidá názvy stran a počet hlasů pro jednotlivé strany
        print(f"Chyba při načítání obce: {nazev_obce} ({kod_obce}) - stránka se nepodařila načíst.")
        return None                                     
        
    def vysledky_obce (id_tag):
        vysledek = html.find("td", {"headers": id_tag})
        return vysledek.get_text(strip=True).replace('\xa0', '')

    volici = vysledky_obce("sa2")
    obalky = vysledky_obce("sa3")
    platne = vysledky_obce("sa6")    

    strany = {}
    trs = html.find_all("tr")                            
    for tr in trs:
        tds = tr.find_all("td")                          
        if len(tds) >= 3:
            nazev_strany = tds[1].get_text(strip=True)
            hlasy = tds[2].get_text(strip=True).replace('\xa0', '')
            if nazev_strany and hlasy.isdigit():
               strany[nazev_strany] = hlasy

    return {
            "kod_obce": kod_obce,
            "obec": nazev_obce,
            "volici": volici,
            "obalky": obalky,
            "platne": platne,
            "strany": strany
        }

def vytvor_novy_nazev(soubor):
    zaklad, pripona = os.path.splitext(soubor)
    i = 1
    novy_nazev = f"{zaklad}({i}){pripona}"
    while os.path.exists(novy_nazev):
        i += 1
        novy_nazev = f"{zaklad}({i}){pripona}"
    return novy_nazev

def main():
    if len(sys.argv) != 3:
        print("Při spouštění, zadej: python vysledky.py <URL v uvozovkách> <vystupni_soubor.csv>")
        return
    
    vstupni_url = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    if os.path.exists(vystupni_soubor):
        novy_nazev = vytvor_novy_nazev(vystupni_soubor)  # pokud soubor již existuje, vytvoří nový název
        print(f"Soubor {vystupni_soubor} již existuje. Výstup bude uložen jako: {novy_nazev}")
        vystupni_soubor = novy_nazev

    if not vstupni_url.startswith(("http://", "https://", "www.")):         # ošetření špatně zadané adresy
        print("Chyba: první argument musí být URL začínající na http://, https:// nebo www.")
        print("Správné použití: python main.py <URL> <vystupni_soubor.csv>")
        return
    
    if not vstupni_url.startswith("https://www.volby.cz/pls/ps2017nss/"):   # ošetření, když by vstupní url odkazovala jinam než na volby z roku 2017
        print("Zadaná adresa je chybná")
        return
    if not vystupni_soubor.endswith(".csv"):                                # ošetření, že druhy argument musi být csv.soubor
        print("Chyba: druhý argument musí být výstupní soubor s příponou .csv")
        return

    odkazy = udaje_okresu(vstupni_url)
    if not odkazy:
        print("Nebyly nalezeny žádné odkazy na obce.")
        return 
    vysledky = []
    vsechny_strany = []

    for obec, cislo, link in odkazy:
        data = zpracovani_obci(obec, cislo, link)
        if data:
            vysledky.append(data)
            for strana in data["strany"].keys():
                if strana not in vsechny_strany:
                    vsechny_strany.append(strana)
                      
    try:
        with open(vystupni_soubor, mode= "w", newline= "", encoding= "utf-8") as f:         # zápis dat do csv souboru
            zapisovac = csv.writer(f)
            hlavicka = ["code", "location", "registered", "envelopes", "valid"] + vsechny_strany
            zapisovac.writerow(hlavicka)

            for obec in vysledky:
                radek = [
                    obec["kod_obce"],
                    obec["obec"],
                    obec["volici"],
                    obec["obalky"],
                    obec["platne"]
                ] + [obec["strany"].get(strana, "0") for strana in vsechny_strany]
                zapisovac.writerow(radek)
        print(f"Hotovo. Výsledky uloženy do: {vystupni_soubor}")
    except FileNotFoundError:
        print(f"Cesta k souboru neexistuje nebo je neplatná: {vystupni_soubor}")
    except PermissionError:
        print(f"Nemáš oprávnění zapisovat do souboru: {vystupni_soubor}")
    except OSError as e:
        print(f"Chyba systému při práci se souborem: {e}")
    except Exception as e:
        print(f"Neočekávaná chyba při zápisu do souboru: {e}")
    

if __name__ == "__main__":
    main()
