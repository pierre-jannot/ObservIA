import requests
import re
import pandas as pd

from bs4 import BeautifulSoup

def scrap_departments_information():

    url = "https://www.regions-departements-france.fr/numero-departement.html"
    response = requests.get(
        url,
        headers={"User-Agent": "ScraperBot/1.0"},
        timeout=10
    )

    response.encoding = "utf-8"

    html = response.text  # str de 50 ko

    soup = BeautifulSoup(html, "html.parser")
    titles = [
        a.get("title")
        for tr in soup.select("tbody tr")
        for th in tr.select("th")
        for a in th.select("a")
    ]

    department_dictionnary = {}

    for title in titles:
        number_match = re.search(r'(?<=\s)(\d+[A-Z]?)(?=\s)', title)
        department_match = re.search(r"(?<=\s|')([A-Z]\S*).", title)
        department_dictionnary[number_match.group(1).strip()] = department_match.group(1).strip()

    df = pd.DataFrame(
        list(department_dictionnary.items()),
        columns=["identifiant_departement", "nom_departement"])
    
    df = df.sort_values("identifiant_departement")

    return df