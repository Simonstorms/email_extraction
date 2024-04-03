import email
import re
from email import policy
from bs4 import BeautifulSoup


def parse_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        msg = email.message_from_file(file, policy=policy.default)

    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ['text/plain', 'text/html'] and not part.get('Content-Disposition'):
                payload = part.get_payload(decode=True)
                body = payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
                break
            
    else:
        payload = msg.get_payload(decode=True)
        body = payload.decode(msg.get_content_charset() or 'utf-8', errors='replace')

    return body, msg


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
    email_body, msg = parse_email(file_path)

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


# Usage example
if __name__ == '__main__':
    main('application-1.eml')
