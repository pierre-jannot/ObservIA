import pandas as pd 
from collections import Counter

df = pd.read_csv("result/freework_offers.csv", sep=";")

def get_top_skills():
    try:
        # df = pd.read_csv("job_offers.csv")
        skills = df["skill_tags"].dropna().str.split(",").explode().str.strip()
        skill_counts = Counter(skills)
        top_skills = skill_counts.most_common(20)
        return [{"skill": skill, "count": count} for skill, count in top_skills]
    except FileNotFoundError:
        return {"error": "Fichier job_offers.csv non trouvé"}
    except KeyError:
        return {"error": "Colonne 'skill_tags' non trouvée dans le CSV"}
    
def get_seniority_stats():
        seniority = df["experience"].dropna()
        seniority_counts = seniority.value_counts()
        
        resultat = []
        for experience, count in seniority_counts.items():
            resultat.append({"experience":experience, "count": count})
        return resultat



