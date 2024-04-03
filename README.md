# Email Parsing Script for Applications

## Overview

This Python script automates the extraction of pertinent details from emails and then posts this data to the KIRI API. This process requires careful consideration of the data’s structure within the emails and how it aligns with the API's requirements.

### Key Features

- **API Authentication (`get_token`)**: Authenticates with the `https://api.dev.getkini.com/token/` endpoint to obtain an access token using credentials stored in environment variables.
- **Send Application (`send_application`)**: Submits application data to the `https://api.dev.getkini.com/applications/` endpoint using the obtained access token.
- **Email Parsing (`parse_email`)**: Parses an email file to extract the body content and attachments.
- **Detail Extraction (`extract_details`, `extract_company_id`)**: Extracts specific details such as date, email address, name, role, reference number, and company ID from the parsed email content.

## Prerequisites

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
3. Paste `.eml` files in your Project
4. Select filename of the `.eml` you want to analyze:
   ```python
   main('application-1.eml')
   ``` 


   ```


Ensure that the file paths and credentials used in the script are valid and correct for your environment and use case.
