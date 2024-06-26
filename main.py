import os
import re
import requests
from bs4 import BeautifulSoup
import base64
import email
from email import policy
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()


def get_token():
    url = "https://api.dev.getkini.com/token/"
    payload = {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD")
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()  # Parse the JSON response into a dictionary

    return data["access"]


def send_application(access_token, payload):
    url = "https://api.dev.getkini.com/applications/"
    headers = {
        "accept": "application/json",
        "Company-Id": "3",
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    return response.text


def determine_attachment_type(filename):
    lower_filename = filename.lower()
    if 'cv' in lower_filename or 'resume' in lower_filename:
        return 'cv'
    elif 'cover' in lower_filename or 'letter' in lower_filename:
        return 'cover-letter'
    elif 'photo' in lower_filename or 'picture' in lower_filename or 'image' in lower_filename:
        return 'photo'
    else:
        return 'other'


def parse_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        msg = email.message_from_file(file, policy=policy.default)  # create an email message object.

    body = ''
    attachments_data = []
    processed_filenames = set()  # Set to track processed filenames
    body_processed = False

    if msg.is_multipart():
        for part in msg.walk():

            if part.get_content_type() in ['text/plain', 'text/html'] and not part.get('Content-Disposition'):
                if not body_processed:
                    payload = part.get_payload(decode=True)
                    body = payload.decode(part.get_content_charset() or 'utf-8',
                                          errors='replace')  # decode the payload in a string
                    body_processed = True

            elif part.get('Content-Disposition'):
                filename = part.get_filename()
                if filename and filename not in processed_filenames:  # Check if filename has been processed
                    processed_filenames.add(filename)  # Mark filename as processed
                    payload = part.get_payload(decode=True)

                    data = base64.b64encode(payload).decode()  # Encode the payload in base64 and decode it in a string

                    attachment_type = determine_attachment_type(filename)
                    content_type = part.get_content_type()
                    # Check if content_type is "jpg" and replace with "jpeg"
                    if content_type == "image/jpg":
                        content_type = "image/jpeg"

                    attachments_data.append({
                        'type': attachment_type,
                        'name': filename.split('.')[0],
                        'content_type': content_type,  # Use the original content_type value
                        'data': data
                    })

    return body, msg, attachments_data


def extract_details(email_body, subject):
    soup = BeautifulSoup(email_body, 'lxml')

    # from HTML body
    # get date
    date_match = soup.find(string=re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b'))  # check for date in the format dd.mm.yyyy
    date_old = date_match.strip() if date_match else None
    # Only parse and reformat the date if it is not None
    if date_old:
        date_obj = datetime.strptime(date_old, "%d.%m.%Y")
        date = date_obj.strftime("%Y-%m-%dT%H:%M:%S+00:00")  # Format the date in the ISO 8601
    else:
        date = None

    # get email address
    email_address = soup.find('a', href=lambda href: href and 'mailto:' in href).text.strip()
    # get RefNr
    ref_texts = soup.find_all(string=lambda text: 'Referenznummer' in text or 'RefNr.' in text)
    ref_nr1 = next((text.split('Referenznummer')[1].split()[0] for text in ref_texts if 'Referenznummer' in text), None)
    ref_nr = ref_nr1 or next((text.split('RefNr.')[1].split()[0] for text in ref_texts if 'RefNr.' in text), None)

    # from subject
    # get name
    name_match = re.search(r"von\s+(\w+\s+\w+)", subject)  #
    name = name_match.group(1) if name_match else None
    # get role
    role_match = re.search(r"als\s+(.+?)\s+\(", subject)
    role = role_match.group(1) if role_match else None

    return date, email_address, name, role, ref_nr


# get company id
def extract_company_id(receiver_email):
    id_match = re.search(r'applications\+(\d+)@getkini.com', receiver_email)  # ex
    return id_match.group(1) if id_match else None


def main(file_path):

    token = get_token()
    email_body, msg, attachments = parse_email(file_path)

    # get easy basic information
    sender = msg['From']
    receiver = msg['To']
    subject = msg['Subject']

    company_id = extract_company_id(receiver)
    date, email_address, name, role, ref_nr = extract_details(email_body, subject)

    # split name into first and last name
    name_list = name.split()
    first_name = name_list[0]
    last_name = name_list[-1]

    # paste information
    candidate_info = {
        "email": email_address,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": name,
        "location": {
            "street": "",
            "city": "",
            "country": ""
        }
    }

    attachments_list = []
    for attachment in attachments:
        attachments_list.append({
            "type": attachment['type'],
            "content_type": attachment['content_type'],
            "name": attachment['name'],
            "data": attachment['data'][:40]  # Only show the first 40 characters bc it would work if its full length
        })

    # Combine everything into a single structure
    application = {
        "candidate": candidate_info,
        "attachments": attachments_list,
        "external_job_id": company_id,
        "applied_at": date
    }

    json_application = {
        "candidate": candidate_info,
        "attachments": attachments_list,
        "additional_info": {
            "sender": sender,
            "receiver": receiver,
            "company_id": company_id,
            "subject": subject,
            "role": role,
            "ref_nr": ref_nr,
            "date": date
        }
    }

    # print the application data in JSON format
    print(json.dumps(json_application, indent=4))
    # api call
    print(send_application(token, application))


# run
if __name__ == '__main__':
    main('application-2.eml')
