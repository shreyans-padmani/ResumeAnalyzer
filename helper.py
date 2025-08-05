import google.generativeai as genai
import PyPDF2 as pdf
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
    
def get_gemini_response(prompt):
    try:
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e):
                print("Pro model quota exceeded — switching to flash...")
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
            else:
                raise

        if not response or not response.text:
            raise Exception("Empty response received from Gemini")

        try:
            response_json = json.loads(response.text)
            required_fields = ["JD Match", "MissingKeywords", "Profile Summary"]
            for field in required_fields:
                if field not in response_json:
                    raise ValueError(f"Missing required field: {field}")
            return response.text

        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if match:
                return match.group()
            else:
                raise Exception("Could not extract valid JSON response")

    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")
    
def truncate_text(text, max_chars=3000):
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


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

def prepare_prompt(resume_text,job_description):
    """
    Prepares the prompt for the Google Generative AI model.
    """
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description cannot be empty.")
    prompt_template = """
    Act as an expert ATS (Applicant Tracking System) specialist with deep expertise in:
    - Technical fields
    - Software engineering
    - Data science
    - Data analysis
    - Big data engineering
    
    Evaluate the following resume against the job description. Consider that the job market 
    is highly competitive. Provide detailed feedback for resume improvement.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide a response in the following JSON format ONLY:
    {{
        "JD Match": "percentage between 0-100",
        "MissingKeywords": ["keyword1", "keyword2", ...],
        "Profile Summary": "detailed analysis of the match and specific improvement suggestions"
    }}
    """
    return prompt_template.format(
        resume_text=resume_text.strip(),
        job_description=job_description.strip()
    )