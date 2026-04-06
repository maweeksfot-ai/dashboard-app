import streamlit as st
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

email_map = {
    "Alice": "alice@email.com",
    "Bob": "bob@email.com",
    "Charlie": "charlie@email.com",
    "Maweeks": ""
}

def send_email(to_email, subject, body, attachment=None, attachment_name=None):
    sender_email = st.secrets["EMAIL"]
    app_password = st.secrets["APP_PASSWORD"]
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach file if provided
    if attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment_name}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

st.title("Report an Issue")

well_options = [f"Deep Well {i}" for i in list(range(1, 46)) + list(range(101, 108))]
recipient_options = ["Alice", "Bob", "Charlie", "Maweeks"]

with st.form("issue_form"):
    well = st.selectbox("Select Well", well_options, key="well")
    issue_date = st.date_input("Select Date", value=date.today(), key="date")
    description = st.text_area("Describe the Issue", key="description")
    reported_by = st.text_input("Your Name", key="reported_by")
    notify_person = st.selectbox("Notify Person", recipient_options, key="notify")
    uploaded_file = st.file_uploader("Attach Image (optional)", type=["png", "jpg", "jpeg"], key="attachment")

    submitted = st.form_submit_button("Submit Issue")

if submitted:
    if not description or not reported_by:
        st.error("Please fill out all required fields.")
    else:
        # Build email body
        to_email = email_map.get(notify_person)
        subject = f"Issue Report - {well}"
        body = f"""
Well: {well}
Date: {issue_date}
Reported By: {reported_by}

Issue:
{description}
"""

        # Send email with optional attachment
        send_email(to_email, subject, body, uploaded_file, uploaded_file.name if uploaded_file else None)
        st.success(f"Issue submitted and email sent to {notify_person}!")

        # Clear the form fields
        for key in ["well", "date", "description", "reported_by", "notify", "attachment"]:
            if key in st.session_state:
                del st.session_state[key]

        # Rerun to reset the form
        st.rerun()