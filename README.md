# CareerLens — Intelligent Resume & Job Match Analyzer
🚀 **Live Demo:** https://careerlense.streamlit.app/

> Turn your resume into a smarter job application.

CareerLens is a Python-based resume analysis tool that helps job seekers understand how well their resume matches a target job description.

Upload a resume PDF, paste a job description, and CareerLens analyzes the application using skill matching and NLP-based text similarity. It highlights matched skills, identifies missing skills, provides improvement suggestions, and generates a polished PDF analysis report.

---

## 🚀 Why CareerLens?

Many applicants apply to jobs without knowing whether their resume actually matches the requirements of the role.

CareerLens provides a quick way to answer:

- How well does my resume match this job?
- Which required skills do I already have?
- Which skills am I missing?
- How strong is my application?
- What should I improve before applying?

---

## ✨ Features

### 📄 Resume PDF Analysis
Upload a resume in PDF format and automatically extract its text for analysis.

### 🎯 Job Match Score
Calculate an overall match score based on the skills found in the resume compared with the skills required by the job description.

### 🧠 NLP-Based Similarity
Use TF-IDF and cosine similarity to measure the textual similarity between the resume and job description.

### 🛠️ Skill Gap Analysis
Identify:

- ✅ Matched skills
- ❌ Missing skills
- 📊 Overall skill coverage

### 📊 Recruiter Snapshot
Get a quick view of:

- Application readiness
- Resume strength
- Main areas that need improvement

### 💡 Improvement Recommendations
CareerLens provides practical next steps based on the skills missing from the target job description.

### 📈 Skill Coverage Visualization
View the proportion of required skills that are already present in the resume.

### 📑 PDF Report
Generate a polished PDF report containing the analysis results, skill match, recommendations, and final takeaway.

---

## 🖥️ Application Workflow

```text
        Resume PDF
             │
             ▼
     Resume Text Extraction
             │
             ▼
       Skill Extraction
             │
             │
Job Description ───────► Skill Extraction
             │
             ▼
      ┌──────────────────┐
      │   CareerLens      │
      │     Analyzer      │
      └──────────────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
 Skill Matching   NLP Similarity
       │           │
       └─────┬─────┘
             ▼
       Match Analysis
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
  Matched  Missing  Recommendations
  Skills   Skills
             │
             ▼
       PDF Report