import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import time
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import io

# Set page config (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="Kavyamanch QR Scanner",
    page_icon="📷",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize session state
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

def scan_qr_code(image):
    """Scan QR code from image."""
    try:
        # Convert PIL Image to numpy array and ensure it's in the right format
        img_array = np.array(image.convert('RGB'))
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Decode QR codes
        qr_codes = decode(gray)
        
        if not qr_codes:
            return None, "No QR code found in image"
        
        # Get the first QR code
        qr_data = qr_codes[0].data.decode('utf-8')
        return qr_data, None
        
    except Exception as e:
        logger.error(f"Error scanning QR code: {str(e)}")
        return None, f"Error scanning QR code: {str(e)}"

def mark_attendance(reg_number):
    """Mark attendance for a given registration number in the CSV file."""
    try:
        csv_path = 'Kavyamanch 2024 – Hindi Club (Responses) - Form Responses 1.csv'
        
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Initialize ATTENDANCE column if it doesn't exist
        if 'ATTENDANCE' not in df.columns:
            df['ATTENDANCE'] = False
        
        # Check if registration number exists
        mask = df['Reg. No.'] == reg_number
        if not mask.any():
            return False, "Registration number not found in the database"
        
        # Check if attendance is already marked
        if df.loc[mask, 'ATTENDANCE'].iloc[0] == True:
            student_name = df.loc[mask, 'Name'].iloc[0]
            return False, f"Attendance already marked for {student_name}"
        
        # Mark attendance as True (explicitly boolean)
        df.loc[mask, 'ATTENDANCE'] = True
        
        # Save the updated CSV
        df.to_csv(csv_path, index=False)
        
        # Get student name
        student_name = df.loc[mask, 'Name'].iloc[0]
        
        return True, f"Welcome {student_name}! Attendance marked successfully."
        
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        return False, f"Error marking attendance: {str(e)}"

def process_image(image):
    """Process the image and handle attendance marking."""
    # Display the image
    st.image(image, caption='QR Code Image', width=300)
    
    # Scan QR code
    reg_number, error = scan_qr_code(image)
    
    if error:
        st.error(error)
        if st.button("Try Again"):
            st.experimental_rerun()
    else:
        # Mark attendance
        success, message = mark_attendance(reg_number)
        
        if success:
            st.success(message)
            st.session_state.scan_count += 1
            st.session_state.last_scan = datetime.now().strftime("%H:%M:%S")
            st.balloons()
            if st.button("Scan Another"):
                st.experimental_rerun()
        else:
            st.error(message)
            if st.button("Try Again"):
                st.experimental_rerun()
        
        # Log the attempt
        logger.info(f"Scan attempt - Reg No: {reg_number}, Success: {success}, Message: {message}")

def main():
    # Remove the set_page_config from here since it's already set at the top
    
    # Add Hindi Club logo
    try:
        st.image("hindi.jpg", width=200)
    except:
        pass

    st.title("Kavyamanch Attendance Scanner")
    
    # Add statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Scans", st.session_state.scan_count)
    with col2:
        if st.session_state.last_scan:
            st.metric("Last Scan", st.session_state.last_scan)

    st.markdown("""
    ### 📱 Scan QR Code
    Choose one of these options:
    1. Use camera to scan QR code directly
    2. Upload a photo of the QR code
    """)
    
    tab1, tab2 = st.tabs(["📸 Camera Scanner", "📤 Upload Photo"])
    
    with tab1:
        st.markdown("Point your camera at the QR code and take a photo")
        picture = st.camera_input("Take a picture", key="camera")
        if picture:
            # Read image
            image = Image.open(picture)
            process_image(image)
            
    with tab2:
        st.markdown("Upload a photo of the QR code")
        uploaded_file = st.file_uploader("Upload QR Code Image", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            # Read image
            image = Image.open(uploaded_file)
            process_image(image)

    # Show attendance statistics
    if st.checkbox("Show Attendance Statistics"):
        try:
            df = pd.read_csv('Kavyamanch 2024 – Hindi Club (Responses) - Form Responses 1.csv')
            total = len(df)
            
            # Properly handle attendance values
            df['ATTENDANCE'] = df['ATTENDANCE'].fillna(False)
            df['ATTENDANCE'] = df['ATTENDANCE'].apply(lambda x: 
                True if isinstance(x, bool) and x 
                else True if isinstance(x, str) and x.lower() == 'true'
                else True if isinstance(x, (int, float)) and x == 1
                else False
            )
            present = int(df['ATTENDANCE'].sum())
            absent = total - present
            
            st.write("### Attendance Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Participants", total)
            col2.metric("Present", present)
            col3.metric("Absent", absent)
            
            # Show detailed attendance list
            if st.checkbox("Show Detailed List"):
                st.write("### Attendance List")
                # Create a more readable attendance display
                attendance_df = df[['Name', 'Reg. No.', 'ATTENDANCE']].copy()
                attendance_df['ATTENDANCE'] = attendance_df['ATTENDANCE'].map({True: 'Present', False: 'Absent'})
                st.dataframe(attendance_df)
                
        except Exception as e:
            logger.error(f"Error loading attendance data: {str(e)}")
            st.error(f"Error loading attendance data: {str(e)}")

if __name__ == "__main__":
    main()
