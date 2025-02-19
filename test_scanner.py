from qr_scanner import QRScanner
import os
import cv2
import qrcode
import logging
import pandas as pd
from pathlib import Path

def create_test_qr(reg_number, output_dir='test_qr_codes'):
    """Create a test QR code for testing the scanner."""
    Path(output_dir).mkdir(exist_ok=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(reg_number)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    output_path = os.path.join(output_dir, f'test_qr_{reg_number}.png')
    img.save(output_path)
    return output_path

def create_test_csv():
    """Create a test CSV file with sample data."""
    test_data = {
        'Timestamp': ['2025-02-20 01:00:00'],
        'Are you a VIT Student ?': ['Yes'],
        'Name': ['Test Student'],
        'Reg. No.': ['TEST001'],
        'Gender': ['Male'],
        'University Mail ID': ['test@vitbhopal.ac.in'],
        'Contact No.': ['1234567890'],
        'Batch': ['2024'],
        'ATTENDANCE': [False]
    }
    df = pd.DataFrame(test_data)
    test_csv_path = 'test_registrations.csv'
    df.to_csv(test_csv_path, index=False)
    return test_csv_path

def test_image_scanning():
    """Test QR code scanning from an image file."""
    print("\nTesting Image-based QR Scanning:")
    print("-" * 50)
    
    try:
        # Create test data
        reg_number = 'TEST001'
        test_csv_path = create_test_csv()
        qr_image_path = create_test_qr(reg_number)
        
        # Initialize scanner with test CSV
        scanner = QRScanner(test_csv_path)
        
        # Test scanning
        print(f"Scanning QR code from: {qr_image_path}")
        result = scanner.scan_image(qr_image_path)
        
        # Verify results
        if result:
            df = pd.read_csv(test_csv_path)
            attendance_marked = df.loc[df['Reg. No.'] == reg_number, 'ATTENDANCE'].iloc[0]
            print(f"QR Code detected: {reg_number}")
            print(f"Attendance marked in CSV: {attendance_marked}")
        else:
            print("Failed to detect QR code")
            
    except Exception as e:
        print(f"Error in image scanning test: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
        if os.path.exists(qr_image_path):
            os.remove(qr_image_path)
        if os.path.exists('test_qr_codes'):
            os.rmdir('test_qr_codes')

def test_webcam_scanning():
    """Test QR code scanning using webcam."""
    print("\nTesting Webcam QR Scanning:")
    print("-" * 50)
    
    try:
        # Create test data
        test_csv_path = create_test_csv()
        
        # Initialize scanner
        scanner = QRScanner(test_csv_path)
        
        print("Starting webcam test...")
        print("Instructions:")
        print("1. Show a QR code to the webcam")
        print("2. The scanner will detect and process the QR code")
        print("3. Press 'q' to quit the webcam test")
        
        # Start webcam scanning
        scanner.start_webcam()
        
    except Exception as e:
        print(f"Error in webcam scanning test: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

def main():
    print("Starting QR Scanner Tests")
    print("=" * 50)
    
    # Test image-based scanning
    test_image_scanning()
    
    # Test webcam scanning
    user_input = input("\nWould you like to test webcam scanning? (y/n): ")
    if user_input.lower() == 'y':
        test_webcam_scanning()
    
    print("\nTests completed!")

if __name__ == "__main__":
    main()
