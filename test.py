import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import email
from email import policy





load_dotenv()



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





# Usage example
email_body = parse_email('application-1.eml')

soup = BeautifulSoup(email_body, 'lxml')

date_pattern = re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b')
# Find the first occurrence of the date pattern
date_match = soup.find(string=date_pattern)
# Extracting the actual date string
date = date_match.strip() if date_match else 'No valid date found'


# Extracting data based on the provided HTML structure
for div in soup.find_all('div'):
    if 'Mit freundlichen Grüßen' in div.text:
        # Find the last <br> tag and get the next sibling
        br_tags = div.find_all('br')
        if br_tags:
            name = br_tags[-1].next_sibling.strip()
            break


email = soup.find('a', href=lambda href: href and 'mailto:' in href).text.strip()

def find_reference_number(text):
    if 'Referenznummer' in text:
        return text.split('Referenznummer')[1].split()[0]
    elif 'RefNr.' in text:
        return text.split('RefNr.')[1].split()[0]
    return None

# Find all text containing 'Referenznummer' or 'RefNr.'
ref_texts = soup.find_all(string=lambda text: 'Referenznummer' in text or 'RefNr.' in text)
ref_nr = next((find_reference_number(text) for text in ref_texts if find_reference_number(text)), 'RefNr not found')


# Print extracted information
print(f"Date: {date}")
print(f"Name: {name}")
print(f"Email: {email}")
print(f"RefNr: {ref_nr}")
