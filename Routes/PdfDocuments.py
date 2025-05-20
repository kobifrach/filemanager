# import os
# import re
# from flask import Blueprint, request, jsonify, send_file
# from pymongo import MongoClient
# import fitz  # PyMuPDF
# import arabic_reshaper
# from bidi.algorithm import get_display
# from ..database import get_db_connection
# from browsepy.Utils.decorators import safe_route

# pdf_documents_bp = Blueprint('pdf_documents', __name__)

# mongo_client = MongoClient("mongodb://localhost:27017")
# mongo_db = mongo_client["Manage_Files_DB"]
# values_collection = mongo_db["Customers_Fields"]
# conn = get_db_connection()
# cursor = conn.cursor()

# # VARIABLE_REGEX = r"\-\-(.*?)\-\-"
# # VARIABLE_REGEX = r"\-\-\s*(.*?)\s*\-\-"
# VARIABLE_REGEX = r"\-\-\s*([^,\-\s]+(?:\s*,\s*[^,\-\s]+)*)\s*\-\-"


# def extract_values(sql_id):
#     return values_collection.find_one({"sql_id": sql_id}) or {}

# # פונקציה לעיבוד טקסט עברי
# def prepare_hebrew_text(text):
#     reshaped_text = arabic_reshaper.reshape(text)
#     bidi_text = get_display(reshaped_text)
#     return bidi_text

# def extract_all_variables(doc):
#     print("123")
#     full_text = ""
#     for page in doc:
#         text = page.get_text("text")
#         full_text += text.replace("\n", " ")
#     matches = re.findall(VARIABLE_REGEX, full_text)
#     return matches

# def process_pdf(file_path, sql_id):
#     doc = fitz.open(file_path)
#     matches1 = extract_all_variables(doc)
#     print("Matches found:", matches1)
#     # for font in fitz.getFontNames():
#     #     print(font)
#     print("Starting PDF processing...")
#     values = extract_values(sql_id)
#     variables_not_found = []


    

#     # נתיב הגופן
#     # font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansHebrewRegular.ttf'))

#     # font_name = "NotoSansHebrew"

#     # טען את הגופן
#     # try:
#     #     doc.add_font(fontfile=font_path, fontname=font_name, set_simple=True)
#     #     print(f"Font {font_name} loaded successfully")
#     # except Exception as e:
#     #     print(f"Error loading font {font_name}: {e}")

#     for page_num, page in enumerate(doc, start=1):
#         print(f"\n--- Processing page {page_num} ---")
#         blocks = page.get_text("dict")["blocks"]
#         for b in blocks:
#             if "lines" not in b:
#                 continue
#             for line in b["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"]
#                     # matches = list(re.finditer(VARIABLE_REGEX, text))
#                     matches = list(re.finditer("--", text))
                    
#                     if not matches:
#                         print("No matches found in this span")
#                         continue
#                     print("Matches found:", matches)

#                     new_text = text

#                     for match in matches:
#                         print("4444444444444444444444444444444444444444444")
#                         print(match)
#                         full_match = match.group(0)
#                         print("full_match   ",full_match)
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
#                         rect.y1 = rect.y0 + 50  # גובה מלאכותי
#                         print(rect)

#                         page.add_redact_annot(rect, fill=(1, 1, 1))
#                         page.apply_redactions()

#                         if rect.width > 0 and rect.height > 0:
#                             hebrew_text = prepare_hebrew_text(new_text)
#                             fontsize1 = span["size"]-3
#                             ok = page.insert_textbox(
#                                 rect,
#                                 hebrew_text,
#                                 # fontname=font_name,  # השתמש בגופן העברי
#                                 fontname = "Helvetica",
#                                 fontsize=fontsize1,#span["size"],
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
# # ... ייבוא ספריות ...




# # import os
# # import re
# # import fitz  # PyMuPDF
# # from reportlab.lib.pagesizes import letter
# # from reportlab.pdfgen import canvas
# # from io import BytesIO
# # from pymongo import MongoClient
# # from bidi.algorithm import get_display
# # import arabic_reshaper
# # from flask import Blueprint, request, jsonify, send_file
# # from ..database import get_db_connection

# # pdf_documents_bp = Blueprint('pdf_documents', __name__)

# # # חיבור לבסיס הנתונים של MongoDB
# # mongo_client = MongoClient("mongodb://localhost:27017")
# # mongo_db = mongo_client["Manage_Files_DB"]
# # values_collection = mongo_db["Customers_Fields"]
# # conn = get_db_connection()
# # cursor = conn.cursor()

# # VARIABLE_REGEX = r"\-\-(.*?)\-\-"

# # # פונקציה לקבלת ערכים מהמאגר
# # def extract_values(sql_id):
# #     return values_collection.find_one({"sql_id": sql_id}) or {}

# # # פונקציה לעיבוד טקסט עברי
# # def prepare_hebrew_text(text):
# #     reshaped_text = arabic_reshaper.reshape(text)
# #     bidi_text = get_display(reshaped_text)
# #     return bidi_text

# # def process_pdf(file_path, sql_id):
# #     fonts = fitz.getFontNames()
# #     for font in fonts():
# #         print(font)
# #     print("Starting PDF processing...")
# #     doc = fitz.open(file_path)
# #     values = extract_values(sql_id)
# #     variables_not_found = []

# #     # נתיב הגופן
# #     font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansHebrewRegular.ttf'))
# #     font_name = "NotoSansHebrew"

# #     # טען את הגופן למסמך
# #     try:
# #         font_name = "Arial"
# #         print(f"✔ גופן {font_name} נטען בהצלחה")
# #     except Exception as e:
# #         print(f"שגיאה בטעינת הגופן: {e}")
# #         raise

# #     for page_num, page in enumerate(doc, start=1):
# #         print(f"\n--- עיבוד עמוד {page_num} ---")
# #         blocks = page.get_text("dict")["blocks"]
# #         for b in blocks:
# #             if "lines" not in b:
# #                 continue
# #             for line in b["lines"]:
# #                 for span in line["spans"]:
# #                     text = span["text"]
# #                     matches = list(re.finditer(VARIABLE_REGEX, text))
# #                     if not matches:
# #                         continue

# #                     new_text = text
# #                     for match in matches:
# #                         full_match = match.group(0)
# #                         inner = match.group(1)
# #                         parts = [p.strip() for p in inner.split(',')]
# #                         if len(parts) < 5:
# #                             continue
# #                         var_name, var_type, var_len, var_required, var_description = parts[:5]
# #                         value = values.get(var_name)

# #                         if value:
# #                             replacement = str(value)
# #                         else:
# #                             if var_required == "*":
# #                                 replacement = "_____"  # חובה אך חסר
# #                                 variables_not_found.append(var_name)
# #                             else:
# #                                 replacement = ""

# #                         new_text = new_text.replace(full_match, replacement)

# #                     if new_text != text:
# #                         rect = fitz.Rect(span["bbox"])
# #                         page.add_redact_annot(rect, fill=(1, 1, 1))
# #                         page.apply_redactions()

# #                         if rect.width > 0 and rect.height > 0:
# #                             hebrew_text = prepare_hebrew_text(new_text)
# #                             ok = page.insert_textbox(
# #                                 rect,
# #                                 hebrew_text,
# #                                 fontname=font_name,
# #                                 fontsize=span["size"],
# #                                 color=(0, 0, 0),
# #                                 align=2,  # יישור לימין (RTL)
# #                                 overlay=True,
# #                             )
# #                             if ok == 0:
# #                                 print(f"⚠ לא הצליח להכניס טקסט לתוך הריבוע: {rect}")
# #                             else:
# #                                 print(f"✔ הטקסט '{hebrew_text}' הוכנס בהצלחה ל-{rect}")

# #     output_path = file_path.replace(".pdf", "-processed.pdf")
# #     doc.save(output_path)
# #     doc.close()
# #     print(f"✅ קובץ שמור: {output_path}")
# #     return output_path, variables_not_found


# # @pdf_documents_bp.route('/pdf/process/<sql_id>', methods=['POST'])
# # def process_pdf_route(sql_id):
# #     try:
        
# #         data = request.get_json()
# #         file_path = data.get("file_path")
# #         if not file_path or not file_path.endswith(".pdf"):
# #             return jsonify({"message": "יש לספק נתיב לקובץ PDF תקני"}), 400

# #         output_path, missing_vars = process_pdf(file_path, sql_id)
# #         return send_file(
# #             output_path,
# #             as_attachment=True,
# #             download_name=os.path.basename(output_path),
# #             mimetype="application/pdf"
# #         )
# #     except Exception as e:
# #         print("שגיאה במהלך עיבוד PDF:", str(e))
# #         return jsonify({"error": str(e)}), 500
