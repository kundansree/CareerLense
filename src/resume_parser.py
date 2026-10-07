import fitz


def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF resume.
    """

    text = ""

    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text