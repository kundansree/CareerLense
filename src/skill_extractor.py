import json
import re
import os


# Find the project folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the skill database
SKILLS_FILE = os.path.join(BASE_DIR, "data", "skills.json")


# Load the skill database
with open(SKILLS_FILE, "r", encoding="utf-8") as file:
    SKILL_CATEGORIES = json.load(file)


def extract_skills(text):
    """
    Extract skills from resume or job description
    using the skill database.
    """

    found_skills = []

    text = text.lower()

    # Treat hyphens and underscores as spaces
    text = re.sub(r"[-_]", " ", text)

    for category, skills in SKILL_CATEGORIES.items():

        for skill in skills:

            skill_lower = skill.lower()

            # Treat hyphens and underscores as spaces
            skill_lower = re.sub(r"[-_]", " ", skill_lower)

            # Escape the skill first
            escaped_skill = re.escape(skill_lower)

            # Allow one or more spaces between words
            escaped_skill = escaped_skill.replace(r"\ ", r"\s+")

            pattern = (
                r"(?<![a-z0-9])"
                + escaped_skill
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, text):
                found_skills.append(skill)

    return found_skills


def categorize_skills(skills):
    """
    Organize detected skills into categories.
    """

    categorized = {}

    for category, category_skills in SKILL_CATEGORIES.items():

        matched = []

        for skill in skills:

            if skill in category_skills:
                matched.append(skill)

        if matched:
            categorized[category] = matched

    return categorized