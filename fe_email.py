import streamlit as st
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Page configuration
st.set_page_config(page_title="Candidate Review", layout="centered")

# Custom CSS styling
st.markdown("""
    <style>
    body {
        background-color: white;
        color: #000;
    }
    .stApp {
        font-family: 'Segoe UI', sans-serif;
        padding: 2rem;
    }
    .main {
        text-align: center;
    }
    .stButton>button {
        background-color: #6A5ACD;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #5a4abf;
    }
    .block-container {
        padding-top: 2rem;
    }
    .logo-title {
        font-size: 36px;
        font-weight: 800;
        margin-top: -10px;
        margin-bottom: 20px;
        color: #6A5ACD;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Logo and branding
st.image("logo.png", width=120)
st.markdown('<div class="logo-title">Athena.7t</div>', unsafe_allow_html=True)

# Page titles
st.title("Career Page")
st.subheader("Candidate Review Dashboard")

# Candidate info (mock data)
candidate = {
    "name": "Yash",
    "email": "guijula2001@gmail.com",
    "skills": ["Python", "Machine Learning", "Data Analysis"],
    "experience": "3 years at Amazon"
}

# Candidate display
st.markdown("### Candidate Info")
st.write(f"**Name:** {candidate['name']}")
st.write(f"**Email:** {candidate['email']}")
st.write(f"**Experience:** {candidate['experience']}")
st.write("**Skills:**")
for skill in candidate["skills"]:
    st.write(f"- {skill}")

# Verdict section
st.markdown("---")
verdict = st.radio("Select your verdict:", ["Yes", "No"], horizontal=True)

# Rejection reason
rejection_reason = None
if verdict == "No":
    rejection_reason = st.selectbox("Reason for rejection:", [
        "Need more experience",
        "Skills do not match",
        "Communication not clear",
        "Position already filled",
        "Not a culture fit"
    ])

# Email sending logic
def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        st.success("✅ Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Email failed: {e}")

# Email body generator and send
if st.button("Send Email"):
    subject = "Application Status – Athena.7t"

    if verdict == "Yes":
        body = f"""
Hi {candidate['name']},

Thank you for applying to Athena.7t. We were impressed with your profile and are excited to move forward.

Our team will reach out to you shortly to schedule a meeting.

Best regards,  
Athena.7t Hiring Team
"""
    else:
        body = f"""
Hi {candidate['name']},

Thank you for taking the time to apply to Athena.7t. After reviewing your profile, we’ve decided not to move forward with your application at this time.

Reason: {rejection_reason}

We encourage you to apply again in the future as our needs evolve.

Best regards,  
Athena.7t Hiring Team
"""
    send_email(candidate['email'], subject, body)
