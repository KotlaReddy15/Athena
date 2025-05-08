import streamlit as st
import requests

st.title("Job Description ")

# Input fields
job_title = st.text_input("Job Title")
custom_note = st.text_input("Custom Note")
key_focus = st.text_area("Key Skills (comma-separated)")


# Button
if st.button("Generate Job Description"):
    with st.spinner("Calling FastAPI backend..."):
        # Send POST request to FastAPI
        response = requests.post(
            "http://127.0.0.1:8000/generate-job-description",
            json={
                "job_title": job_title,
                "custom_note": custom_note,
                "key_focus": key_focus
            }
        )

        if response.status_code == 200:
            result = response.json()["job_description"]
            st.markdown("### ✍️ Generated Job Description")
            st.markdown(result)
        else:
            st.error("Failed to generate job description. Check FastAPI backend.")
