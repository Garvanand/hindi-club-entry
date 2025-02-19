import csv
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QREmailSender:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([self.smtp_username, self.smtp_password]):
            raise ValueError("SMTP credentials not found in environment variables")
        
        # Create directory for QR codes if it doesn't exist
        self.qr_dir = Path('qr_codes')
        self.qr_dir.mkdir(exist_ok=True)

    def generate_qr_code(self, registration_number):
        """Generate a QR code with a label for the given registration number."""
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(registration_number)
            qr.make(fit=True)
            
            # Create QR code image with white background
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to PIL Image if it isn't already
            qr_image = qr_image.get_image()
            
            # Create a new image with space for label
            label_height = 40
            new_img = Image.new('RGB', 
                              (qr_image.width, qr_image.height + label_height), 
                              'white')
            
            # Paste QR code
            new_img.paste(qr_image, (0, 0))
            
            # Add label
            draw = ImageDraw.Draw(new_img)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except OSError:
                font = ImageFont.load_default()
                
            # Add registration number text
            text = f"Registration: {registration_number}"
            text_width = draw.textlength(text, font=font)
            text_position = ((new_img.width - text_width) // 2, qr_image.height + 10)
            draw.text(text_position, text, fill='black', font=font)
            
            # Save the image
            output_path = self.qr_dir / f"qr_{registration_number}.png"
            new_img.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating QR code for {registration_number}: {str(e)}")
            raise

    def send_email(self, email, registration_number, qr_code_path):
        """Send an email with the QR code attachment."""
        try:
            msg = MIMEMultipart('related')
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = f"Your Registration QR Code - {registration_number}"

            # Create the HTML body with embedded image
            html = f"""
            <html>
                <body>
                    <div style="text-align: center;">
                        <img src="cid:header_image" style="max-width: 100%; height: auto; margin-bottom: 20px;">
                    </div>
                    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <p>We are excited to have you join us for the upcoming Kavyamanch event. To ensure smooth entry and attendance, kindly find your unique QR code attached to this email. Please ensure that you carry this QR code with you and present it at the time of check-in on the day of the event.</p>

                        <p>If you have any questions or require assistance, feel free to reach out. We look forward to seeing you at the event and sharing an enriching experience together!</p>

                        <p>Regards,<br>
                        Tech Team,<br>
                        Hindi Club</p>
                    </div>
                </body>
            </html>
            """
            msg_alternative = MIMEMultipart('alternative')
            msg_alternative.attach(MIMEText(html, 'html'))
            msg.attach(msg_alternative)

            # Attach header image with Content-ID for HTML reference
            with open('hindi.jpg', 'rb') as f:
                img_data = f.read()
            header_image = MIMEImage(img_data)
            header_image.add_header('Content-ID', '<header_image>')
            msg.attach(header_image)

            # Attach QR code
            with open(qr_code_path, 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(qr_code_path))
            msg.attach(image)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Successfully sent email to {email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {email}: {str(e)}")
            raise

    def process_csv(self, csv_path):
        """Process the CSV file and send QR codes to participants."""
        success_count = 0
        error_count = 0
        
        try:
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                if not {'Reg. No.', 'University Mail ID'}.issubset(set(reader.fieldnames)):
                    raise ValueError("CSV must contain 'Reg. No.' and 'University Mail ID' columns")

                for row in reader:
                    reg_num = row['Reg. No.'].strip()
                    email = row['University Mail ID'].strip()

                    if not reg_num or not email:
                        logger.warning(f"Skipping row with missing data: {row}")
                        error_count += 1
                        continue

                    try:
                        # Generate QR code
                        qr_path = self.generate_qr_code(reg_num)
                        
                        # Send email
                        self.send_email(email, reg_num, qr_path)
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing registration {reg_num}: {str(e)}")
                        error_count += 1

        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise

        return success_count, error_count

def main():
    try:
        sender = QREmailSender()
        csv_path = 'Kavyamanch 2024 – Hindi Club (Responses) - Form Responses 1.csv'
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return

        success, errors = sender.process_csv(csv_path)
        logger.info(f"Processing complete. Successful: {success}, Errors: {errors}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
