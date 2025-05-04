# import os
# import re
# from flask import Blueprint, request, jsonify, send_file
# from pymongo import MongoClient
# import fitz  # PyMuPDF
# import arabic_reshaper
# from bidi.algorithm import get_display
# from ..database import get_db_connection

# pdf_documents_bp = Blueprint('pdf_documents', __name__)

# mongo_client = MongoClient("mongodb://localhost:27017")
# mongo_db = mongo_client["Manage_Files_DB"]
# values_collection = mongo_db["Customers_Fields"]
# conn = get_db_connection()
# cursor = conn.cursor()

# VARIABLE_REGEX = r"\-\-(.*?)\-\-"

# def extract_values(sql_id):
#     return values_collection.find_one({"sql_id": sql_id}) or {}

# # פונקציה לעיבוד טקסט עברי
# def prepare_hebrew_text(text):
#     reshaped_text = arabic_reshaper.reshape(text)
#     bidi_text = get_display(reshaped_text)
#     return bidi_text

# def process_pdf(file_path, sql_id):
#     print("Starting PDF processing...")
#     doc = fitz.open(file_path)
#     values = extract_values(sql_id)
#     variables_not_found = []

#     # נתיב הגופן
#     font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansHebrewRegular.ttf'))

#     font_name = "NotoSansHebrew"

#     # טען את הגופן
#     try:
#         doc.add_font(fontfile=font_path, fontname=font_name, set_simple=True)
#         print(f"Font {font_name} loaded successfully")
#     except Exception as e:
#         print(f"Error loading font {font_name}: {e}")

#     for page_num, page in enumerate(doc, start=1):
#         print(f"\n--- Processing page {page_num} ---")
#         blocks = page.get_text("dict")["blocks"]
#         for b in blocks:
#             if "lines" not in b:
#                 continue
#             for line in b["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"]
#                     matches = list(re.finditer(VARIABLE_REGEX, text))
#                     if not matches:
#                         continue

#                     new_text = text

#                     for match in matches:
#                         full_match = match.group(0)
#                         inner = match.group(1)
#                         parts = [p.strip() for p in inner.split(',')]
#                         if len(parts) < 5:
#                             continue
#                         var_name, var_type, var_len, var_required, var_description = parts[:5]
#                         value = values.get(var_name)

#                         if value:
#                             replacement = str(value)
#                         else:
#                             if var_required == "*":
#                                 replacement = "_____"  # חובה אך חסר
#                                 variables_not_found.append(var_name)
#                             else:
#                                 replacement = ""

#                         new_text = new_text.replace(full_match, replacement)

#                     if new_text != text:
#                         rect = fitz.Rect(span["bbox"])
#                         rect.y1 = rect.y0 + 100000  # גובה מלאכותי

#                         page.add_redact_annot(rect, fill=(1, 1, 1))
#                         page.apply_redactions()

#                         if rect.width > 0 and rect.height > 0:
#                             hebrew_text = prepare_hebrew_text(new_text)
#                             ok = page.insert_textbox(
#                                 rect,
#                                 hebrew_text,
#                                 fontname=font_name,  # השתמש בגופן העברי
#                                 fontsize=span["size"],
#                                 color=(0, 0, 0),
#                                 align=2,
#                                 overlay=True,
#                             )
#                             if ok == 0:
#                                 print(f"⚠ לא הצליח לכתוב טקסט בתוך הריבוע: {rect}, טקסט: '{hebrew_text}'")
#                             else:
#                                 print(f"✔ הטקסט נכתב בהצלחה בריבוע: {rect}")
#                         else:
#                             print(f"⚠ המלבן ריק או לא תקין: {rect}")

#     base, ext = os.path.splitext(file_path)
#     output_path = f"{base}_processed{ext}"
    
#     try:
#         doc.save(output_path)
#         print("Processed file saved at:", output_path)
#     except Exception as e:
#         print("Error saving file:", e)

#     doc.close()
#     return output_path, variables_not_found

# @pdf_documents_bp.route('/pdf/process/<sql_id>', methods=['POST'])
# def process_pdf_route(sql_id):
#     data = request.get_json()
#     file_path = data.get("file_path")
#     if not file_path or not file_path.endswith(".pdf"):
#         return jsonify({"message": "יש לספק נתיב לקובץ PDF תקני"}), 400

#     try:
#         output_path, missing_vars = process_pdf(file_path, sql_id)
#         return send_file(
#             output_path,
#             as_attachment=True,
#             download_name=os.path.basename(output_path),
#             mimetype="application/pdf"
#         )
#     except Exception as e:
#         return jsonify({"message": f"שגיאה בעיבוד PDF: {str(e)}"}), 500
# ... ייבוא ספריות ...
import os
import re
from flask import Blueprint, request, jsonify, send_file
from pymongo import MongoClient
import fitz  # PyMuPDF
import arabic_reshaper
from bidi.algorithm import get_display
from ..database import get_db_connection

pdf_documents_bp = Blueprint('pdf_documents', __name__)

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["Manage_Files_DB"]
values_collection = mongo_db["Customers_Fields"]
conn = get_db_connection()
cursor = conn.cursor()

VARIABLE_REGEX = r"\-\-(.*?)\-\-"

def extract_values(sql_id):
    return values_collection.find_one({"sql_id": sql_id}) or {}

# פונקציה לעיבוד טקסט עברי
def prepare_hebrew_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def process_pdf(file_path, sql_id):
    print("Starting PDF processing...")
    doc = fitz.open(file_path)
    values = extract_values(sql_id)
    variables_not_found = []

    # טען גופן עברי מתוך fonts/ ליד routes/
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansHebrewRegular.ttf'))
    print("מחפש את הגופן בנתיב:", font_path)
    print("הקובץ קיים:", os.path.exists(font_path))

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"הגופן לא נמצא בנתיב: {font_path}. ודאי שהקובץ NotoSansHebrewRegular.ttf קיים בתיקיית fonts")

    print("font_path:", font_path)

    try:
        # שינוי בטעינת הגופן
        font_name = "NotoSansHebrew"
        doc.add_font(fontfile=font_path, fontname=font_name)
        print(f"Font loaded: {font_name}")
    except Exception as e:
        raise Exception(f"שגיאה בטעינת הגופן: {str(e)}")

    for page_num, page in enumerate(doc, start=1):
        print(f"\n--- Processing page {page_num} ---")
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    matches = list(re.finditer(VARIABLE_REGEX, text))
                    if not matches:
                        continue

                    new_text = text
                    for match in matches:
                        full_match = match.group(0)
                        inner = match.group(1)
                        parts = [p.strip() for p in inner.split(',')]
                        if len(parts) < 5:
                            continue
                        var_name, var_type, var_len, var_required, var_description = parts[:5]
                        value = values.get(var_name)

                        if value:
                            replacement = str(value)
                        else:
                            if var_required == "*":
                                replacement = "_____"  # חובה אך חסר
                                variables_not_found.append(var_name)
                            else:
                                replacement = ""

                        new_text = new_text.replace(full_match, replacement)

                    if new_text != text:
                        rect = fitz.Rect(span["bbox"])
                        rect.y1 = rect.y0 + 100000  # גובה מלאכותי כדי לכלול טקסט רב שורה

                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        if rect.width > 0 and rect.height > 0:
                            hebrew_text = prepare_hebrew_text(new_text)
                            ok = page.insert_textbox(
                                rect,
                                hebrew_text,
                                fontname=font_name,
                                fontsize=span["size"],
                                color=(0, 0, 0),
                                align=2,  # ימין
                                overlay=True,
                            )
                            if ok == 0:
                                print(f"⚠ לא הצליח לכתוב טקסט בתוך הריבוע: {rect}, טקסט: '{hebrew_text}'")
                            else:
                                print(f"✔ הטקסט נכתב בהצלחה בריבוע: {rect}")
                        else:
                            print(f"⚠ מלבן לא תקין: {rect}")

    base, ext = os.path.splitext(file_path)
    output_path = f"{base}_processed{ext}"
    
    try:
        doc.save(output_path)
        print("Processed file saved at:", output_path)
    except Exception as e:
        raise Exception(f"שגיאה בשמירת הקובץ: {e}")

    doc.close()
    return output_path, variables_not_found

@pdf_documents_bp.route('/pdf/process/<sql_id>', methods=['POST'])
def process_pdf_route(sql_id):
    try:
        data = request.get_json()
        file_path = data.get("file_path")
        if not file_path or not file_path.endswith(".pdf"):
            return jsonify({"message": "יש לספק נתיב לקובץ PDF תקני"}), 400

        output_path, missing_vars = process_pdf(file_path, sql_id)
        return send_file(
            output_path,
            as_attachment=True,
            download_name=os.path.basename(output_path),
            mimetype="application/pdf"
        )
    except Exception as e:
        print("שגיאה במהלך עיבוד PDF:", str(e))
        return jsonify({"error": str(e)}), 500
