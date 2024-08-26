"""
scraper.py: třetí projekt webscrapingu pro Engeto
author: Kamil Hnátek
email: kamil.hnatek@gmail.com
discord: irenicus87
"""
import requests
from bs4 import BeautifulSoup
import csv
import os
import argparse
import warnings

# Vypnutí varování o neověřených HTTPS požadavcích
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def parse_numeric_value(value):
    """
    Převede textovou hodnotu na celé číslo odstraněním všech typů mezer včetně nezlomitelných mezer.
    Pokud není hodnota platná, vrátí 0.
    """
    try:
        cleaned_value = value.replace("\u00a0", "").replace(" ", "")
        return int(cleaned_value)
    except ValueError:
        return 0

def fetch_detail_data(detail_url):
    """
    Získává detailní data pro daný odkaz, včetně okrsku, registrovaných, obálek, platných hlasů, hlaviček a dalších dat.
    """
    try:
        response = requests.get(detail_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Získání hodnoty okrsek z detailního URL
        okrsek_cell = soup.find('td', class_='cislo', headers='sa1 sb1')
        okrsek = parse_numeric_value(okrsek_cell.get_text(strip=True)) if okrsek_cell else 0

        # Získání registrovaných, obálek a platných hlasů
        registered_cell = soup.find('td', class_='cislo', headers='sa2')
        envelopes_cell = soup.find('td', class_='cislo', headers='sa3')
        valid_cell = soup.find('td', class_='cislo', headers='sa6')

        registered = parse_numeric_value(registered_cell.get_text(strip=True)) if registered_cell else 0
        envelopes = parse_numeric_value(envelopes_cell.get_text(strip=True)) if envelopes_cell else 0
        valid = parse_numeric_value(valid_cell.get_text(strip=True)) if valid_cell else 0

        # Získání hlaviček z detail_url
        headers_1 = [cell.get_text(strip=True) for cell in soup.find_all('td', class_='overflow_name', headers='t1sa1 t1sb2')]
        headers_2 = [cell.get_text(strip=True) for cell in soup.find_all('td', class_='overflow_name', headers='t2sa1 t2sb2')]

        # Získání dat
        additional_data_1 = [parse_numeric_value(cell.get_text(strip=True)) for cell in soup.find_all('td', class_='cislo', headers='t1sa2 t1sb3')]
        additional_data_2 = [parse_numeric_value(cell.get_text(strip=True)) for cell in soup.find_all('td', class_='cislo', headers='t2sa2 t2sb3')]
        additional_data = additional_data_1 + additional_data_2

        all_headers = headers_1 + headers_2
        return okrsek, registered, envelopes, valid, all_headers, additional_data

    except requests.RequestException as e:
        print(f"Error fetching detail data from URL: {e}")
        return 0, 0, 0, 0, [], []

def parse_row_data(row, headers_code, headers_location, writer, headers_written):
    """
    Zpracovává jeden řádek tabulky, získává kód, lokaci a detailní data.
    """
    code_cell = row.find('td', class_='cislo', headers=headers_code)
    location_cell = row.find('td', class_='overflow_name', headers=headers_location)
    link_cell = code_cell.find('a') if code_cell else None

    if code_cell and location_cell and link_cell:
        code = code_cell.get_text(strip=True)
        location = location_cell.get_text(strip=True)
        detail_url = 'https://volby.cz/pls/ps2017nss/' + link_cell['href']

        okrsek, registered, envelopes, valid, additional_headers, additional_data = fetch_detail_data(detail_url)

        if not headers_written[0]:
            writer.writerow(['code', 'location', 'okrsky', 'registered', 'envelopes', 'valid'] + additional_headers)
            headers_written[0] = True

        writer.writerow([code, location, okrsek, registered, envelopes, valid] + additional_data)

def process_table(soup, headers_code, headers_location, writer, headers_written):
    """
    Zpracovává tabulku pro zadané kombinace headers a zapisuje data do CSV.
    """
    rows = soup.find_all('tr')
    for row in rows:
        parse_row_data(row, headers_code, headers_location, writer, headers_written)

def scrape_election_data(url, output_file):
    """
    Hlavní funkce pro scraping dat z dané URL a jejich uložení do CSV.
    """
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        headers_written = [False]  # Seznam kvůli mutabilitě

        # Definice různých kombinací hlaviček pro každou tabulku
        header_combinations = [
            ('t1sa1 t1sb1', 't1sa1 t1sb2'),
            ('t2sa1 t2sb1', 't2sa1 t2sb2'),
            ('t3sa1 t3sb1', 't3sa1 t3sb2')
        ]

        # Iterace přes kombinace hlaviček
        for headers_code, headers_location in header_combinations:
            process_table(soup, headers_code, headers_location, writer, headers_written)

def main():
    """
    Hlavní funkce programu. Zpracuje vstupní argumenty a spustí scraping.
    """
    parser = argparse.ArgumentParser(description='Election data scraper')
    parser.add_argument('url', type=str, help='URL to scrape')
    parser.add_argument('output_file', type=str, help='Output CSV file name')
    args = parser.parse_args()

    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    scrape_election_data(args.url, args.output_file)

if __name__ == "__main__":
    main()
