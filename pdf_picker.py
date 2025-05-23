from pdfminer.high_level import extract_text
import re
import spacy
from spacy.training.example import Example
from spacy.matcher import PhraseMatcher


MATCH_DATA = ["Python", "SQL", "R", "Scala", "Java", "Julia", "MATLAB", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly", "Power BI", "Tableau", "Looker",
              "Excel", "TensorFlow", "PyTorch", "scikit-learn", "Keras", "XGBoost", "LightGBM", "Hugging Face Transformers", "Reinforcement Learning", "spaCy", "NLTK",
              "Gensim", "BERT", "Sentiment Analysis", "Apache Spark", "Hadoop", "Dask", "Kafka", "Databricks", "AWS", "Azure", "BigQuery", "Google Cloud", "Snowflake",
              "PostgreSQL", "MongoDB", "Elasticsearch", "Apache Airflow", "dbt (Data Build Tool)", "ETL Processing", "Data Warehousing", "Apache NiFi", "Hypothesis Testing", 
              "Bayesian Statistics", "Probability Theory", "Linear Algebra", "Time Series Forecasting", "MySQL", "MSSQL", "Microsoft SQL Server", "Active listening", 
              "Verbal & written communication", "Public speaking", "Analytical thinking", "Decision-making", "Creativity", "Adaptability", "Attention to detail",
              "Collaboration", "Time management", "Self-motivation", "Predictive Modeling", "StreanLit", "Exploratory Data Analysis", "Data Analysis", "Logistic Regression"]

resume_path = 'LukeShawket_Resume.pdf'



def extract_resume(path):
    if path is not None:
        whole_text = extract_text(path)
        return whole_text
    return None


def parse_resume(text):
    nlp = spacy.load('en_core_web_sm')
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(skill) for skill in MATCH_DATA]
    matcher.add("TECH_SKILL", None, *patterns)

    doc = nlp(text)
    matches = matcher(doc)
    
    name = next((ent.text for ent in doc.ents if ent.label_ == 'PERSON'), None)
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    all_skills = [doc[start:end].text for _, start, end in matches]
    skills = set(all_skills)
    
    return {
        'name': name,
        'email': email.group(0) if email else None,
        'phone': phone.group(0) if phone else None,
        'skills': skills
    }

#print(parse_resume(extract_resume(resume_path)))

def parse_skills(text):
    nlp = spacy.load('en_core_web_sm')
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(skill) for skill in MATCH_DATA]
    matcher.add("TECH_SKILL", None, *patterns)

    doc = nlp(text)
    matches = matcher(doc)

    skills = [doc[start:end].text for _, start, end in matches]
    return set(skills)






