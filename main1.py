import streamlit as st
import base64
import fitz  # PyMuPDF
import re
import os
from datetime import datetime
from supabase import create_client
import google.generativeai as genai
from streamlit_calendar import calendar

# --- Configure API Keys ---
genai.configure(api_key="AIzaSyDjsZpxdPc0Hf2QCbUyjTsKOEZy3LqAhD8")
SUPABASE_URL = "https://zlbsvvuulawbmubgnyyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpsYnN2dnV1bGF3Ym11YmdueXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU4NzM0NDUsImV4cCI6MjA2MTQ0OTQ0NX0.YWzoQn7fc4vrDU7Wn5tAsL4aUzuAM0uT9aakxJZuL58"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Streamlit Config ---
st.set_page_config(page_title="Athena HR Toolkit", layout="wide")
st.title("🚀 Athena HR Toolkit")

# --- Sidebar Navigation ---
st.sidebar.title("🗭 Navigation")
page = st.sidebar.radio("Choose a tool:", [
    "🏗️ Job Description Generator",
    "📊 Resume Scorer",
    "🗓️ Interview Scheduler",
    "👥 Candidate Manager"
])

# --- Job Description Generator ---
if page == "🏗️ Job Description Generator":
    import streamlit as st

# --- Page config ---
st.set_page_config(page_title="JD Generator", layout="centered")

# --- Header ---
st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📄 Job Description Generator</h2>", unsafe_allow_html=True)
st.write("Fill in the fields below to automatically generate a professional job description.")

# --- Input fields ---
job_title = st.text_input("Job Title")
key_skills = st.text_area("Key Skills (comma-separated)", placeholder="e.g., Python, Data Analysis, Machine Learning")
benefits = st.text_area("Benefits", placeholder="e.g., Health insurance, Remote work, Flexible hours")
custom_note = st.text_input("Additional Notes (Optional)")

# --- Generate button ---
if st.button("🚀 Generate JD"):
    if job_title and key_skills and benefits:
        jd = f"""
### {job_title}

We are looking for a passionate and skilled **{job_title}** to join our team.

**Key Skills:**
- {', '.join([skill.strip() for skill in key_skills.split(',')])}

**Benefits:**
- {benefits.replace(',', '\n- ')}

**Additional Notes:**
{custom_note or 'N/A'}
        """
        st.success("✅ Job Description Generated!")
        st.markdown(jd)
    else:
        st.warning("⚠️ Please fill in all required fields (Job Title, Key Skills, and Benefits).")

# --- Resume Scorer ---
elif page == "📊 Resume Scorer":
    st.header("📊 Resume Scorer")
    uploaded_file = st.file_uploader("Upload a resume (PDF only)", type=["pdf"])

    if uploaded_file and st.button("Analyze Resume"):
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        doc = fitz.open("temp_resume.pdf")
        resume_text = "\n".join(page.get_text() for page in doc)

        job_id = st.text_input("Enter Job ID to compare")
        if not job_id:
            st.warning("Please provide a job ID")
        else:
            job_result = supabase.table("job_description") \
                .select("description") \
                .eq("job_id", job_id) \
                .single() \
                .execute()

            if not job_result.data:
                st.error("❌ Job description not found.")
            else:
                job_description = job_result.data["description"]

                prompt = f"""
You are an intelligent Applicant Tracking System (ATS) and Resume Reviewer trained to assess how well a candidate’s resume matches a specific job description.
Return results with ATS Match Score, Verdict, Summary, and detailed scores.

Resume: {resume_text}
Job Description: {job_description}
"""
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(prompt)
                feedback = response.text

                st.markdown("#### 📝 Feedback")
                st.text_area("Gemini Output", feedback, height=400)

                def extract_score(label, out_of):
                    match = re.search(rf"{label}.*\(out of {out_of}\):\s*(\d+)", feedback)
                    return float(match.group(1)) if match else 0

                scores = {
                    "skills_match_score": extract_score("Skills Match", 30),
                    "experience_score": extract_score("Experience Relevance", 20),
                    "keyword_score": extract_score("Keyword", 15),
                    "projects_score": extract_score("Projects", 15),
                    "education_score": extract_score("Education", 10),
                    "formatting_score": extract_score("Formatting", 5),
                    "additional_value_score": extract_score("Additional Value", 5),
                }

                summary_match = re.search(r"Summary Feedback:\s*(.*)", feedback)
                summary = summary_match.group(1).strip() if summary_match else "No summary available"

                supabase.table("resume_scores").insert({
                    "applicant_id": job_id,  # Temporary mapping
                    "summary_feedback": summary,
                    "detailed_feedback": feedback,
                    "evaluation_date": datetime.utcnow().isoformat(),
                    **scores
                }).execute()

                st.success("✅ Score saved to Supabase")

# --- Interview Scheduler ---
elif page == "🗓️ Interview Scheduler":
    st.header("🗓️ Interview Scheduler")

    interview_date = st.date_input("Select Date")
    interview_time = st.time_input("Select Time")
    candidate_email = st.text_input("Candidate Email")
    job_id = st.text_input("Job ID")

    if st.button("Schedule Interview"):
        if candidate_email and job_id:
            timestamp = datetime.combine(interview_date, interview_time)
            supabase.table("interviews").insert({
                "candidate_email": candidate_email,
                "interview_datetime": timestamp.isoformat(),
                "job_id": job_id
            }).execute()
            st.success("✅ Interview scheduled and saved to Supabase!")
        else:
            st.warning("Please fill in all required fields")

    st.markdown("### 📅 Calendar View")
    events = supabase.table("interviews").select("interview_datetime, candidate_email").execute()
    calendar_events = [
        {
            "title": row["candidate_email"],
            "start": row["interview_datetime"],
            "end": row["interview_datetime"]
        } for row in events.data
    ]
    calendar(options={"initialView": "dayGridMonth"}, events=calendar_events, key="calendar")

# --- Candidate Manager ---
elif page == "👥 Candidate Manager":
    st.header("👥 Candidate Manager")
    st.markdown("Coming soon: Manage applicants, send emails, track interviews.")
