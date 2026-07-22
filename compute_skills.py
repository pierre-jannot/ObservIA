import pandas as pd 
from collections import Counter 

skills_list = [
 # Langages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby",
    "Swift", "Kotlin", "Golang", "Rust", "Scala", "MATLAB", "Bash", "PowerShell",
    "Dart", "Perl", " Lua ", "Groovy", "COBOL", "Fortran", "Assembly", "Elixir",
    "Haskell", "Clojure", "Erlang", "ABAP", " R ",

    # Frameworks & Libraries
    "React", "Angular", " Vue ", "Node.js", "Django", "Flask", "FastAPI", "Spring",
    "Laravel", "Rails", "Express", "Next.js", "NestJS", "Flutter", "TensorFlow",
    "PyTorch", "Pandas", "NumPy", "Symfony", ".NET", "Spring Boot", "Hibernate",
    "Keras", "OpenCV", "Spark", "PySpark", "Svelte", "Remix", "Nuxt.js", "Fastify", " Gin ",
    "Echo", "Fiber", "Quarkus", "Micronaut", "Blazor", "Tailwind",

    # Bases de données
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle",
    "SQLite", "Cassandra", "MariaDB", "DynamoDB", "Neo4j", "InfluxDB", "Snowflake",
    "BigQuery",

    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
    "GitLab CI", "GitHub Actions", "Linux", "Nginx", "Apache", "Prometheus", "Grafana",
    "Helm", "Pulumi", "CloudFormation", "ArgoCD", "Vault", "Istio", " Consul ",
    "Linkerd", "Rancher", "OpenShift", "Proxmox", "Puppet", "Nagios",
    "AWS Glue", "FinOps", "Nutanix", "Citrix",

    # CI/CD & Qualité de code
    "CI/CD", "SonarQube", "SonarCloud", "TNR",

    # Cybersécurité
    "Splunk", "Wireshark", "Nmap", "Metasploit", "Burp Suite", "SIEM", "SOC",
    "Pentest", "OWASP", "ISO 27001", "CrowdStrike", "SentinelOne", "Qualys",
    "Tenable", "Carbon Black", "Snort", "Suricata",

    # Data & BI
    "Looker", "Qlik", "SAS", "SPSS", "Databricks", "MLflow", "Jupyter", "Streamlit",
    "Dash", "Power BI", "Tableau", "Hadoop", "Airflow", "dbt", "Great Expectations",
    "dvc", "Feast", "Tecton", "Prefect", "Luigi", "Talend", "Stambia",
    "Airbyte", "Microsoft Fabric", "Data Lake", "Data Warehouse", "Data Mesh",
    "Data Catalog", "ETL", "ELT", "Data Pipeline", "Master Data Management", "Dataiku", "ETL",

    # IA & Machine Learning
    "LangChain", "LlamaIndex", "Hugging Face", "OpenAI API", "Stable Diffusion",
    "NLTK", "spaCy", "Scikit-learn", "XGBoost", "LightGBM", "CatBoost",
    "Reinforcement Learning", "Computer Vision", "NLP", " RAG ", "Fine-tuning",
    " Prompt Engineering ", "Vector Database", "Pinecone", "Weaviate", "Ignio", "IA Agentique",

    # Réseau & Infra
    "Active Directory", "LDAP", "Cisco", "VMware", "Palo Alto", "Fortinet", "F5",
    "BGP", "OSPF", "VPN", "SDN", "SharePoint",

    # Hardware & FPGA
    "RTL Design",

    # Low-code / No-code
    "Power Automate", "Power Apps", "Zapier", "Make", "Bubble", "N8N", "WinDev",

    # Messaging & Communication
    "Slack API", "Twilio", "SendGrid", "Firebase",

    # Mobile
    "React Native", "Xamarin", "Ionic", "Cordova",

    # Testing
    "Jest", "Cypress", "Pytest", "JUnit", "Playwright", "Gatling", "k6",

    # Monitoring & Logs
    "Datadog", "New Relic", "Dynatrace", "ELK Stack", "Logstash", "Kibana",

    # Protocoles & Standards
    "OAuth", "JWT", "SAML", "SOAP", "gRPC", "WebSocket", "MQTT",

    # Gestion de projet
    "Confluence", " Notion ", "Trello", "Monday", "Asana",

    # Méthodologies
    "Kanban", " SAFe ", "DevOps", " ITIL ", "PRINCE2", "PMP",

    # CAO
    "AutoCAD", "SolidWorks", "CATIA", "Revit", "Rhino", "Fusion 360",

    # ERP & Métiers
    "Oracle EBS", "Microsoft Dynamics", "Odoo", "Sage", "OPCON",

    # Autres
    " Git ", "REST API", "GraphQL", "Kafka", "RabbitMQ", "Jira", "Agile", "Scrum",
    "PowerBI", "Selenium", "Postman", "Figma", "Salesforce", "SAP", "ServiceNow",
    "Workday", "HubSpot", "Astro", "Solid.js", "Qwik", "htmx", "Alpine.js"
]



df = pd.read_csv("result/freework_offers.csv",sep=";")

def get_skills_from_profile():
    skills_found = []
    for profile in df["profile"].dropna():
        profile_lower = profile.lower()
        for skill in skills_list:
            # if re.search(r'\b' + re.escape(skill) + r'/b' , profile, re.IGNORECASE):
            skill_lower = skill.lower()
            if skill_lower in profile_lower:
                skills_found.append(skill)


    skill_counts = Counter(skills_found)
    result = []
    for skill, count in skill_counts.most_common(50):
        result.append({"skill": skill, "count": count})
    return result

def compter_competences(profile):
    #  nb de compétences de skills_list trouvées dans un profil" 
    if pd.isna(profile):
        return 0 
    profile_lower = profile.lower()
    return sum(1 for skill in skills_list if skill.lower() in profile_lower)


def lire_tjm(row):
    #  TJM moyen d'une offre (moyenne minimum et maximum) ou None si absent.
    valeurs = [row["min_daily_salary"], row["max_daily_salary"]]
    valeurs = [v for v in valeurs if pd.notna(v)]
    if not valeurs:
        return None
    return sum(valeurs) / len(valeurs)
                              
def get_salary_by_skill_count():
    #  etape 1 : paires (nb de compétences, TJM ) pour chaque offre.
    rows = []
    for _, row in df.iterrows():
        nb_skills = compter_competences(row["profile"])
        tjm = lire_tjm(row)

        # on garde l'offre seulement si elle a des skills et un tjm 
        if nb_skills > 0 and tjm is not None:
            rows.append({"nb_skills": nb_skills, "tjm": tjm})

    return rows 

def get_salary_grouped_by_skill_count():
    #  etape 2 : TJM moyen par nombre de compétences (moyenne des TJM pour chaque nombre de compétences)
    rows = get_salary_by_skill_count()
    analyse_df = pd.DataFrame(rows)

    grouped = (
        analyse_df
        .groupby("nb_skills")["tjm"]
        .agg(
            tjm_moyen = "mean", 
            tjm_median = "median",
            nb_offres = "count",
        )
        .reset_index()
    )

    return grouped.round(0)

if __name__ == "__main__":
    grouped = get_salary_grouped_by_skill_count()
    print(get_salary_grouped_by_skill_count())


