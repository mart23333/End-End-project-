
#import required libraries
import os
import pdfplumber
from docx import Document

# function to extract text from supported file types (TXT, PDF, DOCX)
def extract_text_from_file(file_path):
    """
    Extracts text from TXT, PDF, and DOCX files.
    Returns the extracted text as a string.
    """

    if not file_path:
        return ""

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError("Unsupported file type. Please upload a TXT, PDF, or DOCX file.")

# helper function to extract text from a TXT file
def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()

# helper function to extract text from a PDF file using pdfplumber
def extract_text_from_pdf(file_path):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text.strip()

# helper function to extract text from a DOCX file using python-docx
def extract_text_from_docx(file_path):
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text.strip())

    return "\n".join(paragraphs)