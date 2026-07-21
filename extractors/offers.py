"""
Scrapping des offres freework et lecture du fichier csv résultant.
"""

import os
import json

import requests
import pandas as pd

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from utils.compute_dataframe import load_csv_to_df
from transformers.get_region import get_region

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FREEWORK_OFFERS_PATH = f"{RESULT_PATH}/{os.getenv("FREEWORK_OFFERS_PATH")}"

BASE_URL = os.getenv("FREEWORK_BASE_URL")
OFFER_URL = os.getenv("FREEWORK_OFFER_URL")

def load_freework_offers():
    """
    Lecture des offres freework depuis le csv freework_offers.

    Returns:
        dataframe : Dataframe pandas - Offres freework du fichier csv
    """
    dataframe = load_csv_to_df(FREEWORK_OFFERS_PATH)
    return dataframe

def scrap_freework_pages_quantity(items_per_page):
    """
    Récupère le nombre de pages d'offres en fonction du nombre d'offres par page.

    Args:
        items_per_page : int - Nombre d'offres par pages

    Returns:
        int - Nombre de pages d'offres
    """
    url = f"{BASE_URL}&page=1&itemsPerPage={items_per_page}"
    response = requests.get(url,
                            headers=HEADERS,
                            timeout=10).text
    data = json.loads(response)
    return int(data["hydra:view"]["hydra:last"].split("=")[-1])

def scrap_freework_offers(items_per_page, page):
    """
    Réalise le scraping de toutes les offres freework d'une page.

    Args:
        items_per_page : int - Nombre d'offres par pages
        page : int - Numéro de page

    Returns:
        df : Dataframe pandas - Offres scrapées de la page
    """
    job_offers = []
    url = f"{BASE_URL}&page={page}&itemsPerPage={items_per_page}"
    response = requests.get(url,
                            headers=HEADERS,
                            timeout=10)
    while response.status_code != 200:
        response = requests.get(url,
                                headers=HEADERS,
                                timeout=10)
    data = json.loads(response.text)
    for element in data["hydra:member"]:
        skills_tags = []
        for skill in element["skills"]:
            skills_tags.append(skill["name"])
        profile = element["candidateProfile"] or ""
        profile = BeautifulSoup(profile, "html.parser").get_text(separator=" ", strip=True)
        dur_value = element["durationValue"] or None
        dur_period = element["durationPeriod"] or None
        month_duration = 0
        if isinstance(dur_value, int) and dur_value > 0 and dur_period in ["month", "year"]:
            if dur_period == "month":
                month_duration = dur_value
            elif dur_period == "year":
                month_duration = dur_value * 12
        url = f"{OFFER_URL}{element["job"]["nameForContributionSlug"]}/{element["slug"]}"

        job_offer = {
            "id": element["id"],
            "title": element["title"],
            "publication_date": element["publishedAt"],
            "skill_tags": skills_tags,
            "profile": profile,
            "experience": element["experienceLevel"] or "",
            "min_annual_salary": element["minAnnualSalary"] or None,
            "max_annual_salary": element["maxAnnualSalary"] or None,
            "min_daily_salary": element["maxDailySalary"] or None,
            "max_daily_salary": element["maxDailySalary"] or None,
            "month_duration": month_duration,
            "address": element["location"]["label"],
            "location": get_region(element["location"]["label"]),
            "url": url
        }

        job_offers.append(job_offer)
    df = pd.DataFrame(job_offers)
    df["skill_tags"] = df["skill_tags"].apply(lambda x: "|".join(x) if isinstance(x, list) else x)
    return df
