# scrapping
Project of webscraping for engeto.

Projekt slouží k scrapingu dat z webu [https://volby.cz].

## instalace

Vytvoř a aktivujte si vrituální prostředí, v kterém nainstalujete knihovny a spustíte projekt.

Virtuální prostředí se v terminálu spustí:
```bash
python -m venv venv
   source venv/bin/activate  
# Na Windows: .\venv\Scripts\activate
```

Nainstaluj potřebné knihovny v terminálu (potřebuješ soubor requirments.txt):
```bash
pip install -r requirements.txt
```

## spuštění skriptu
Spusť skript pomocí dvou argumentů:
```bash
python scraper.py <URL> <výstupní_soubor>
```
Například pokud chceš scrapovat výsledky z obce Benešov do souboru "vysledky_benesov.csv" tak zadáš toto:
```bash
python scraper.py https://volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xnumnuts=7103 vysledky_benesov.csv
```
Vždy zadávej stránku obce s vypsanými výsledky.

Při spouštění skriptu se ujistit, že si v aktivním virtuálním prostředí.

Ve výsledném CSV souboru bys tak měl mít formátované výsledky, každý řádek jako obec. Pokud to otevíráš v excelu, tak pozor na formátování UTF-8, zkontroluj, že je text ve wordpadu čitelný, pokud tomu tak v excelu není.