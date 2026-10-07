import textwrap
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.resume_parser import extract_text_from_pdf
from src.skill_extractor import extract_skills
from src.analyser import analyze_skills, calculate_text_similarity

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


st.set_page_config(
    page_title="CareerLens — Resume & Job Match",
    page_icon="🎯",
    layout="wide"
)

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = {}


def build_pdf_report(
    match_score,
    similarity_percentage,
    matched_skills,
    missing_skills,
    resume_skills,
    job_skills,
    readiness,
    strength,
    concern,
    readiness_detail,
    readiness_action,
    strength_detail,
    strength_action,
    concern_detail,
    concern_action,
):
    """Build a polished A4 CareerLens PDF report."""

    buffer = BytesIO()
    width, height = A4

    navy = colors.HexColor("#111827")
    indigo = colors.HexColor("#4F46E5")
    light_indigo = colors.HexColor("#EEF2FF")
    slate = colors.HexColor("#64748B")
    border = colors.HexColor("#E2E8F0")
    light = colors.HexColor("#F8FAFC")
    green_bg = colors.HexColor("#F0FDF4")
    orange_bg = colors.HexColor("#FFF7ED")

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title2", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=25, leading=30,
        textColor=navy, alignment=TA_LEFT, spaceAfter=6
    )
    subtitle = ParagraphStyle(
        "Subtitle2", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=16,
        textColor=slate
    )
    section = ParagraphStyle(
        "Section2", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=15, leading=19,
        textColor=navy, spaceBefore=13, spaceAfter=8
    )
    body = ParagraphStyle(
        "Body2", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=colors.HexColor("#475569")
    )
    small = ParagraphStyle(
        "Small2", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=slate
    )
    label = ParagraphStyle(
        "Label2", parent=styles["BodyText"],
        fontName="Helvetica-Bold", fontSize=8.2, leading=11,
        textColor=slate
    )
    value = ParagraphStyle(
        "Value2", parent=styles["BodyText"],
        fontName="Helvetica-Bold", fontSize=15, leading=19,
        textColor=navy
    )

    def header_footer(canvas, doc):
        canvas.saveState()

        canvas.setStrokeColor(border)
        canvas.setLineWidth(0.7)
        canvas.line(18 * mm, height - 17 * mm, width - 18 * mm, height - 17 * mm)

        canvas.setFont("Helvetica-Bold", 9.5)
        canvas.setFillColor(indigo)
        canvas.drawString(18 * mm, height - 13 * mm, "CAREERLENS")

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(slate)
        canvas.drawRightString(
            width - 18 * mm,
            height - 13 * mm,
            "Resume Intelligence Report"
        )

        canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)

        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(
            18 * mm, 9 * mm,
            "CareerLens • Resume Intelligence made simple."
        )
        canvas.drawRightString(
            width - 18 * mm, 9 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=21 * mm,
        title="CareerLens Resume Analysis Report",
        author="CareerLens"
    )

    story = [
        Spacer(1, 5 * mm),
        Paragraph("Your CareerLens Report", title),
        Paragraph(
            "A clear snapshot of how your resume aligns with the target role "
            "and where you can improve next.",
            subtitle
        ),
        Spacer(1, 7 * mm)
    ]

    score_table = Table(
        [
            [
                Paragraph("OVERALL RESUME MATCH", label),
                Paragraph("SKILLS MATCHED", label),
                Paragraph("NLP SIMILARITY", label)
            ],
            [
                Paragraph(f"{match_score:.0f}%", value),
                Paragraph(f"{len(matched_skills)} / {len(job_skills)}", value),
                Paragraph(f"{similarity_percentage:.0f}%", value)
            ],
            [
                Paragraph("Overall fit", small),
                Paragraph("Recognized job skills", small),
                Paragraph("Text-level similarity", small)
            ]
        ],
        colWidths=[55 * mm] * 3
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light),
        ("BOX", (0, 0), (-1, -1), .8, border),
        ("INNERGRID", (0, 0), (-1, -1), .5, border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [score_table, Spacer(1, 4 * mm)]

    story.append(Paragraph("Recruiter snapshot", section))

    snapshot = Table(
        [
            [
                Paragraph("APPLICATION READINESS", label),
                Paragraph("RESUME STRENGTH", label),
                Paragraph("MAIN CONCERN", label)
            ],
            [
                Paragraph(readiness, value),
                Paragraph(strength, value),
                Paragraph(concern, value)
            ]
        ],
        colWidths=[55 * mm] * 3
    )
    snapshot.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), .8, border),
        ("INNERGRID", (0, 0), (-1, -1), .5, border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [snapshot, Spacer(1, 2 * mm)]

    meaning = Table(
        [
            [
                Paragraph("<b>Application readiness</b>", body),
                Paragraph(readiness_detail, body)
            ],
            [
                Paragraph("<b>Resume strength</b>", body),
                Paragraph(strength_detail, body)
            ],
            [
                Paragraph("<b>Main concern</b>", body),
                Paragraph(concern_detail, body)
            ]
        ],
        colWidths=[42 * mm, 123 * mm]
    )
    meaning.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), light_indigo),
        ("BOX", (0, 0), (-1, -1), .7, border),
        ("INNERGRID", (0, 0), (-1, -1), .5, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [meaning]

    story.append(Paragraph("Skill match", section))

    matched = ", ".join(sorted(matched_skills)) if matched_skills else "None identified."
    missing = ", ".join(sorted(missing_skills)) if missing_skills else "None identified."

    skills = Table(
        [
            [Paragraph("MATCHED SKILLS", label), Paragraph("SKILLS TO STRENGTHEN", label)],
            [Paragraph(matched, body), Paragraph(missing, body)]
        ],
        colWidths=[82.5 * mm, 82.5 * mm]
    )
    skills.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), green_bg),
        ("BACKGROUND", (1, 0), (1, -1), orange_bg),
        ("BOX", (0, 0), (-1, -1), .7, border),
        ("INNERGRID", (0, 0), (-1, -1), .5, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [skills]

    story.append(Paragraph("Recommended next steps", section))

    for number, action in enumerate(
        [readiness_action, strength_action, concern_action], 1
    ):
        story.append(Paragraph(f"<b>{number}.</b> {action}", body))
        story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("Analysis coverage", section))

    coverage = Table(
        [
            [
                Paragraph("RESUME SKILLS DETECTED", label),
                Paragraph("JOB SKILLS DETECTED", label)
            ],
            [
                Paragraph(str(len(resume_skills)), value),
                Paragraph(str(len(job_skills)), value)
            ]
        ],
        colWidths=[82.5 * mm, 82.5 * mm]
    )
    coverage.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light),
        ("BOX", (0, 0), (-1, -1), .7, border),
        ("INNERGRID", (0, 0), (-1, -1), .5, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [coverage, Spacer(1, 6 * mm)]

    takeaway = Table(
        [[Paragraph(
            "<b>CareerLens takeaway</b><br/>"
            "Use this report as a roadmap, not a verdict. Focus on building "
            "genuine skills and relevant projects, then keep your resume "
            "targeted to the roles you want.",
            body
        )]],
        colWidths=[165 * mm]
    )
    takeaway.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_indigo),
        ("BOX", (0, 0), (-1, -1), .8, colors.HexColor("#C7D2FE")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(takeaway)

    doc.build(
        story,
        onFirstPage=header_footer,
        onLaterPages=header_footer
    )

    return buffer.getvalue()


# ==================================================
# CSS
# ==================================================

st.markdown(
    textwrap.dedent("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 5%, rgba(224,231,255,.65), transparent 28%),
            radial-gradient(circle at 90% 15%, rgba(219,234,254,.55), transparent 25%),
            #f8fafc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        background: linear-gradient(135deg,#eef2ff,#f8fafc 55%,#eff6ff);
        border: 1px solid #e0e7ff;
        border-radius: 24px;
        padding: 48px;
        margin-bottom: 36px;
        box-shadow: 0 12px 35px rgba(15,23,42,.06);
    }

    .hero-badge {
        display: inline-block;
        background: white;
        border: 1px solid #e0e7ff;
        color: #4f46e5;
        padding: 7px 13px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 17px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #111827;
        line-height: 1.15;
        max-width: 780px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #64748b;
        margin-top: 15px;
        max-width: 780px;
        line-height: 1.65;
    }

    .hero-note {
        margin-top: 20px;
        color: #475569;
        font-size: 13px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
        margin-top: 32px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 20px;
        line-height: 1.55;
    }

    .input-card,.score-card,.metric-card,.skill-card,.snapshot-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        box-shadow: 0 7px 22px rgba(15,23,42,.035);
    }

    .input-card {
        padding: 22px;
        min-height: 110px;
    }

    .input-title {
        font-size: 16px;
        font-weight: 750;
        color: #111827;
        margin-bottom: 5px;
    }

    .input-description {
        color: #64748b;
        font-size: 13px;
    }

    .score-card {
        padding: 25px;
        text-align: center;
        min-height: 174px;
    }

    .score-label,.metric-label,.snapshot-title {
        color: #64748b;
        font-size: 12px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: .5px;
    }

    .score-value {
        font-size: 53px;
        font-weight: 850;
        color: #111827;
        margin: 5px 0;
    }

    .score-message {
        color: #64748b;
        font-size: 13px;
        line-height: 1.5;
    }

    .metric-card {
        padding: 25px 18px;
        text-align: center;
        min-height: 174px;
    }

    .metric-value {
        font-size: 29px;
        font-weight: 800;
        color: #111827;
        margin-top: 16px;
    }

    .skill-card {
        padding: 24px;
        min-height: 150px;
    }

    .skill-card-title {
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 16px;
        color: #111827;
    }

    .skill-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .skill-pill {
        display: inline-flex;
        background: #f8fafc;
        color: #334155;
        border: 1px solid #e2e8f0;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 13px;
    }

    .snapshot-card {
        padding: 23px;
        min-height: 165px;
    }

    .snapshot-title {
        margin-bottom: 12px;
    }

    .snapshot-value {
        font-size: 24px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 10px;
    }

    .snapshot-description {
        font-size: 13px;
        color: #64748b;
        line-height: 1.55;
    }

    .snapshot-detail {
        background: linear-gradient(135deg,#fff,#eef2ff);
        border: 1px solid #e0e7ff;
        border-radius: 18px;
        padding: 28px;
        margin-top: 12px;
    }

    .snapshot-detail-title {
        font-size: 19px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 12px;
    }

    .snapshot-detail-text {
        color: #475569;
        font-size: 14px;
        line-height: 1.7;
    }

    .snapshot-detail-action {
        background: white;
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 17px;
        color: #3730a3;
        font-size: 14px;
        line-height: 1.6;
    }

    button[data-baseweb="tab"] {
        font-weight: 650;
        color: #64748b;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3730a3;
    }

    div.stButton > button {
        background: #374151;
        color: white;
        border: none;
        border-radius: 10px;
        min-height: 2.8rem;
        font-weight: 650;
    }

    div.stButton > button:hover {
        background: #1f2937;
        color: white;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        margin-top: 55px;
        padding-top: 25px;
        border-top: 1px solid #e5e7eb;
        font-size: 13px;
    }
    </style>
    """),
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("## 🎯 CareerLens")
    st.caption("Your resume. Your target role. One clearer next step.")
    st.divider()

    st.markdown("### How it works")
    st.markdown("""
    **01** — Upload your resume

    **02** — Add a job description

    **03** — Analyze your match

    **04** — Improve your gaps
    """)

    st.divider()

    st.markdown("### CareerLens gives you")
    st.markdown("""
    ✓ Resume match score

    ✓ Skill comparison

    ✓ NLP similarity

    ✓ Personalized recommendations

    ✓ Recruiter snapshot

    ✓ Downloadable PDF report
    """)

    st.divider()
    st.caption("CareerLens v1.0")


# ==================================================
# HERO
# ==================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-badge">🎯 Your career, one step clearer</div>'
    '<div class="hero-title">Turn your resume into a smarter job application.</div>'
    '<div class="hero-subtitle">'
    'See how well your resume fits a role, discover the skills you are '
    'missing, and get a clear idea of what to improve before you apply.'
    '</div>'
    '<div class="hero-note">'
    'Built to help you apply with more confidence — not just a higher score.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# INPUTS
# ==================================================

st.markdown(
    '<div class="section-title">Let’s get started</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Choose the role you want to apply for and let CareerLens compare it '
    'with your current resume.'
    '</div>',
    unsafe_allow_html=True
)

resume_col, jd_col = st.columns(2)

with resume_col:
    st.markdown(
        '<div class="input-card">'
        '<div class="input-title">📄 Your resume</div>'
        '<div class="input-description">Upload your latest resume as a PDF.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    uploaded_resume = st.file_uploader(
        "Upload your resume PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

with jd_col:
    st.markdown(
        '<div class="input-card">'
        '<div class="input-title">💼 Target job</div>'
        '<div class="input-description">Paste the job description for the role you want.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    job_description = st.text_area(
        "Paste the job description",
        height=180,
        placeholder="Paste the complete job description here...",
        label_visibility="collapsed"
    )

st.write("")

analyze_button = st.button(
    "✨ Analyze my resume",
    use_container_width=True
)


# ==================================================
# ANALYSIS
# ==================================================

if analyze_button:

    if uploaded_resume is None:
        st.warning("Please upload your resume to continue.")
        st.stop()

    if not job_description.strip():
        st.warning("Please paste a job description to continue.")
        st.stop()

    with st.spinner("Reading your resume and comparing it with the role..."):

        resume_text = extract_text_from_pdf(uploaded_resume)
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)

        matched_skills, missing_skills, match_score = analyze_skills(
            resume_skills,
            job_skills
        )

        similarity_percentage = (
            calculate_text_similarity(
                resume_text,
                job_description
            ) * 100
        )

    st.session_state.analysis_data = {
        "resume_text": resume_text,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "similarity_percentage": similarity_percentage
    }

    st.session_state.analysis_complete = True


# ==================================================
# RESULTS
# ==================================================

if st.session_state.analysis_complete:

    data = st.session_state.analysis_data

    resume_skills = data["resume_skills"]
    job_skills = data["job_skills"]
    matched_skills = data["matched_skills"]
    missing_skills = data["missing_skills"]
    match_score = data["match_score"]
    similarity_percentage = data["similarity_percentage"]

    st.markdown(
        '<div class="section-title">Your results</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Here is how closely your current resume matches this role.'
        '</div>',
        unsafe_allow_html=True
    )

    if match_score >= 80:
        match_message = "Strong match. Your resume covers most of the skills identified for this role."
    elif match_score >= 60:
        match_message = "Good match. You have a solid foundation, with a few areas to strengthen."
    elif match_score >= 40:
        match_message = "Moderate match. Strengthening the missing skills could improve your fit."
    else:
        match_message = "Several important skills are missing. Use the recommendations below as a guide."

    score_col, m1, m2, m3 = st.columns([1.5, 1, 1, 1])

    with score_col:
        st.markdown(
            '<div class="score-card">'
            '<div class="score-label">Overall resume match</div>'
            f'<div class="score-value">{match_score:.0f}%</div>'
            f'<div class="score-message">{match_message}</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.progress(match_score / 100)

    with m1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-label">SKILL MATCH</div>'
            f'<div class="metric-value">{match_score:.0f}%</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-label">SKILLS MATCHED</div>'
            f'<div class="metric-value">{len(matched_skills)} / {len(job_skills)}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-label">NLP SIMILARITY</div>'
            f'<div class="metric-value">{similarity_percentage:.0f}%</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # SKILLS
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">Your skill profile</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">'
        'See what already matches the role and what may need attention.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        html = (
            '<div class="skill-card">'
            '<div class="skill-card-title">✓ Matched skills</div>'
        )
        if matched_skills:
            html += '<div class="skill-pills">'
            for skill in sorted(matched_skills):
                html += f'<span class="skill-pill">✓ {skill}</span>'
            html += '</div>'
        else:
            html += '<div style="color:#64748b;">No matching skills identified yet.</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    with c2:
        html = (
            '<div class="skill-card">'
            '<div class="skill-card-title">↗ Skills to strengthen</div>'
        )
        if missing_skills:
            html += '<div class="skill-pills">'
            for skill in sorted(missing_skills):
                html += f'<span class="skill-pill">{skill}</span>'
            html += '</div>'
        else:
            html += '<div style="color:#64748b;">No missing skills identified.</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # --------------------------------------------------
    # NEXT STEP
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">What to improve next</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Start with a few high-priority improvements instead of trying to fix everything at once.'
        '</div>',
        unsafe_allow_html=True
    )

    if missing_skills:
        st.info(
            "🎯 Start with: " +
            ", ".join(sorted(missing_skills)[:5]) + "."
        )
    else:
        st.success("🎉 Your resume covers all identified job skills.")

    # --------------------------------------------------
    # SNAPSHOT LOGIC
    # --------------------------------------------------

    if match_score >= 80:
        readiness = "High"
        readiness_description = "Your resume is a strong fit for this role."
        readiness_detail = "Your resume already covers most of the skills identified for this position."
        readiness_action = "Make sure your strongest matching skills and relevant projects are clearly visible near the top of your resume."
    elif match_score >= 60:
        readiness = "Good"
        readiness_description = "Your resume is reasonably aligned with this role."
        readiness_detail = "You already have a useful foundation, but some role-specific requirements are missing."
        readiness_action = "Prioritize the missing skills that are most relevant to this particular position."
    elif match_score >= 40:
        readiness = "Moderate"
        readiness_description = "Your resume has some relevant skills, but noticeable gaps remain."
        readiness_detail = "The role requires several skills that are not currently visible in your resume."
        readiness_action = "Strengthen the most important missing skills and build relevant projects before adding them to your resume."
    else:
        readiness = "Low"
        readiness_description = "Your resume currently has several important skill gaps for this role."
        readiness_detail = f"Only {len(matched_skills)} of {len(job_skills)} recognized job skills currently match your resume."
        readiness_action = "Use the missing-skill list as a learning roadmap. Focus on the most relevant skills first."

    if len(resume_skills) >= 15:
        strength = "Broad skill set"
        strength_description = f"{len(resume_skills)} recognized skills were detected in your resume."
        strength_detail = "Your resume demonstrates a broad technical foundation."
        strength_action = "For a specific job, make the most relevant skills and projects more prominent instead of giving every skill equal importance."
    elif len(resume_skills) >= 8:
        strength = "Solid skill base"
        strength_description = f"{len(resume_skills)} recognized skills were detected in your resume."
        strength_detail = "Your resume has a reasonable technical foundation."
        strength_action = "Continue adding practical projects and role-specific skills as you develop them."
    else:
        strength = "Focused skill set"
        strength_description = f"{len(resume_skills)} recognized skills were detected in your resume."
        strength_detail = "Your resume currently presents a relatively focused set of technical skills."
        strength_action = "Build practical skills through projects, coursework, and hands-on practice relevant to your target roles."

    if len(missing_skills) == 0:
        concern = "No major skill gaps"
        concern_description = "All recognized job skills are covered."
        concern_detail = "CareerLens did not identify any missing skills from the current job description."
        concern_action = "Keep your resume targeted to the role and make sure your strongest matching experience is easy to find."
    elif len(missing_skills) <= 5:
        concern = "Small skill gap"
        concern_description = f"{len(missing_skills)} job skills are currently missing."
        concern_detail = "You are relatively close to the role's identified skill requirements."
        concern_action = "Focus on the missing skills shown above and strengthen them before applying."
    elif len(missing_skills) <= 10:
        concern = "Several skill gaps"
        concern_description = f"{len(missing_skills)} job skills are currently missing."
        concern_detail = "The role contains several requirements that are not currently detected in your resume."
        concern_action = "Choose the most important missing skills and create a focused learning plan around them."
    else:
        concern = "Large skill gap"
        concern_description = f"{len(missing_skills)} job skills are currently missing."
        concern_detail = "This role currently has a substantial difference between its requirements and the skills detected in your resume."
        concern_action = "Start with the highest-priority missing skills. Build genuine knowledge and practical experience first."

    # --------------------------------------------------
    # RECRUITER SNAPSHOT
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">Recruiter snapshot</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">A quick interpretation of your application readiness.</div>',
        unsafe_allow_html=True
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown(
            '<div class="snapshot-card">'
            '<div class="snapshot-title">Application readiness</div>'
            f'<div class="snapshot-value">{readiness}</div>'
            f'<div class="snapshot-description">{readiness_description}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with s2:
        st.markdown(
            '<div class="snapshot-card">'
            '<div class="snapshot-title">Resume strength</div>'
            f'<div class="snapshot-value">{strength}</div>'
            f'<div class="snapshot-description">{strength_description}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with s3:
        st.markdown(
            '<div class="snapshot-card">'
            '<div class="snapshot-title">Main concern</div>'
            f'<div class="snapshot-value">{concern}</div>'
            f'<div class="snapshot-description">{concern_description}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    t1, t2, t3 = st.tabs([
        "Application readiness",
        "Resume strength",
        "Main concern"
    ])

    with t1:
        st.markdown(
            '<div class="snapshot-detail">'
            '<div class="snapshot-detail-title">What this means</div>'
            f'<div class="snapshot-detail-text">{readiness_detail}</div>'
            '<div class="snapshot-detail-action">'
            '<strong>What you can do →</strong><br>'
            f'{readiness_action}'
            '</div></div>',
            unsafe_allow_html=True
        )

    with t2:
        st.markdown(
            '<div class="snapshot-detail">'
            '<div class="snapshot-detail-title">What this means</div>'
            f'<div class="snapshot-detail-text">{strength_detail}</div>'
            '<div class="snapshot-detail-action">'
            '<strong>What you can do →</strong><br>'
            f'{strength_action}'
            '</div></div>',
            unsafe_allow_html=True
        )

    with t3:
        st.markdown(
            '<div class="snapshot-detail">'
            '<div class="snapshot-detail-title">What this means</div>'
            f'<div class="snapshot-detail-text">{concern_detail}</div>'
            '<div class="snapshot-detail-action">'
            '<strong>What you can do →</strong><br>'
            f'{concern_action}'
            '</div></div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # COVERAGE CHART
    # --------------------------------------------------

    st.write("")
    st.write("")

    with st.expander("View skill coverage chart"):
        if job_skills:
            coverage_data = pd.DataFrame({
                "Skill Type": ["Matched", "Missing"],
                "Count": [len(matched_skills), len(missing_skills)]
            })

            fig = px.bar(
                coverage_data,
                x="Skill Type",
                y="Count",
                text="Count"
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=25, b=20),
                xaxis_title="",
                yaxis_title="Number of skills",
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No job skills were identified.")

    # --------------------------------------------------
    # PDF DOWNLOAD
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">Your report</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Save a polished PDF copy of your CareerLens analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    pdf_report = build_pdf_report(
        match_score,
        similarity_percentage,
        matched_skills,
        missing_skills,
        resume_skills,
        job_skills,
        readiness,
        strength,
        concern,
        readiness_detail,
        readiness_action,
        strength_detail,
        strength_action,
        concern_detail,
        concern_action
    )

    st.download_button(
        "⬇ Download polished PDF report",
        data=pdf_report,
        file_name="CareerLens_Analysis_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ==================================================
# FOOTER
# ==================================================

st.markdown(
    '<div class="footer">CareerLens • Resume Intelligence made simple.</div>',
    unsafe_allow_html=True
)
