import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

genai.configure(api_key="AIzaSyArNjAreog5Ls4S-O2X9OZk7EYoHstqP1Q")  # Replace with your actual API key
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = FastAPI()

class JobInput(BaseModel):
    job_title: str
    custom_note: str
    key_focus: str

@app.post("/generate-job-description")
async def generate_job_description(data: JobInput):
    try:
        prompt = f"""
        Generate a detailed and professional job description for a **{data.job_title}** role. Follow this exact structure and include realistic and specific content:

        1. **About the Job** section: Include this note – "{data.custom_note}".
        2. **Required Skills** section: Include 10–12 highly specific technical and soft skills related to {data.key_focus}. Use bullet points and mention tools, technologies, or techniques where appropriate.
        3. Add a **Featured Benefits** section listing:
            - Medical insurance
            - Vision insurance
            - Dental insurance
            - 401(k)

        Use section headings: "About the job", "Required Skills", and "Featured benefits". Keep the tone professional, structured, and suitable for a U.S.-based tech company.
        """

        response = model.generate_content(prompt)
        return {"job_description": response.text}
    
    except Exception as e:
        print("❌ Gemini error:", str(e))
        traceback.print_exc()  # Log full error
        raise HTTPException(status_code=500, detail="Gemini API failed. See server logs.")
