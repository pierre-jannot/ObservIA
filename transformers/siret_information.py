from extractors.siret_api import get_region_from_siret
from tqdm import tqdm
import time

def get_sirets_information(unique_sirets):
    print('\nAvancement récupération informations SIRET :\n')
    pbar = tqdm(total=len(unique_sirets))
    siret_info_list = []
    for siret in unique_sirets:
        siret_information = get_region_from_siret(siret)
        siret_info_list.append(siret_information)
        pbar.update(1)
        time.sleep(0.15) # Maximum 7 appels par seconde
    return siret_info_list