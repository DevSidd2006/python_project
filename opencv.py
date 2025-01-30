import cv2
import pandas as pd
from pyzbar.pyzbar import decode
from datetime import datetime

# Function to initialize or load the existing Excel file for logging
def initialize_excel_file(file_name="attendence.xlsx"):
    try:
        # Try to read the existing Excel file
        df = pd.read_excel(file_name)
    except FileNotFoundError:
        # If the file doesn't exist, create a new DataFrame with appropriate columns
        df = pd.DataFrame(columns=["Date and Time", "QR Code Data"])
    return df, file_name

# Function to detect QR codes from live camera feed and log data to Excel
def detect_qr_from_live_camera():
    # Initialize webcam (camera index 0 for default webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Initialize the Excel file and load the data
    df, file_name = initialize_excel_file()

    # Set to store previously detected QR code data to avoid duplicate logging
    detected_qr_codes = set()

    while True:
        # Capture frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Optional: Resize the frame to improve detection (optional, can be adjusted)
        frame = cv2.resize(frame, (450, 250))

        # Decode QR codes in the frame
        qr_codes = decode(frame)

        # If QR codes are detected, process them
        for qr in qr_codes:
            qr_data = qr.data.decode('utf-8')  # Decode the QR data
            qr_type = qr.type  # QR code type (QR, EAN, etc.)
            points = qr.polygon  # Points for drawing the bounding box

            # Check if the QR code has already been detected
            if qr_data not in detected_qr_codes:
                # Mark the QR code as detected
                detected_qr_codes.add(qr_data)

                # Get the current timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Create a new DataFrame with the new row
                new_row = pd.DataFrame({"Date and Time": [timestamp], "QR Code Data": [qr_data]})

                # Concatenate the new row with the existing DataFrame
                df = pd.concat([df, new_row], ignore_index=True)

                # Save the updated DataFrame to the Excel file
                df.to_excel(file_name, index=False, engine="openpyxl")
                print(f"Detected QR Code: {qr_data} ({qr_type}) at {timestamp}")

                # Display QR code type and data on the frame
                cv2.putText(frame, f"{qr_type}: {qr_data}", (points[0][0], points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # Draw bounding box (if the QR code has 4 points)
                if len(points) == 4:
                    for i in range(len(points)):
                        cv2.line(frame, tuple(points[i]), tuple(points[(i + 1) % 4]), (0, 255, 0), 5)
                elif len(points) == 1:
                    # If only one point is detected, draw a small circle
                    cv2.circle(frame, tuple(points[0]), 10, (0, 0, 255), -1)  # Red circle

        # Show the frame with the detected QR codes
        cv2.imshow("QR Code Scanner", frame)

        # Exit loop if the user presses the "Esc" key
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

def detect_barcodes(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect barcodes in the image
    barcodes = decode(gray)
    
    # Loop over detected barcodes
    for barcode in barcodes:
        # Extract barcode data
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        
        # Get the barcode location
        (x, y, w, h) = barcode.rect
        
        # Draw rectangle around the barcode
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Put barcode data on the image
        cv2.putText(image, barcode_data, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    return image, barcodes

# Run the live QR code scanner with Excel logging
detect_qr_from_live_camera()
