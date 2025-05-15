import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import tempfile
import re
import os
from dotenv import load_dotenv
from datetime import datetime
from supabase import create_client

# === Load environment variables ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# === Initialize Supabase ===
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Initialize Gemini model ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# === Page Setup (must be first Streamlit command) ===
st.set_page_config(page_title="Athena HR Toolkit", layout="wide")

# === Title ===
st.title("\U0001F680 Athena HR Toolkit")

# === Sidebar Navigation ===
st.sidebar.title("\U0001F9ED Navigation")
page = st.sidebar.radio("Choose a tool:", [
    "\U0001F3D7️ Job Description Generator",
    "\U0001F4CA Resume Scorer",
    "\U0001F4C5 Interview Scheduler",
    "\U0001F465 Candidate Manager"
])

# === Job Description Generator ===
if page == "🏗️ Job Description Generator":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📄 Job Description Generator (AI-Powered)</h2>", unsafe_allow_html=True)
    st.write("Fill in the fields below. Gemini will generate a complete, professional job description.")

    # Input fields
    job_title = st.text_input("Job Title", placeholder="e.g., Data Scientist")
    key_skills = st.text_area("Key Skills (comma-separated)", placeholder="e.g., Python, Machine Learning, Data Analysis")
    benefits = st.text_area("Benefits", placeholder="e.g., Remote work, Health insurance, Paid time off")
    custom_note = st.text_area("Additional Notes (Optional)", placeholder="Any extra instructions or notes for Gemini")

    # Button to generate JD
    if st.button("🤖 Generate JD with Gemini"):
        if job_title and key_skills and benefits:
            with st.spinner("Generating job description using Gemini..."):
                prompt = f"""
You are a skilled HR professional. Based on the information below, generate a professional, engaging, and well-structured Job Description including these sections:

1. **Job Title**
2. **About the Role**
3. **Responsibilities**
4. **Required Skills**
5. **Preferred Qualifications**
6. **Benefits**
7. **How to Apply**

### Job Title: {job_title}
### Key Skills: {key_skills}
### Benefits: {benefits}
### Additional Notes: {custom_note or "N/A"}

Make it clear, concise, and suitable for posting on job portals like LinkedIn or Indeed.
"""

                response = model.generate_content(prompt)
                jd_output = response.text.strip()

            st.success("✅ Job Description Generated!")
            st.markdown(jd_output)
        else:
            st.warning("⚠️ Please fill in all required fields (Job Title, Skills, and Benefits).")

# === Resume Scorer ===
elif page == "\U0001F4CA Resume Scorer":
    st.header("\U0001F4CA Resume Scorer")
    st.markdown("Upload a resume and job description to get an instant AI-powered evaluation.")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description", height=200)

    if uploaded_file and job_description:
        if st.button("\U0001F50D Analyze Resume"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            doc = fitz.open(tmp_path)
            resume_text = "\n".join(page.get_text() for page in doc)

            prompt = f"""
You are an intelligent Applicant Tracking System (ATS) and Resume Reviewer trained to assess how well a candidate’s resume matches a specific job description.

Return the results in the following format:

1. ATS Match Score: X/100  
2. Verdict: [Highly Suitable / Suitable / Partially Suitable / Not Suitable]  
3. Summary Feedback: <short summary>  

4. Detailed Feedback:

Skills Match (out of 30): <score>  
Experience Relevance (out of 20): <score>  
Keyword Match (out of 15): <score>  
Projects (out of 15): <score>  
Education (out of 10): <score>  
Formatting (out of 5): <score>  
Additional Value (out of 5): <score>

Resume: {resume_text}
Job Description: {job_description}
            """

            with st.spinner("Analyzing with Gemini..."):
                response = model.generate_content(prompt)
                feedback = response.text

            st.subheader("\U0001F4CB Feedback")
            st.markdown(feedback)

            def extract_score(label, out_of):
                match = re.search(rf"{label} \(out of {out_of}\):\\s*(\\d+)", feedback)
                return int(match.group(1)) if match else 0

            st.subheader("\U0001F4CA Score Breakdown")
            st.write({
                "Skills Match": extract_score("Skills Match", 30),
                "Experience": extract_score("Experience Relevance", 20),
                "Keyword Match": extract_score("Keyword Match", 15),
                "Projects": extract_score("Projects", 15),
                "Education": extract_score("Education", 10),
                "Formatting": extract_score("Formatting", 5),
                "Additional Value": extract_score("Additional Value", 5),
            })
    else:
        st.info("Upload a PDF resume and paste the job description to begin analysis.")

# === Interview Scheduler ===
elif page == "\U0001F4C5 Interview Scheduler":
    st.header("\U0001F4C5 Schedule an Interview")
    st.markdown("Select a candidate and schedule an interview with optional notes.")

    candidate_list = ["Alice Johnson", "Bob Smith", "Charlie Lee"]  # Replace with Supabase query if needed
    candidate = st.selectbox("Select Candidate", candidate_list)
    interview_date = st.date_input("Interview Date")
    interview_time = st.time_input("Interview Time")
    interviewer = st.text_input("Interviewer Name")
    notes = st.text_area("Notes (optional)")

    if st.button("\U0001F4C5 Schedule Interview"):
        if candidate and interview_date and interview_time and interviewer:
            scheduled_at = datetime.combine(interview_date, interview_time)
            st.success(f"\u2705 Interview scheduled for **{candidate}** with **{interviewer}** on **{scheduled_at.strftime('%Y-%m-%d %H:%M')}**.")
            if notes:
                st.info(f"\U0001F4AC Notes: {notes}")
        else:
            st.warning("Please fill out all required fields.")

# === Candidate Manager ===
elif page == "\U0001F465 Candidate Manager":
    st.header("\U0001F465 Candidate Manager")
    st.markdown("Coming soon: Manage applicants, send emails, track interviews.")
    st.info("This feature is under development. Stay tuned!")