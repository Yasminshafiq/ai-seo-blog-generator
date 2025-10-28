import streamlit as st
import google.generativeai as genai
import base64
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --------------------------------------------------------
# 🔹 STEP 1: CONFIG
# --------------------------------------------------------
GEMINI_API_KEY = "AIzaSyAf1X-nWg83HHAdxsqa29A0R2zPtC8wBQ0"
LINKEDIN_ACCESS_TOKEN = "YOUR_LINKEDIN_ACCESS_TOKEN"
MAIL_SENDER = "yasminshafiq01@gmail.com"
MAIL_APP_PASSWORD = "YOUR_APP_PASSWORD"
NEWSLETTER_RECIPIENTS = ["subscriber1@gmail.com", "subscriber2@gmail.com"]

genai.configure(api_key=GEMINI_API_KEY)

# Models
text_model = genai.GenerativeModel("models/gemini-2.5-flash")
image_model = genai.GenerativeModel("models/gemini-2.5-flash")

# --------------------------------------------------------
# 🔹 STEP 2: Generate SEO Blog
# --------------------------------------------------------
def generate_blog(keyword, tone, length):
    prompt = f"""
    Write an SEO-optimized blog about "{keyword}".
    Tone: {tone}.
    Length: {length}.
    Include:
    - A catchy title
    - Meta description (under 160 characters)
    - 3–4 engaging subheadings
    - Natural keyword flow
    - A conclusion with call-to-action
    Also list 5 related SEO keywords and tags.
    """
    response = text_model.generate_content(prompt)
    return response.text

# --------------------------------------------------------
# 🔹 STEP 3: Generate Blog Image
# --------------------------------------------------------
def generate_blog_image(keyword):
    image_prompt = f"Create a clean, modern blog banner image about '{keyword}'. High quality, soft light, realistic, no text."
    result = image_model.generate_content(image_prompt)

    if hasattr(result, "candidates") and result.candidates:
        img_data = result.candidates[0].content.parts[0].inline_data.data
        img_bytes = base64.b64decode(img_data)
        return img_bytes
    else:
        return None

# --------------------------------------------------------
# 🔹 STEP 4: Post to LinkedIn
# --------------------------------------------------------
def post_to_linkedin(title, content):
    try:
        post_text = f"{title}\n\n{content[:2500]}..."
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "author": "urn:li:person:YOUR_PERSON_URN_ID",  # Replace with your LinkedIn person URN
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts", headers=headers, json=data
        )
        if response.status_code == 201:
            return "✅ Successfully posted to LinkedIn!"
        else:
            return f"⚠️ LinkedIn post failed: {response.text}"
    except Exception as e:
        return f"❌ LinkedIn Error: {e}"

# --------------------------------------------------------
# 🔹 STEP 5: Send Newsletter via Gmail SMTP
# --------------------------------------------------------
def send_newsletter(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = MAIL_SENDER
        msg["To"] = ", ".join(NEWSLETTER_RECIPIENTS)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_SENDER, MAIL_APP_PASSWORD)
            server.sendmail(MAIL_SENDER, NEWSLETTER_RECIPIENTS, msg.as_string())

        return "✅ Newsletter sent successfully!"
    except Exception as e:
        return f"❌ Newsletter error: {e}"

# --------------------------------------------------------
# 🔹 STEP 6: Streamlit UI
# --------------------------------------------------------
st.set_page_config(page_title="AI Blog + LinkedIn Poster", page_icon="🚀", layout="centered")
st.title("🚀 AI Blog Generator + Image + LinkedIn + Newsletter")
st.write("Create an **SEO blog**, generate **AI image**, and post to **LinkedIn** or send as **Newsletter** — all in one click ⚡")

# Inputs
keyword = st.text_input("Enter Blog Topic:")
tone = st.selectbox("Choose Tone:", ["Professional", "Friendly", "Informative", "Storytelling"])
length = st.selectbox("Select Length:", ["Short (300–400 words)", "Medium (600–800 words)", "Long (1000+ words)"])

# Generate blog & image
if st.button("✨ Generate Blog"):
    if keyword.strip():
        with st.spinner("Generating blog & image... ⏳"):
            blog = generate_blog(keyword, tone, length)
            image = generate_blog_image(keyword)

        st.success("✅ Blog Generated Successfully!")
        st.markdown(blog)
        if image:
            st.image(image, caption=f"AI Image for {keyword}", use_container_width=True)

        # Store for verification/posting
        st.session_state.blog_title = keyword
        st.session_state.blog_content = blog

# Post or Send Options
if "blog_content" in st.session_state:
    st.subheader("📤 Verify & Post")
    if st.checkbox("I’ve verified the content and image"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Post to LinkedIn"):
                status = post_to_linkedin(st.session_state.blog_title, st.session_state.blog_content)
                st.info(status)
        with col2:
            if st.button("Send Newsletter"):
                status = send_newsletter(st.session_state.blog_title, st.session_state.blog_content)
                st.info(status)

st.markdown("---")
st.caption("💡 Built with ❤️ using Gemini 2.5 Flash & Streamlit — by Yasmin's AI Blog Suite")

