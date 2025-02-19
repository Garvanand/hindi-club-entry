# QR Code Email Sender

This Python script generates and emails QR codes to registered participants based on their registration numbers.

## Features

- Reads participant data from a CSV file
- Generates QR codes with registration numbers
- Adds visual labels to QR codes
- Sends personalized emails with QR code attachments
- Includes comprehensive error handling and logging
- Uses environment variables for secure SMTP configuration

## Prerequisites

- Python 3.7 or higher
- Required Python packages (install using `requirements.txt`)

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your SMTP settings:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

   Note: If using Gmail, you'll need to create an App Password in your Google Account settings.

## CSV File Format

Create a `registrations.csv` file with the following columns:
```
registration_number,email
REG001,participant1@example.com
REG002,participant2@example.com
```

## Usage

1. Place your `registrations.csv` file in the project directory
2. Run the script:
   ```
   python qr_email_sender.py
   ```

## Error Handling

The script includes comprehensive error handling for:
- Missing or invalid CSV files
- Invalid email addresses
- QR code generation failures
- Email sending failures
- Missing SMTP credentials

Errors are logged to the console with timestamps for debugging.

## Output

- Generated QR codes are saved in the `qr_codes` directory
- Each participant receives an email with their QR code attached
- A log of successful sends and errors is displayed in the console
