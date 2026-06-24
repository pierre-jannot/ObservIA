import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

from transformers.get_department import get_department

HEADERS = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )}

BASE_URL = "https://www.free-work.com/api/job_postings?locationKeys=fr%7E%7E%7E"
OFFER_URL = "https://www.free-work.com/fr/tech-it/job-mission/"

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
            "address": address,
            "location": location,
            "url": url
        }

        job_offers.append(job_offer)
    df = pd.DataFrame(job_offers)
    df["skill_tags"] = df["skill_tags"].apply(lambda x: "|".join(x) if isinstance(x, list) else x)
    return df