def analyze_skills(resume_skills, job_skills):
    """
    Compare resume skills with job-required skills.
    """

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched_skills = resume_set.intersection(job_set)
    missing_skills = job_set - resume_set

    if len(job_set) > 0:
        match_score = (len(matched_skills) / len(job_set)) * 100
    else:
        match_score = 0

    return matched_skills, missing_skills, match_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(resume_text, job_description):
    """
    Calculate similarity between resume and job description using TF-IDF.
    """

    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return similarity[0][0]