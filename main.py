import re
from bs4 import BeautifulSoup
import base64
import email
from email import policy


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

    body = ''
    attachments_data = []
    processed_filenames = set()  # Set to track processed filenames
    body_processed = False

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if part.get_content_type() in ['text/plain', 'text/html'] and not part.get('Content-Disposition'):
                if not body_processed:
                    payload = part.get_payload(decode=True)
                    body = payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
                    body_processed = True

            elif part.get('Content-Disposition'):
                filename = part.get_filename()
                if filename and filename not in processed_filenames:  # Check if filename has been processed
                    processed_filenames.add(filename)  # Mark filename as processed
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

    return body, msg, attachments_data


def extract_details(email_body, subject):
    soup = BeautifulSoup(email_body, 'lxml')

    # from html body
    date_match = soup.find(string=re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b'))
    date = date_match.strip() if date_match else 'No valid date found'
    email_address = soup.find('a', href=lambda href: href and 'mailto:' in href).text.strip()

    ref_texts = soup.find_all(string=lambda text: 'Referenznummer' in text or 'RefNr.' in text)
    ref_nr1 = next((text.split('Referenznummer')[1].split()[0] for text in ref_texts if 'Referenznummer' in text), None)
    ref_nr = ref_nr1 or next((text.split('RefNr.')[1].split()[0] for text in ref_texts if 'RefNr.' in text),
                             'RefNr not found')

    # from subject
    name_match = re.search(r"von\s+(\w+\s+\w+)", subject)
    name = name_match.group(1) if name_match else "Name not found"

    role_match = re.search(r"als\s+(.+?)\s+\(", subject)
    role = role_match.group(1) if role_match else "Role not found"

    return date, email_address, name, role, ref_nr


def extract_company_id(receiver_email):
    id_match = re.search(r'applications\+(\d+)@getkini.com', receiver_email)
    return id_match.group(1) if id_match else "Company ID not found"


def main(file_path):
    email_body, msg, attachments = parse_email(file_path)

    sender = msg['From']
    receiver = msg['To']
    subject = msg['Subject']

    date, email_address, name, role, ref_nr = extract_details(email_body, subject)
    company_id = extract_company_id(receiver)

    name_list = name.split()
    first_name = name_list[0]
    last_name = name_list[-1]

    print(f"First name: {first_name}")
    print(f"Last name: {last_name}")

    # Print extracted information
    print(f"Sender: {sender}")
    print(f"Company_id: {company_id}")
    # print(f"Subject: {subject}")
    print(f"Date: {date}")
    print(f"Email: {email_address}")
    print(f"Role: {role}")
    print(f"RefNr: {ref_nr}")

    for attachment in attachments:
        print(f"Type: {attachment['type']}")
        print(f"Name: {attachment['name']}")
        print(f"Content Type: {attachment['content_type']}")
        print(f"Data: {attachment['data'][:30]}... (truncated for display)")


# Usage example
if __name__ == '__main__':
    main('application-2.eml')
