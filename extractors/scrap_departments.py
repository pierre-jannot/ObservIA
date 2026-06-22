import requests
import pandas as pd

from bs4 import BeautifulSoup

def scrap_departments_information():

    url = "https://www.regions-departements-france.fr/"
    response = requests.get(
        url,
        headers={"User-Agent": "ScraperBot/1.0"},
        timeout=10
    )

    response.encoding = "utf-8"

    html = response.text  # str de 50 ko

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="tableDepartements")
    numbers = [
        tr.get_text() for tr in table.select("tr")
    ]

    department_list = []
    for value in numbers[1:]:
        department_list.append(value[1:-1].split('\n'))

    df = pd.DataFrame(department_list, columns=["identifiant_departement", "nom_departement", "region"])

    return df