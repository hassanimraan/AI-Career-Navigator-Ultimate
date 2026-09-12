from io import BytesIO

import fitz
from docx import Document


def extract_cv_text(data: bytes, filename: str) -> str:
    """
    Extract text from PDF or DOCX CV data.
    """

    name = filename.lower()

    if name.endswith(".pdf"):
        doc = fitz.open(
            stream=data,
            filetype="pdf",
        )

        try:
            text = "\n".join(
                page.get_text("text")
                for page in doc
            )
        finally:
            doc.close()

        return text.strip()

    if name.endswith(".docx"):
        doc = Document(
            BytesIO(data)
        )

        paragraphs = [
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    if name.endswith(".txt"):
        return data.decode(
            "utf-8",
            errors="ignore",
        ).strip()

    raise ValueError(
        "Only PDF, DOCX, and TXT files are supported."
    )


def extract_text_from_file(uploaded_file) -> str:
    """
    Streamlit-compatible wrapper.

    Accepts a Streamlit UploadedFile object.
    """

    if uploaded_file is None:
        return ""

    data = uploaded_file.getvalue()
    filename = uploaded_file.name

    return extract_cv_text(
        data,
        filename,
    )
