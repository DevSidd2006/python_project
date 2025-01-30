from flask import Flask, request, jsonify, render_template
from numpy import __array_namespace_info__
from openpyxl import load_workbook
from datetime import datetime
import opencv  # Import your opencv.py file

app = Flask(__array_namespace_info__)

# Path to attendance Excel file
EXCEL_FILE = "attendance.xlsx"

@app.route("/")
def home():
    return render_template("attendance.html")  # Renders the frontend HTML

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    # Assuming OpenCV script processes an image and returns PRN
    image_path = request.form.get("image_path")  # Path to uploaded ID card image
    prn, roll_number, name = opencv.process_id_card(image_path)  # Call function from opencv.py

    if prn:
        # Update attendance in Excel
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            workbook = load_workbook(EXCEL_FILE)
            sheet = workbook.active
        except FileNotFoundError:
            return jsonify({"status": "error", "message": "Attendance file not found"})

        # Append data to Excel
        sheet.append([prn, roll_number, name, timestamp])
        workbook.save(EXCEL_FILE)
        return jsonify({"status": "success", "message": "Attendance marked", "prn": prn, "name": name})
    else:
        return jsonify({"status": "error", "message": "Unable to process ID card"})

if _name_ == "_main_":
    app.run(debug=True)