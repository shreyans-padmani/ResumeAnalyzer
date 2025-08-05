import google.genrativeai as genai
import Pypdf2 as pdf
import json

def configure_google_api(api_key):
    """
    Configures the Google API with the provided API key.
    """
    try:
        genai.configure(api_key=api_key)
        # Load the API key from the environment variable
    except Exception as e :
        raise Exception("google.genrativeai module is not installed. Please install it using 'pip install google-genrativeai'.")
    
def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    try:
        render = pdf.PdfReader(pdf_path)
        if len(render.pages) == 0:
            raise ValueError("The PDF file is empty or has no pages.")
        
        text = []
        for page in render.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        if not text:
            raise ValueError("No text could be extracted from the PDF file.")
        
        return "\n".join(text)
    except Exception:
        raise Exception(f"The file {pdf_path} does not exist.")