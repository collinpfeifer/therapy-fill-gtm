import streamlit as st
import json
import os
from datetime import datetime, timedelta, UTC
import hashlib

# Path to the directory containing JSON files
DATA_DIR = "psychology_today/therapist_data/"
EMAIL_HISTORY_FILE = "psychology_today/email_history.json"
TRACKING_PIXELS_FILE = "psychology_today/tracking_pixels.json"
TRACKING_LINKS_FILE = "psychology_today/tracking_links.json"

EMAIL_TEMPLATES = {
    "Cold Outreach - Learning": '''Hi {name},

Nice to meet you virtually! My name is Collin and {fun_fact}

I’m reaching out because I went to school for clinical psychology and I want to learn about some of the work you do as a private practice owner.

I know your time is incredibly valuable, but if you would be willing to have a quick 20 minute chat to talk about your experience, I would love to talk!
''',
    "Followup - Learning": '''Hi {name},

Nice to meet you virtually! My name is Collin and {fun_fact}

I’m reaching out because I went to school for clinical psychology and I want to learn about some of the work you do as a private practice owner.

I know your time is incredibly valuable, but if you would be willing to have a quick 20 minute chat to talk about your experience, I would love to talk!
''',
    "Cold Outreach:Email - TherapyFill": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
  </head>
  <body>
      <p>Hi {name},</p>
      <p>
          When I would talk to therapists, cancellations kept coming up as a concern.
          <p>Usually the options would be:</p>
          <ol>
              <li>Seeing more clients</li>
              <li>Instituting higher cancellation fees or stricter policies</li>
              <li>Shuffling clients around to make it work</li>
          </ol>
          <p>But therapists weren’t happy with those options.</p>
          <p>
              To remedy this, I built <a href={tracking_link}>TherapyFill</a>, a cancellation platform that will field cancellation requests, work to reschedule your clients and find a replacement from your current caseload.
          </p>
      </p>
      <p>
         I’d love to hear your thoughts! If you’re interested in learning more, would you be open to a quick chat this week? You can also schedule a time that works for you <a href="https://cal.com/cpfeifer/10min">here</a>.
      </p>
      <p>Thanks, </p>
      <p>Collin</p>
      {tracking_pixel}
  </body>
</html>
''',
    "Cold Outreach:Psychology Today - TherapyFill": '''Hi {name},

When I would talk to therapists, cancellations kept coming up as a concern.

Usually the options would be:

1. Seeing more clients

2. Instituting higher cancellation fees or stricter policies

3. Shuffling clients around to make it work

But therapists weren't happy with those options.

To remedy this, I built TherapyFill (https://therapyfill.rudd-bebop.ts.net/), a cancellation platform that will field cancellation requests, work to reschedule your clients and find a replacement from your current caseload.

If you're interested in learning more, how about sometime this week? Alternatively you can schedule here (https://cal.com/cpfeifer/10min).
''',
    "Curious Outreach - Cancellations": '''Hi {name},

I’ve been chatting with therapists about last-minute cancellations, and I’m curious—how do you usually handle them?

Some have mentioned stricter cancellation policies, charging fees, or trying to reshuffle clients, but I’d love to hear what works for you.

If you have a quick second, I’d really appreciate your thoughts.'''
}

# Daily goal and all-time record
DAILY_GOAL = 10

# Set this value according to your desired follow-up period
FOLLOW_UP_WAITING_DAYS = 10

# Load email history


def load_email_history():
    if os.path.exists(EMAIL_HISTORY_FILE):
        with open(EMAIL_HISTORY_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

# Save email history


def save_email_history(history):
    with open(EMAIL_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

# Update email history


def update_email_history(email):
    today = datetime.now().strftime("%Y-%m-%d")
    history = load_email_history()

    if today not in history:
        history[today] = {"emails": [], "count": 0}

    history[today]["emails"].append(email)
    history[today]["count"] += 1
    save_email_history(history)


def generate_link_id(email: str, original_url: str = "https://therapyfill.rudd-bebop.ts.net/") -> str:
    return hashlib.md5(f"/track/{original_url}{email}{datetime.now(UTC)}".encode()).hexdigest()


def generate_pixel_id(email: str) -> str:
    # return f'<img src="https://therapyfill.rudd-bebop.ts.net/crm/pixel/{email}" width="1" height="1" style="display:none;">'
    return hashlib.md5(f"/pixel/{email}{datetime.now(UTC)}".encode()).hexdigest()


def load_tracking_pixels():
    if os.path.exists(TRACKING_PIXELS_FILE):
        with open(TRACKING_PIXELS_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


def load_tracking_links():
    if os.path.exists(TRACKING_LINKS_FILE):
        with open(TRACKING_LINKS_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


def save_tracking_pixels(data):
    with open(TRACKING_PIXELS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def save_tracking_links(data):
    with open(TRACKING_LINKS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def update_tracking_pixels(pixel_id, email):
    tracking_pixels = load_tracking_pixels()
    tracking_pixels[pixel_id] = {
        "email": email,
        "opens": []
    }
    save_tracking_pixels(tracking_pixels)


def update_tracking_links(link_id, email, original_url="https://therapyfill.rudd-bebop.ts.net/"):
    tracking_links = load_tracking_links()
    tracking_links[link_id] = {
        "original_url": original_url,
        "email": email,
        "clicks": []
    }
    save_tracking_links(tracking_links)

# Get the all-time best record


def get_best_record(history):
    if not history:
        return 0
    return max(day_data["count"] for day_data in history.values())

# Function to read therapist data from JSON files (with arrays) and remove duplicates


def load_therapist_data():
    therapists = []
    seen_uuids_ids = set()  # Set to track unique UUID and ID pairs

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list):  # Check if the JSON is an array
                        for therapist in data:
                            therapist_uuid = therapist.get("uuid")
                            therapist_id = therapist.get("id")

                            if (therapist_uuid, therapist_id) in seen_uuids_ids:
                                continue  # Skip duplicate entry

                            seen_uuids_ids.add((therapist_uuid, therapist_id))
                            therapists.append(therapist)
                    else:
                        st.warning(f"Skipping non-array JSON file: {filename}")
                except json.JSONDecodeError:
                    st.warning(f"Skipping invalid JSON file: {filename}")

    return therapists

# Function to update therapist data after emailing


def update_therapist_data(therapist_data):
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r") as file:
                data = json.load(file)

            updated = False

            if isinstance(data, list):  # Check if the JSON is an array
                for therapist in data:
                    # Find therapist by UUID and ID
                    if therapist["uuid"] == therapist_data["uuid"] and therapist["id"] == therapist_data["id"]:

                        # Ensure "emails" field exists
                        if "emails" not in therapist:
                            therapist["emails"] = []

                        # Handle "already_sent" and "send_later" fields
                        if therapist_data.get("already_sent") is not None:
                            therapist["already_sent"] = therapist_data["already_sent"]
                            updated = True

                        elif therapist_data.get("send_later") is not None:
                            therapist["send_later"] = therapist_data["send_later"]
                            updated = True

                        # Handle sending email updates
                        elif therapist_data.get("selected_email"):
                            # Add email if not already in the list
                            if therapist_data["selected_email"] not in therapist["emails"]:
                                therapist["emails"].append(
                                    therapist_data["selected_email"])
                            therapist["emailed"] = True
                            therapist["emailed_on"] = datetime.now().isoformat()
                            therapist["email_content"] = therapist_data["email_content"]
                            # therapist["tracking_pixel"] = []
                            # therapist["tracking_link"] = {
                            #     therapist_data["tracking_link"] : {
                            #         "original_url" : "therapyfill.rudd-bebop.ts.net/",
                            #         "email": therapist_data["selected_email"],
                            #         "clicks": []
                            #     }
                            # }
                            updated = True
                        else:
                            therapist["psychology_today_outreach"] = True
                            therapist["emailed"] = True
                            therapist["emailed_on"] = datetime.now().isoformat()
                            therapist["email_content"] = therapist_data["email_content"]
                            updated = True

                if updated:
                    # Save the updated therapist data back to the file
                    with open(os.path.join(DATA_DIR, filename), "w") as file:
                        json.dump(data, file, indent=4)

                    print(f"Updated therapist data in {filename}")


def load_therapist_follow_up(therapist_data):
    if not therapist_data:
        return []
    today = datetime.now()
    follow_ups = []
    for therapist in therapist_data:
        if therapist.get("emailed", False):
            sent_on = datetime.strptime(
                therapist["emailed_on"], "%Y-%m-%dT%H:%M:%S.%f")
            if (today - timedelta(days=FOLLOW_UP_WAITING_DAYS)) > sent_on:
                follow_ups.append(therapist)
    return follow_ups


# ======================================================================================#
# =======================================CRM============================================#
# Streamlit UI setup
st.title("Therapist CRM")

# Load therapist data and filter those who haven't been emailed yet
therapists = load_therapist_data()
email_history = load_email_history()

# Today's date
today = datetime.now().strftime("%Y-%m-%d")
emails_sent_today = email_history.get(today, {}).get("count", 0)
best_record = get_best_record(email_history)
follow_ups = load_therapist_follow_up(therapists)

# Side Bar
st.sidebar.text_input("Search for therapists")
# Sidebar
st.sidebar.header("Follow-up")

for therapist in follow_ups:
    with st.sidebar.expander(therapist["name"]):
        # Dropdown to choose an email template
        st.header("Email Templates")
        selected_template = st.selectbox("Choose a template", list(
            EMAIL_TEMPLATES.keys()), key=f"{therapist.get('uuid')}template")
        fun_fact = st.text_input(
            "Fun Fact", key=f"{therapist.get('uuid')}funfact")

        # Display the default email content based on the selected template
        email_content = st.text_area("Email Content",
                                     EMAIL_TEMPLATES[selected_template].format(
                                         name=therapist.get(
                                             "name").split(" ")[0],
                                         education="fellow IU" if therapist.get("education") and "Indiana University" in therapist.get(
                                             "education") else "clinical psychology",
                                         fun_fact=fun_fact,
                                     ), key=f"{therapist.get('uuid')}textarea",
                                     height=300)
        st.write(f"Education: {therapist.get('education', 'N/A')}")
        st.write(
            f"Website: {therapist.get('personal_website') or therapist.get('profile_link')}")

        # Dropdown to select an email from the therapist's list
        add_email = st.text_input(
            "Add email", key=f"{therapist['uuid']}_add_email")

        email_options = [
            email for email in therapist.get("emails", [])
        ]

        if add_email:
            email_options.insert(0, add_email)

        selected_email = st.selectbox(
            f"Select an email for {therapist['name']}", email_options, key=f"{therapist.get('uuid')}emails"
        )

# Progress bars
st.header("Daily Progress")
st.progress(min(emails_sent_today / DAILY_GOAL, 1.0))
st.write(f"Emails sent today: {emails_sent_today}/{DAILY_GOAL}")

st.header("All-Time Best Record")
st.progress(min(emails_sent_today / (best_record if best_record > 0 else 1), 1.0))
st.write(f"Your all-time best record is {best_record} emails in a day.")

# Load tracking data
with open(TRACKING_PIXELS_FILE, "r") as f:
    pixels_data = json.load(f)

with open(TRACKING_LINKS_FILE, "r") as f:
    links_data = json.load(f)

# Calculate total emails sent
total_emails = len(pixels_data)

# Calculate total opens
total_opens = sum(1 if len(entry["opens"]) >
                  0 else 0 for entry in pixels_data.values())

# Calculate total clicks
total_clicks = sum(1 if len(entry["clicks"]) >
                   0 else 0 for entry in links_data.values())

# Compute percentages
open_rate = (total_opens / total_emails) * 100 if total_emails > 0 else 0
click_through_rate = (total_clicks / total_emails) * \
    100 if total_emails > 0 else 0

# Display as a table
# st.write({
#    "Total Emails Sent": total_emails,
#    "Total Opens": total_opens,
#    "Total Clicks": total_clicks,
#    "Open Rate (%)": round(open_rate, 2),
#    "Click-Through Rate (%)": round(click_through_rate, 2)
# })
st.write(f"Total Emails Sent: {total_emails}")
st.write(f"Total Opens: {total_opens}")
st.write(f"Open Rate(%): {round(open_rate, 2)}")
st.write(f"Total Clicks: {total_clicks}")
st.write(f"Click-Through Rate (%): {round(click_through_rate, 2)}")

emailed_therapists = [t for t in therapists if not t.get("emailed", False) and not t.get(
    "send_later", False) and not t.get("already_sent", False)]

# Filter therapists marked for "Send Later"
therapists_send_later = [
    t for t in therapists if t.get("send_later", False)
]

if not emailed_therapists:
    st.write("No therapists to email.")
else:
    # Display therapists who haven't been emailed yet
    st.header(f"Therapists to email: {len(emailed_therapists)}")

    for therapist in emailed_therapists:
        with st.expander(therapist["name"]):
            # Dropdown to choose an email template
            st.header("Email Templates")
            selected_template = st.selectbox("Choose a template", list(
                EMAIL_TEMPLATES.keys()), key=f"{therapist.get('uuid')}template")
            fun_fact = st.text_input(
                "Fun Fact", key=f"{therapist.get('uuid')}funfact")
            # Dropdown to select an email from the therapist's list
            add_email = st.text_input(
                "Add email", key=f"{therapist['uuid']}_add_email")

            email_options = [
                email for email in therapist.get("emails", [])
            ]

            if add_email:
                email_options.insert(0, add_email)

            selected_email = st.selectbox(
                f"Select an email for {therapist['name']}", email_options, key=f"{therapist.get('uuid')}emails"
            )
            link_id = generate_link_id(selected_email)
            pixel_id = generate_pixel_id(selected_email)
            # Display the default email content based on the selected template
            email_content = st.text_area("Email Content",
                                         EMAIL_TEMPLATES[selected_template].format(
                                             name=therapist.get(
                                                 "name").split(" ")[0],
                                             education="fellow IU" if therapist.get("education") and "Indiana University" in therapist.get(
                                                 "education") else "clinical psychology",
                                             fun_fact=fun_fact,
                                             tracking_link=f'"https://therapyfill.rudd-bebop.ts.net/crm/track/{link_id}"',
                                             tracking_pixel=f'<img src="https://therapyfill.rudd-bebop.ts.net/crm/pixel/{pixel_id}" >'
                                         ), key=f"{therapist.get('uuid')}newcontent",
                                         height=300)
            st.write(f"Education: {therapist.get('education', 'N/A')}")
            st.write(
                f"Website: {therapist.get('personal_website') or therapist.get('profile_link')}")
            st.write(f"Link ID: {link_id}, Pixel ID: {pixel_id}")

            # Email sending section
            send_email = st.button(
                f"Sent Email to {selected_email or 'Psychology Today'}", key=f"{therapist['uuid']}{selected_email}")

            if send_email:
                # Update email history
                update_email_history({
                    "to": selected_email,
                    "content": email_content,
                    "therapist_name": therapist["name"],
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "date": today,
                })
                update_therapist_data({
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "name": therapist["name"],
                    "selected_email": selected_email,
                    "email_content": email_content
                })
                if selected_email is not None:
                    update_tracking_pixels(pixel_id, selected_email)
                    update_tracking_links(link_id, selected_email)
                # st.rerun()
                # st.success(f"Email sent to {therapist['name']} at {selected_email}")
            # Option to move therapist to "Send Later"
            if st.button(f"Move {therapist['name']} to Send Later", key=f"{therapist['uuid']}_send_later"):
                update_therapist_data({
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "send_later": True
                })
                st.rerun()

            if st.button(f"Move {therapist['name']} to Already Sent", key=f"{therapist['uuid']}_already_sent"):
                update_therapist_data({
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "already_sent": True
                })
                st.rerun()

# Display "Send Later" therapists
if therapists_send_later:
    st.header("Send Later Therapists")
    for therapist in therapists_send_later:
        with st.expander(therapist["name"]):
            # Dropdown to choose an email template
            st.header("Email Templates")
            selected_template = st.selectbox("Choose a template", list(
                EMAIL_TEMPLATES.keys()), key=f"{therapist.get('uuid')}template")
            fun_fact = st.text_input(
                "Fun Fact", key=f"{therapist.get('uuid')}funfact")

            # Display the default email content based on the selected template
            email_content = st.text_area("Email Content",
                                         EMAIL_TEMPLATES[selected_template].format(
                                             name=therapist.get(
                                                 "name").split(" ")[0],
                                             education="fellow IU alum" if therapist.get(
                                                 "education") and "Indiana University" in therapist.get("education") else "clinical psychology",
                                             fun_fact=fun_fact,
                                         ), key=f"{therapist.get('uuid')}textarea",
                                         height=300)
            st.write(f"Education: {therapist.get('education')}")
            st.write(f"Website: {therapist.get('personal_website')}")

            add_email = st.text_input(
                "Add email", key=f"{therapist['uuid']}_add_email")
            # Dropdown to select an email from the therapist's list
            email_options = [
                email for email in therapist.get("emails", [])
            ]

            if add_email:
                email_options.insert(0, add_email)

            selected_email = st.selectbox(
                f"Select an email for {therapist['name']}", email_options, key=f"{therapist.get('uuid')}emails"
            )

            # Email sending section
            send_email = st.button(
                f"Sent Email to {selected_email or 'Psychology Today'}", key=f"{therapist['name']}{selected_email}")

            if send_email:
                # Update email history
                update_email_history({
                    "to": selected_email,
                    "content": email_content,
                    "therapist_name": therapist["name"],
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "date": today,
                })
                update_therapist_data({
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "name": therapist["name"],
                    "selected_email": selected_email,
                    "email_content": email_content
                })
                st.success(
                    f"Email sent to {therapist['name']} at {selected_email}")
                # st.balloons()

            if st.button(f"Move {therapist['name']} to Already Sent", key=f"{therapist['uuid']}_already_sent"):
                update_therapist_data({
                    "uuid": therapist["uuid"],
                    "id": therapist["id"],
                    "already_sent": True,
                    "send_later": False
                })
                st.rerun()


# Email History Section
st.header("Email History")

# Show all available days
dates = list(email_history.keys())
dates.sort(reverse=True)  # Show the most recent first

# Dropdown for selecting a day
selected_date = st.selectbox("Select a day to view sent emails:", dates)

if selected_date:
    # Display the emails sent on the selected date
    emails_on_day = email_history[selected_date]["emails"]
    for email_data in emails_on_day:
        with st.expander(email_data["therapist_name"]):
            st.write(f"Email to {email_data['to']} on {selected_date}")
            st.write(f"Therapist: {email_data['therapist_name']}")
            st.code(email_data['content'])
