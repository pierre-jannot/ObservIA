from extractors.freework_api import scrap_freework_pages_quantity, scrap_freework_offers
from utils.write_to_csv import write_dataframe

from tqdm import tqdm
import os

FREEWORK_CSV_PATH = "result/freework_offers.csv"

def compute_freework_offers(items_per_page=50):
    if os.path.exists(FREEWORK_CSV_PATH):
        print(f"Données {FREEWORK_CSV_PATH} existantes. Réécriture des données ignorée.")
        return
    else:
        number_of_pages = scrap_freework_pages_quantity(items_per_page)
        print('\nRécupération des offres Freework\n')
        pbar = tqdm(total=number_of_pages)
        for page in range(1,number_of_pages + 1):
            scrapped_page = scrap_freework_offers(items_per_page, page)
            write_dataframe(path=FREEWORK_CSV_PATH, dataframe=scrapped_page, method="a")
            pbar.update(1)
        print(f"Données {FREEWORK_CSV_PATH} écrites avec succès.")
        return