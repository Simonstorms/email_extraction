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

    attachments_data = []
    processed_filenames = set()  # Set to track processed filenames

    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = part.get('Content-Disposition')
        if content_disposition:
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

    return attachments_data


# Example usage of parse_email
email_file = 'application-2.eml'
attachments = parse_email(email_file)

# Example of how to use the extracted attachments data
for attachment in attachments:
    print(f"Type: {attachment['type']}")
    print(f"Name: {attachment['name']}")
    print(f"Content Type: {attachment['content_type']}")
    print(f"Data: {attachment['data'][:30]}... (truncated for display)")
