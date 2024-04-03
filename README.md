# Email Parsing Script for Applications

## Overview

This Python script provides a comprehensive solution for automating application processes through API integration and email parsing. It includes functionalities to authenticate with an API to obtain an access token, send application data, parse emails to extract relevant information, and determine attachment types.

### Key Features

- **API Authentication (`get_token`)**: Authenticates with the `https://api.dev.getkini.com/token/` endpoint to obtain an access token using credentials stored in environment variables.
- **Send Application (`send_application`)**: Submits application data to the `https://api.dev.getkini.com/applications/` endpoint using the obtained access token.
- **Email Parsing (`parse_email`)**: Parses an email file to extract the body content and attachments.
- **Detail Extraction (`extract_details`, `extract_company_id`)**: Extracts specific details such as date, email address, name, role, reference number, and company ID from the parsed email content.

## Prerequisites

- Python installed on pc
- Requests: `pip install requests`
- Beautiful Soup 4: `pip install beautifulsoup4`
- Python-dotenv: `pip install python-dotenv`

## Setup

1. Ensure Python and the required packages are installed.
2. Store your API credentials (`USERNAME` and `PASSWORD`) in a `.env` file:
   ```
   USERNAME=your_username
   PASSWORD=your_password
   ```

## Usage

1. **Get Token**: Authenticate and obtain an access token.
   ```python
   access_token = get_token()
   ```
2. **Send Application**: Use the obtained token to send application data.
   ```python
   payload = {/* your application data */}
   send_application(access_token, payload)
   ```
3. **Parse Email**: Extract information from an email file.
   ```python
   email_body, msg, attachments = parse_email('path_to_email_file.eml')
   ```
4. **Extract Details**: Get specific details from the email content.
   ```python
   date, email_address, name, role, ref_nr = extract_details(email_body, msg['Subject'])
   ```
5. **Run Main Function**: Process an email file and send application data.
   ```python
   if __name__ == '__main__':
       main('path_to_email_file.eml')
   ```

## Function Descriptions

- `get_token()`: Fetches an access token from the API.
- `send_application(access_token, payload)`: Submits the application data along with the access token.
- `parse_email(file_path)`: Parses the email file to extract content and attachments.
- `extract_details(email_body, subject)`: Extracts date, email address, name, role, and reference number from the email body.
- `extract_company_id(receiver_email)`: Extracts the company ID from the receiver's email address.
- `main(file_path)`: Orchestrates the flow of parsing the email, extracting details, and sending the application.

Ensure that the file paths and credentials used in the script are valid and correct for your environment and use case.
