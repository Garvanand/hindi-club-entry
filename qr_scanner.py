import cv2
from pyzbar.pyzbar import decode
import pandas as pd
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QRScanner:
    def __init__(self, csv_path):
        """Initialize the QR Scanner with the path to the CSV file."""
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        self.camera = None
        
    def save_csv(self):
        """Save the updated DataFrame back to CSV."""
        try:
            self.df.to_csv(self.csv_path, index=False)
            logger.info("CSV file updated successfully")
        except Exception as e:
            logger.error(f"Error saving CSV file: {str(e)}")
            raise

    def update_attendance(self, reg_number):
        """Update attendance status for a given registration number."""
        try:
            # Find the row with matching registration number
            mask = self.df['Reg. No.'] == reg_number
            if not mask.any():
                logger.warning(f"Registration number {reg_number} not found in CSV")
                return False

            # Update the ATTENDANCE column to TRUE
            self.df.loc[mask, 'ATTENDANCE'] = True
            
            # Get participant name for logging
            participant_name = self.df.loc[mask, 'Name'].iloc[0]
            
            # Save the changes
            self.save_csv()
            
            logger.info(f"Marked attendance for {participant_name} ({reg_number})")
            return True

        except Exception as e:
            logger.error(f"Error updating attendance: {str(e)}")
            return False

    def process_qr_code(self, frame):
        """Process a frame and decode QR code if present."""
        try:
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Decode QR codes in the frame
            qr_codes = decode(gray)
            
            for qr_code in qr_codes:
                # Extract registration number from QR code
                reg_number = qr_code.data.decode('utf-8')
                
                # Draw rectangle around QR code
                points = qr_code.polygon
                if len(points) == 4:
                    for i in range(4):
                        cv2.line(frame, 
                                (points[i].x, points[i].y),
                                (points[(i+1)%4].x, points[(i+1)%4].y),
                                (0, 255, 0), 3)
                
                # Update attendance
                if self.update_attendance(reg_number):
                    # Display success message on frame
                    cv2.putText(frame, f"Attendance Marked: {reg_number}",
                              (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                              (0, 255, 0), 2)
                else:
                    # Display error message on frame
                    cv2.putText(frame, f"Invalid Registration: {reg_number}",
                              (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                              (0, 0, 255), 2)
                
                return True, frame
            
            return False, frame

        except Exception as e:
            logger.error(f"Error processing QR code: {str(e)}")
            return False, frame

    def start_webcam(self):
        """Start the webcam and begin scanning QR codes."""
        try:
            self.camera = cv2.VideoCapture(0)
            logger.info("Webcam started successfully")
            
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    logger.error("Failed to grab frame from camera")
                    break

                # Display the current time on the frame
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, current_time, (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Process the frame
                qr_found, processed_frame = self.process_qr_code(frame)
                
                # Display the frame
                cv2.imshow('QR Scanner', processed_frame)
                
                # If QR code was found, wait a bit longer to show the result
                if qr_found:
                    time.sleep(2)
                
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            logger.error(f"Error in webcam scanning: {str(e)}")
        
        finally:
            if self.camera is not None:
                self.camera.release()
            cv2.destroyAllWindows()
            logger.info("Scanner stopped")

    def scan_image(self, image_path):
        """Scan a QR code from an image file."""
        try:
            # Read the image
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Process the image
            qr_found, processed_frame = self.process_qr_code(frame)
            
            if qr_found:
                # Save the processed image with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"scanned_{timestamp}.jpg"
                cv2.imwrite(output_path, processed_frame)
                logger.info(f"Processed image saved as: {output_path}")
            
            return qr_found

        except Exception as e:
            logger.error(f"Error scanning image: {str(e)}")
            return False

def main():
    try:
        # Initialize scanner with CSV file
        csv_path = 'Kavyamanch 2024 – Hindi Club (Responses) - Form Responses 1.csv'
        scanner = QRScanner(csv_path)
        
        # Start webcam scanning
        scanner.start_webcam()

    except Exception as e:
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
