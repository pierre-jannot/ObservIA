import pandas as pd 
from collections import Counter

# On charge le fichier
df = pd.read_csv("job_offers.csv")

# On commence le traitement datas 
def get_top_skills():
    skills = df["skill_tags"].dropna().str.split(",").explode().str.strip()
    skill_counts = Counter(skills)
    top_skills = skill_counts.most_common(20)
    return [{"skill": skill, "count": count} for skill, count in top_skills]

