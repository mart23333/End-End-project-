from docx import Document

# function to read a DOCX file and extract its text content, returning the text as a single string with paragraphs separated by newlines
def read_docx(file_path):
    try:
        document = Document(file_path)
        paragraphs = []

        for paragraph in document.paragraphs:
            clean_text = paragraph.text.strip()

            if clean_text:
                paragraphs.append(clean_text)

        return "\n".join(paragraphs)

    except Exception as error:
        raise RuntimeError(f"Failed to read DOCX file: {error}")