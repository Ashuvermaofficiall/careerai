import io
from PyPDF2 import PdfReader
import docx

def parse_resume(file):
    try:
        filename = file.filename
        file_stream = io.BytesIO(file.read())

        if filename.endswith('.pdf'):
            reader = PdfReader(file_stream)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text

        elif filename.endswith('.docx'):
            doc = docx.Document(file_stream)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text

        else:
            return None
    except Exception as e:
        return None
