"""
Scraping et écriture des données des offres Freework.
"""

import os

from tqdm import tqdm
from dotenv import load_dotenv

from db.session import SessionLocal
from transformers.offers import prepare_freework_offer_for_db
from db.repositories.offers_repository import insert_offer
from extractors.offers import scrap_freework_pages_quantity, scrap_freework_offers
from utils.write_to_csv import write_dataframe

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FREEWORK_OFFERS_PATH = f"{RESULT_PATH}/{os.getenv("FREEWORK_OFFERS_PATH")}"

def compute_freework_offers(items_per_page=50):
    """
    Scraping et écriture des données des offres Freework.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    number_of_pages = scrap_freework_pages_quantity(items_per_page)
    print('\nRécupération des offres Freework\n')
    pbar = tqdm(total=number_of_pages)
    for page in range(1,number_of_pages + 1):
        scrapped_page = scrap_freework_offers(items_per_page, page)
        db = SessionLocal()
        try:
            df_db = prepare_freework_offer_for_db(scrapped_page)
            insert_offer(df_db, db)
        finally:
            db.close()
        pbar.update(1)
    print(f"Données {FREEWORK_OFFERS_PATH} écrites avec succès.")
    return
