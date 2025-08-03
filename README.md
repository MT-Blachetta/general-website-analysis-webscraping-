# WebAnalyse-Crawler

WebAnalyse-Crawler ist ein leistungsstarkes und flexibles Web-Scraping-Tool, das in Python geschrieben wurde. Es dient der systematischen Analyse von Webseiten, der Extraktion von Textinhalten und der Durchführung computerlinguistischer Auswertungen.

## Funktionen

* **Breitensuche-Crawler**: Durchsucht eine Webseite und ihre verlinkten Unterseiten bis zu einer definierbaren Tiefe.
* **Text-Extraktion**: Extrahiert und bereinigt den Textinhalt von HTML-Seiten mit `BeautifulSoup`.
* **Link-Analyse**: Identifiziert und unterscheidet zwischen internen und externen Links.
* **Linguistische Analyse**: Nutzt `nltk` und `TextBlob` zur Analyse von Textdaten, wie z.B. Worthäufigkeiten und Phrasen-Extraktion.
* **Fehler- und Timeout-Management**: Robuste Fehlerbehandlung, um auch bei nicht erreichbaren Seiten eine stabile Ausführung zu gewährleisten.

## Voraussetzungen

Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist. Die folgenden Python-Bibliotheken werden benötigt:

* `urllib`
* `BeautifulSoup4`
* `nltk`
* `requests`
* `lxml`
* `textblob`

Sie können diese mit pip installieren:

```bash
pip install beautifulsoup4 nltk requests lxml textblob
```

## Wie man das Programm startet und anwendet (User Manual & How-to-Run)

Die primäre Funktionalität wird über die `webscrape.py`-Bibliothek bereitgestellt. Die Jupyter Notebooks im Repository demonstrieren die Anwendung des Tools.

### Beispiel 1: Analyse einer Nachrichtenseite (`ARDwebscrape.ipynb`)

Dieses Beispiel zeigt, wie man die Webseite `ard.de` analysiert.

1.  Öffnen Sie das Jupyter Notebook `ARDwebscrape.ipynb`.
2.  Die entscheidende Code-Zelle importiert die Bibliothek und startet die Suche:

    ```python
    import webscrape
    w = webscrape.breath_search('[http://www.ard.de](http://www.ard.de)',['ard.de'],3)
    ```

    -   `'http://www.ard.de'`: Die Start-URL für die Suche.
    -   `['ard.de']`: Eine Liste von Domains, die als "intern" betrachtet werden sollen.
    -   `3`: Die maximale Suchtiefe. Das bedeutet, der Crawler folgt Links bis zu 3 Ebenen tief von der Startseite aus.

3.  Führen Sie die Zellen im Notebook aus, um den Prozess zu starten. Die Ausgabe zeigt die geladenen URLs und die Anzahl der gefundenen Hyperlinks an.

### Beispiel 2: Analyse eines Wikipedia-Artikels (`webscrape wikipedia.ipynb`)

Dieses Notebook demonstriert, wie man einen einzelnen Wikipedia-Artikel über "Blog" analysiert und linguistisch auswertet.

1.  Öffnen Sie das Jupyter Notebook `webscrape wikipedia.ipynb`.
2.  Die ersten Zellen laden die Webseite und bereinigen den HTML-Code:

    ```python
    import urllib.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("[https://de.wikipedia.org/wiki/Blog](https://de.wikipedia.org/wiki/Blog)").read()
    soup = BeautifulSoup(html, "lxml")
    for b in soup.findAll(['script','link','style']): b.decompose()
    ```

3.  Weitere Zellen zeigen, wie man den Text extrahiert und mit `nltk` und `TextBlob` analysiert, um Sätze und Wortlisten zu erhalten.

### Eigene Analysen durchführen

Um Ihre eigene Analyse zu starten, können Sie ein neues Python-Skript oder Jupyter Notebook erstellen und die `webscrape`-Bibliothek importieren. Passen Sie den Aufruf von `breath_search` mit Ihrer gewünschten URL, der Basis-URL für interne Links und der Suchtiefe an.

```python
import webscrape

# Beispiel für die Analyse der Ruhr-Universität Bochum Webseite
analyse_ergebnis = webscrape.breath_search('[http://www.ruhr-uni-bochum.de](http://www.ruhr-uni-bochum.de)',['www.ruhr-uni-bochum.de'], 2)

# Ausgabe der Ergebnisse
print(f"Besuchte Seiten insgesamt: {len(analyse_ergebnis.visited)}")
print(f"Fehlerhafte Links: {len(analyse_ergebnis.errors)}")
```
