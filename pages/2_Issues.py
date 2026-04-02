import streamlit as st
from datetime import date
import smtplib
from email.mime.text import MIMEText

email_map = {
    "Alice": "alice@email.com",
    "Bob": "bob@email.com",
    "Charlie": "charlie@email.com",
    "Maweeks": "maweeks.fot@maweeks.com"
}

def send_email(to_email, subject, body):
    sender_email = st.secrets["EMAIL"]
    app_password = st.secrets["APP_PASSWORD"]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

st.title("Report an Issue")

# Build well list: 1–45 and 101–107
well_options = [f"Deep Well {i}" for i in list(range(1, 46)) + list(range(101, 108))]

# Temporary recipient list
recipient_options = ["Alice", "Bob", "Charlie", "Maweeks"]

with st.form("issue_form"):
    well = st.selectbox("Select Well", well_options, key="well")
    issue_date = st.date_input("Select Date", key="date")
    description = st.text_area("Describe the Issue", key="description")
    reported_by = st.text_input("Your Name", key="reported_by")
    notify_person = st.selectbox("Notify Person", recipient_options, key="notify")

    # submitted = st.form_submit_button("Submit Issue")

    # 🚨 IMPORTANT: outside the form block but gated by submitted
#     if submitted:
#         if not description or not reported_by:
#             st.error("Please fill out all required fields.")
#         else:
#             st.success("Issue submitted!")

#             # Build email
#             to_email = email_map.get(notify_person)
#             subject = f"Issue Report - {well}"
#             body = f"""
#             Well: {well}
#             Date: {issue_date}
#             Reported By: {reported_by}

#             Issue:
#             {description}
#             """

#             # ✅ Only runs when button is pressed
#             send_email(to_email, subject, body)
            
#         for key in ["well", "date", "description", "reported_by", "notify"]:
#             if key in st.session_state:
#                 del st.session_state[key]

#         st.rerun()        

# if "issues" in st.session_state:
#     st.subheader("Submitted Issues")
#     st.write(st.session_state.issues)

# if submitted and not st.session_state.get("sent", False):
#     send_email(to_email, subject, body)
#     st.session_state.sent = True
    
# st.session_state.sent = False
# to_email = email_map.get(notify_person)

# subject = f"Issue Report - {well}"
# body = f"""
# Well: {well}
# Date: {issue_date}
# Reported By: {reported_by}

# Issue:
# {description}
# """

# send_email(to_email, subject, body)