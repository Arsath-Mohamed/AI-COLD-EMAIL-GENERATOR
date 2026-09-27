import streamlit as st
import time
from scraper import ScraperError, scrape_website
from llm import LLMError, generate_cold_email
from st_copy_to_clipboard import st_copy_to_clipboard
from gmail import send_email

# Set the configuration for the Streamlit page
st.set_page_config(
    page_title="AI Cold Email Generator",
    page_icon="📧",
    layout="centered"
)

# Custom CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at top left, #1e1b4b, #0f172a, #000000);
        color: #e2e8f0;
    }

    /* Headers */
    h1, h2, h3 {
        color: #fff !important;
        background: -webkit-linear-gradient(45deg, #a855f7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }

    /* Glassmorphism for inputs and textareas */
    div[data-testid="stTextInput"] > div > div > input,
    div[data-testid="stTextArea"] > div > div > textarea,
    div[data-testid="stSelectbox"] > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    /* Focus state for inputs */
    div[data-testid="stTextInput"] > div > div > input:focus,
    div[data-testid="stTextArea"] > div > div > textarea:focus,
    div[data-testid="stSelectbox"] > div > div:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3) !important;
    }

    /* Primary Button Styling */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0.5rem 2.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
    }

    /* Button Hover */
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }
    
    /* Secondary Button Styling (Copy to Clipboard) */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: #8b5cf6 !important;
    }

    /* Adjust main padding */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }

</style>
""", unsafe_allow_html=True)
# Initialize session state for the generated email
if "generated_email" not in st.session_state:
    st.session_state.generated_email = None

# Main title and description
st.title("📧 AI Cold Email Generator for Internships")
st.markdown("Generate personalized cold emails to recruiters by scraping the company's website and using AI.")

# Create input fields for the user
st.header("1. Your Details")
user_details = st.text_area(
    "Enter your background, skills, and what you are looking for (e.g., 'I am a CS student at XYZ University, skilled in Python and React. Looking for a software engineering internship.')",
    height=100
)

st.header("2. Target Details")
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name (e.g., Google)")
with col2:
    job_role = st.text_input("Target Role (e.g., Software Engineer Intern)")

target_url = st.text_input("Company Website or Job Posting URL (used to scrape context)")

st.header("3. Email Preferences")
col_tone, col_length = st.columns(2)
with col_tone:
    tone = st.selectbox("Tone", ["Formal", "Friendly", "Aggressive"])
with col_length:
    length = st.selectbox("Length", ["Short", "Medium", "Long"])

# Create a button to trigger the generation process
if st.button("Generate Cold Email ", type="primary"):
    # Input validation: ensure all required fields are filled
    if not company_name or not job_role or not target_url or not user_details:
        st.error("Please fill in all the fields above.")
    else:
        # Show a loading spinner while processing
        with st.spinner("Scraping website and generating email..."):
            # Step 1: Scrape the website
            try:
                scraped_data = scrape_website(target_url)
                st.success("Successfully scraped company context!")
            except ScraperError as error:
                st.error(f"Scraping failed: {error}")
                st.session_state.generated_email = None
                st.stop()

            try:
                scraped_context = "\n".join(
                    part for part in [
                        f"Page title: {scraped_data.title}",
                        f"Page description: {scraped_data.description}",
                        f"Headings: {' | '.join(scraped_data.headings)}",
                        f"Page text: {scraped_data.text[:3000]}",
                    ] if part.split(": ", 1)[-1].strip()
                )
                email_content = generate_cold_email(
                    company_name=company_name,
                    job_role=job_role,
                    user_details=user_details,
                    scraped_content=scraped_context,
                    tone=tone,
                    length=length
                )
            except LLMError as error:
                st.error(f"Email generation failed: {error}")
                st.session_state.generated_email = None
            else:
                st.session_state.generated_email = email_content

# Display the email and send options if an email has been generated
if st.session_state.generated_email:
    st.header("4. Your Generated Email")
    
    # Display the email in a text area so the user can easily copy or edit it
    edited_email = st.text_area("Review and Edit:", value=st.session_state.generated_email, height=300)
    st_copy_to_clipboard(text=edited_email, before_copy_label=" Copy to Clipboard", after_copy_label="✅ Copied!")
    
    st.header("5. Send Direct via Gmail")
    st.markdown("Send the email directly using your Google Account.")
    
    recipient_email = st.text_input("Recipient Email Address")
    email_subject = st.text_input("Email Subject", value=f"Internship Application - {job_role}")
    
    if st.button("Send Email ", type="primary"):
        if not recipient_email or not email_subject:
            st.error("Please provide both a recipient email and a subject.")
        else:
            with st.spinner("Authenticating and sending email via Gmail API..."):
                success, msg = send_email(recipient_email, email_subject, edited_email)
                if success:
                    st.success(msg)
                    st.info("Email sent successfully! Resetting for your next email...")
                    time.sleep(3)
                    st.session_state.generated_email = None
                    st.rerun()
                else:
                    st.error(msg)
