import email
import json
import requests


def parse_email(file_path):
    # Open and parse the .eml file
    with open(file_path, 'r') as file:
        msg = email.message_from_file(file)

    # Extract relevant fields
    sender = msg['From']
    recipient = msg['To']
    subject = msg['Subject']
    date = msg['Date']
    body = msg.get_payload(decode=True)

    # Extract company ID
    company_id = sender.split('@')[1]

    return {
        'sender': sender,
        'recipient': recipient,
        'subject': subject,
        'date': date,
        'body': body,
        'company': company_id
    }


def post_to_api(data):
    # Post extracted data to the API
    response = requests.post('https://getkini.readme.io/', json=data)
    return response.status_code





def convert_to_json(data):
    # Convert data to JSON format
    return json.dumps(data, indent=4)


# Usage example
email_data = parse_email('application-1.eml')
# api_response = post_to_api(email_data)
json_data = convert_to_json(email_data)

# print(api_response)
print(json_data)

