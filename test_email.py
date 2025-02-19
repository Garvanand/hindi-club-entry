from qr_email_sender import QREmailSender
import os
from dotenv import load_dotenv
import shutil

def test_single_email():
    try:
        # Initialize the sender
        sender = QREmailSender()
        
        # Test registration number
        test_reg = "TEST001"
        
        # Make sure hindi.jpg exists in the correct location
        if not os.path.exists('hindi.jpg'):
            print("Error: hindi.jpg not found in the current directory")
            return
        
        # Generate QR code
        qr_path = sender.generate_qr_code(test_reg)
        print(f"Generated QR code at: {qr_path}")
        
        # Send test email
        sender.send_email("garvanand03@gmail.com", test_reg, qr_path)
        print("Test email sent successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_single_email()
