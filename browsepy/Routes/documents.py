import shutil
from flask import Blueprint, request, jsonify
from ..database import get_db_connection
from docx import Document
from docx.shared import Pt
import os
import re
from pymongo import MongoClient
import win32com.client
from ..database import get_db_connection
import pythoncom
import shutil

# Blueprint for the Word processing routes
documents_bp = Blueprint('documents', __name__)

# ---------- Configuration ----------
# MongoDB connection setup
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["Manage_Files_DB"]
values_collection = mongo_db["Customers_Fields"]

# Regular expression to match placeholders in the format {{name,type,length,required,description}}
VARIABLE_REGEX = r"\{\{([a-zA-Z0-9_]+(?:,[a-zA-Z0-9_]+)*)\}\}"

# Function to convert DOC files to DOCX format using Word COM API
def convert_doc_to_docx(input_path):
    try:
        pythoncom.CoInitialize()  # Initialize COM library for the current thread
        print(f"🔄 מנסה להמיר את הקובץ: {input_path}")
        # Initialize Word application
        word = win32com.client.Dispatch("Word.Application")
        print("✅ Microsoft Word הופעל") 
        doc = word.Documents.Open(input_path)
        output_path = os.path.splitext(input_path)[0] + ".docx"
        doc.SaveAs(output_path, FileFormat=16)  # 16 is the code for docx format
        doc.Close()
        word.Quit()
        print(f"✅ הקובץ נשמר בהצלחה בנתיב: {output_path}")
        return output_path
    except Exception as e:
        print("Error in DOC to DOCX conversion:", e)
        return None

# Function to back up the original file before replacing it
# def backup_and_replace(input_path):
    
#     # Define the backup directory (you can change this path to a location of your choice)
#     backup_dir = os.path.join(os.path.dirname(input_path), "backups")
    
#     # Ensure the backup directory exists
#     if not os.path.exists(backup_dir):
#         os.makedirs(backup_dir)

#     # Create a backup filename based on the original file name and timestamp
#     backup_filename = os.path.join(backup_dir, f"{os.path.basename(input_path)}_backup_{int(time.time())}.docx")

#     # Copy the original file to the backup directory
#     shutil.copy2(input_path, backup_filename)
#     print(f"✅ גיבוי הקובץ נשמר בנתיב: {backup_filename}")

#     # Now proceed with saving the new file (overwriting the original file)
#     doc.save(input_path)  # Save the processed document back to the original location
#     print(f"✅ הקובץ הוחלף בהצלחה בנתיב: {input_path}")

#     return backup_filename  # Return the backup file path in case it's needed for reference


# Function to highlight text in yellow in the Word document
def create_highlighted_run(text, paragraph):
    run = paragraph.add_run(text)
    run.font.highlight_color = 7  # Yellow highlight
    run.font.name = 'Arial'
    run.font.size = Pt(12)
    return run

# Function to process DOCX files and replace placeholders
def process_docx(path):
    # Save a backup of the original file before processing
    backup_path = path + ".bak"
    shutil.copy2(path, backup_path)  # Copy the original file as backup
    
    doc = Document(path)
    conn = get_db_connection()
    cursor = conn.cursor()
    variables_not_found = []

    # Iterate through all paragraphs in the document
    for para in doc.paragraphs:
        if not re.search(VARIABLE_REGEX, para.text):
            continue

        new_text = ""
        last_end = 0

        # Loop through each placeholder and replace with actual data
        for match in re.finditer(VARIABLE_REGEX, para.text):
            full_match = match.group(0)
            start, end = match.span()

            new_text += para.text[last_end:start]

            parts = match.group(1).split(',')
            if len(parts) < 5:
                new_text += full_match
                last_end = end
                continue

            var_name, var_type, var_len, var_required, var_description = [p.strip() for p in parts]

            # SQL: Check if the variable exists
            cursor.execute("SELECT COUNT(*) FROM Fields WHERE name = ?", (var_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Fields (name, type, length, required) VALUES (?, ?, ?, ?)",
                               (var_name, var_type, int(var_len), int(var_required == '*')))
                conn.commit()

            # MongoDB: Retrieve the value for the placeholder
            value_doc = values_collection.find_one({"name": var_name})
            value = value_doc.get("value") if value_doc else None

            # If value is missing, highlight the placeholder in yellow and mark it as missing
            if not value:
                variables_not_found.append(var_name)
                value = "     "  # 5 spaces

                # Add 5 spaces with yellow highlight
                create_highlighted_run("     ", para)

            new_text += str(value)
            last_end = end

        new_text += para.text[last_end:]
        para.clear()  # Clear the paragraph before adding the new text
        run = para.add_run(new_text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)

    # Save the processed document, overwrite the original file
    doc.save(path)

    print(f"✅ File saved as: {path}")
    if variables_not_found:
        print("⚠️ Missing variables:", variables_not_found)

# ---------- Routes for Word Processing ----------

# Route to convert DOC to DOCX and process it
@documents_bp.route('/process_doc', methods=['POST'])
def process_doc():
    data = request.get_json()

    # Get file path from the request
    input_path = data.get('file_path')

    # Validate input
    if not input_path:
        return jsonify({"message": "חובה לספק את נתיב הקובץ"}), 400

    # If the file is in DOC format, convert it to DOCX
    if input_path.endswith(".doc"):
        input_path = convert_doc_to_docx(input_path)
        if not input_path:
            return jsonify({"message": "שגיאה בהמרה לקובץ DOCX"}), 500

    # Process the DOCX file
    process_docx(input_path)

    return jsonify({"message": "הקובץ עובר עיבוד בהצלחה"}), 200

# Route for testing the Word document conversion
@documents_bp.route('/convert_docx', methods=['POST'])
def convert_to_docx():
    data = request.get_json()

    # Get file path from the request
    input_path = data.get('file_path')

    # Validate input
    if not input_path:
        return jsonify({"message": "חובה לספק את נתיב הקובץ"}), 400

    # Convert DOC to DOCX
    output_path = convert_doc_to_docx(input_path)

    if not output_path:
        return jsonify({"message": "שגיאה בהמרה לקובץ DOCX"}), 500

    return jsonify({"message": "הקובץ הומר בהצלחה ל-DOCX", "output_path": output_path}), 200
# Route to process DOCX files   
@documents_bp.route('/process_docx', methods=['POST'])
def process_docx():
    data = request.get_json()

    # Get file path from the request
    input_path = data.get('file_path')

    # Validate input
    if not input_path:
        return jsonify({"message": "חובה לספק את נתיב הקובץ"}), 400

    # Process the DOCX file
    process_docx(input_path)

    return jsonify({"message": "הקובץ עובר עיבוד בהצלחה"}), 200