import pdfplumber

# function to read a PDF file and extract its text content, returning the text as a single string with pages separated by newlines
def read_pdf(file_path):
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()

                if extracted_text:
                    text += extracted_text + "\n"

    except Exception as error:
        raise RuntimeError(f"Failed to read PDF: {error}")

    return text.strip()