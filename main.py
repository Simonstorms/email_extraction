import json
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

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
    return response.text


def send_application(access_token, payload):
    url = "https://api.dev.getkini.com/applications/"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


import email
from email import policy

def parse_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        msg = email.message_from_file(file, policy=policy.default)

    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ['text/plain', 'text/html'] and not part.get('Content-Disposition'):
                payload = part.get_payload(decode=True)
                try:
                    body = payload.decode(part.get_content_charset() or 'utf-8')
                except UnicodeDecodeError:
                    try:
                        body = payload.decode('latin-1')  # Trying with 'latin-1' as a fallback
                    except UnicodeDecodeError:
                        body = payload.decode('utf-8', errors='replace')  # Replace undecodable chars
                break
    else:
        payload = msg.get_payload(decode=True)
        try:
            body = payload.decode(msg.get_content_charset() or 'utf-8')
        except UnicodeDecodeError:
            try:
                body = payload.decode('latin-1')  # Trying with 'latin-1' as a fallback
            except UnicodeDecodeError:
                body = payload.decode('utf-8', errors='replace')  # Replace undecodable chars

    return body


def convert_to_json(data):
    return json.dumps(data, indent=4)


# Usage example
email_body = parse_email('application-2.eml')

soup = BeautifulSoup(email_body, 'lxml')

# Extracting data based on the provided HTML structure
for div in soup.find_all('div'):
    if 'Mit freundlichen Grüßen' in div.text:
        # Find the last <br> tag and get the next sibling
        br_tags = div.find_all('br')
        if br_tags:
            name = br_tags[-1].next_sibling.strip()
            break


email = soup.find('a', href=lambda href: href and 'mailto:' in href).text.strip()

ref_element = soup.find(string=lambda text: text and 'RefNr.' in text)
ref_nr = ref_element.split('RefNr.')[1].split()[0] if ref_element else 'RefNr not found'


# Print extracted information
print(f"Name: {name}")
print(f"Email: {email}")
print(f"RefNr: {ref_nr}")
# token_response = get_token()
# token_data = json.loads(token_response)
# access_token = token_data.get('access_token')

# Example of sending application
# application_payload = {}  # You need to define the payload based on your application's requirements
# send_application_response = send_application(access_token, application_payload)
# print(send_application_response)

# If you need to parse attachments, ensure that the parse_email function
# includes logic to extract and return attachment details
