import requests
import json
import pandas as pd
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from utils.compute_dataframe import load_csv_to_df
from transformers.get_department import get_department

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FREEWORK_OFFERS_PATH = f"{RESULT_PATH}/{os.getenv("FREEWORK_OFFERS_PATH")}"

BASE_URL = os.getenv("FREEWORK_BASE_URL")
OFFER_URL = os.getenv("FREEWORK_OFFER_URL")

def load_freework_offers():
    dataframe = load_csv_to_df(FREEWORK_OFFERS_PATH)
    return dataframe

def scrap_freework_pages_quantity(items_per_page):
    url = f"{BASE_URL}&page=1&itemsPerPage={items_per_page}"
    response = requests.get(url, headers=HEADERS).text
    data = json.loads(response)
    number_of_pages = int(data["hydra:view"]["hydra:last"].split("=")[-1])
    return number_of_pages

def scrap_freework_offers(items_per_page, page):
    job_offers = []
    url = f"{BASE_URL}&page={page}&itemsPerPage={items_per_page}"
    response = None
    while response is None:
        response = requests.get(url, headers=HEADERS).text
    data = json.loads(response)
    for element in data["hydra:member"]:
        skills_tags = []
        title = element["title"]
        publication_date = element["publishedAt"]
        for skill in element["skills"]:
            skills_tags.append(skill["name"])
        profile = element["candidateProfile"] or ""
        profile = BeautifulSoup(profile, "html.parser").get_text(separator=" ", strip=True)
        experience = element["experienceLevel"] or "NaN"
        min_annual_salary = element["minAnnualSalary"] or "NaN"
        max_annual_salary = element["maxAnnualSalary"] or "NaN"
        min_daily_salary = element["maxDailySalary"] or "NaN"
        max_daily_salary = element["maxDailySalary"] or "NaN"
        duration_value = element["durationValue"] or 0
        duration_period = element["durationPeriod"] or "NaN"
        if type(duration_value) == int and duration_value > 0 and duration_period in ["month", "year"]:
            if duration_period == "month":
                month_duration = duration_value
            elif duration_period == "year":
                month_duration = duration_value * 12
        else:
            month_duration = 0
        address = element["location"]["label"]
        location = get_department(address)
        slug = element["slug"]
        contribution_slug = element["job"]["nameForContributionSlug"]
        url = f"{OFFER_URL}{contribution_slug}/{slug}"

        job_offer = {
            "title": title,
            "publication_date": publication_date,
            "skill_tags": skills_tags,
            "profile": profile,
            "experience": experience,
            "min_annual_salary": min_annual_salary,
            "max_annual_salary": max_annual_salary,
            "min_daily_salary": min_daily_salary,
            "max_daily_salary": max_daily_salary,
            "month_duration": month_duration,
            "address": address,
            "location": location,
            "url": url
        }

        job_offers.append(job_offer)
    df = pd.DataFrame(job_offers)
    df["skill_tags"] = df["skill_tags"].apply(lambda x: "|".join(x) if isinstance(x, list) else x)
    return df