import json
import requests
import os
from dotenv import load_dotenv
import base64
import email
from email import policy

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
        msg = email.message_from_file(file, policy=policy.default)

    attachments_data = []

    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = part.get('Content-Disposition')
        if content_disposition:
            filename = part.get_filename()
            if filename:
                payload = part.get_payload(decode=True)
                data = base64.b64encode(payload).decode()

                attachment_type = determine_attachment_type(filename)
                readable_content_type = {
                    'application/pdf': 'Pdf',
                    'image/jpeg': 'Jpeg',
                    'image/png': 'Png',
                    'text/plain': 'Plain Text',
                    'application/msword': 'Ms Word',
                }.get(content_type, content_type.split('/')[-1].capitalize())

                attachments_data.append({
                    'type': attachment_type,
                    'name': filename.split('.')[0],
                    'content_type': readable_content_type,
                    'data': data
                })

    return attachments_data

def convert_to_json(data):
    return json.dumps(data, indent=4)

# Example usage of parse_email
file_path = 'application-2.eml'
attachments = parse_email(file_path)



# Extracting additional data from the email body as required...
# (Process the soup object to extract other required information like name, email, etc.)

# Print extracted information

# Continue to extract and print other information as needed

# Example of how to use the extracted attachments data
for attachment in attachments:
    print(f"Type: {attachment['type']}")
    print(f"Name: {attachment['name']}")
    print(f"Content Type: {attachment['content_type']}")
    print(f"Data: {attachment['data'][:30]}... (truncated for display)")

# Example of token retrieval and sending an application
# token_response = get_token()
# token_data = json.loads(token_response)
# access_token = token_data.get('access_token')
# application_payload = {}  # Define the payload
# send_application_response = send_application(access_token, application_payload)
# print(send_application_response)
