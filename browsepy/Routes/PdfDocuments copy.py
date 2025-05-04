# import os
# import re
# import pdfplumber
# from reportlab.pdfgen import canvas
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from bidi.algorithm import get_display
# import arabic_reshaper
# from io import BytesIO
# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from datetime import datetime
# from ..database import get_db_connection
# import fitz  # PyMuPDF

# # ---------- הגדרות כלליות ----------
# Pdf_documents_bp = Blueprint('Pdf_documents', __name__)

# # חיבור ל-MongoDB
# mongo_client = MongoClient("mongodb://localhost:27017")
# mongo_db = mongo_client["Manage_Files_DB"]
# values_collection = mongo_db["Customers_Fields"]

# # חיבור ל-SQL Server
# conn = get_db_connection()
# cursor = conn.cursor()

# VARIABLE_REGEX = r"\{\{\s*([^\{\}\s]+)\s*\}\}"

# # # ---------- פונקציות ----------

# # def validate_value_by_type(value, sql_type, field_name=None, errors=None):
# #     if 'id' in (field_name or '').lower():
# #         if not str(value).isdigit():
# #             msg = f"שגיאה בשדה '{field_name or 'שדה'}': ערך '{value}' לא מספרי (שדה ID חייב להכיל רק ספרות)"
# #             if errors is not None:
# #                 errors.append(msg)
# #             return "_____"

# #     type_match = re.match(r"([a-zA-Z]+)\(?(\d*)\)?", sql_type.strip())
# #     if not type_match:
# #         return value

# #     base_type = type_match.group(1).lower()
# #     length_str = type_match.group(2)
# #     max_length = int(length_str) if length_str.isdigit() else None

# #     try:
# #         if base_type in ['varchar', 'char', 'nchar', 'nvarchar']:
# #             str_value = str(value)
# #             if max_length and len(str_value) > max_length:
# #                 return str_value[:max_length]
# #             return str_value
# #         elif base_type in ['int', 'bigint', 'smallint']:
# #             return int(value)
# #         elif base_type in ['float', 'real', 'decimal', 'numeric']:
# #             return float(value)
# #         elif base_type in ['bit']:
# #             return bool(int(value))
# #         elif base_type in ['date', 'datetime', 'smalldatetime']:
# #             return datetime.fromisoformat(str(value))
# #         else:
# #             return str(value)
# #     except Exception:
# #         msg = f"שגיאה בשדה '{field_name or 'שדה'}': ערך לא תקין '{value}' לסוג '{sql_type}'"
# #         if errors is not None:
# #             errors.append(msg)
# #         return "_____"



# # # def process_pdf_pymupdf(pdf_path, sql_id, cursor, values_collection):
# # #     doc = fitz.open(pdf_path)
# # #     print("doc:", doc)
# # #     print("pdf_path:", pdf_path)
# # #     values = values_collection.find_one({"sql_id": sql_id}) or {}
# # #     print("values:", values)
# # #     variables_not_found = []

# # #     VARIABLE_REGEX = r"\{\{\s*([^\{\}\s]+)\s*\}\}"

# # #     for page in doc:
# # #         text_instances = page.get_text("blocks")
# # #         for b in text_instances:
# # #             block_text = b[4]
# # #             matches = list(re.finditer(VARIABLE_REGEX, block_text))
# # #             print("🔍 block_text:", block_text)
# # #             print("🔎 matches:", matches)
# # #             if not matches:
# # #                 continue

# # #             for match in matches:
# # #                 full_match = match.group(0)
# # #                 inner = match.group(1)
# # #                 parts = [p.strip() for p in inner.split(',')]
# # #                 if len(parts) < 5:
# # #                     continue

# # #                 var_name, var_type, var_len, var_required, var_description = parts

# # #                 cursor.execute("SELECT COUNT(*) FROM Fields WHERE name = ?", (var_name,))
# # #                 if cursor.fetchone()[0] == 0:
# # #                     cursor.execute("INSERT INTO Fields (name, type, length, required, description) VALUES (?, ?, ?, ?, ?)",
# # #                                    (var_name, var_type, int(var_len), int(var_required == '*'), var_description))
# # #                     cursor.connection.commit()

# # #                 value = values.get(var_name)
# # #                 errors = []
# # #                 if value is not None:
# # #                     sql_type = f"{var_type}({var_len})" if var_len else var_type
# # #                     validated = validate_value_by_type(value, sql_type, var_name, errors)
# # #                 else:
# # #                     validated = "_____"
# # #                     variables_not_found.append(var_name)

# # #                 rects = page.search_for(full_match)
# # #                 for rect in rects:
# # #                     page.add_redact_annot(rect, fill=(1, 1, 1))  # מוחק ברקע לבן
# # #                 page.apply_redactions()

# # #                 for rect in rects:
# # #                     page.insert_textbox(rect, str(validated), fontsize=11, fontname="helv", align=1)

# # #     output_path = pdf_path.replace(".pdf", "_מעודכן.pdf")
# # #     doc.save(output_path)
# # #     doc.close()
# # #     return output_path, variables_not_found

# # def extract_text_from_pdf(pdf_path):
# #     full_text = ""  # הגדרת המשתנה לאיסוף הטקסט
# #     with pdfplumber.open(pdf_path) as pdf:
# #         for i, page in enumerate(pdf.pages):
# #             text = page.extract_text()
# #             full_text += text  # מוסיפים את הטקסט של כל עמוד למשתנה
# #             print(f"\n--- עמוד {i+1} ---\n{text}")
# #     return full_text
    


# # def clean_variable_format(line):
# #     # מסיר רווחים מיותרים לפני ואחרי הסוגריים
# #     line = re.sub(r"\{\{\s*\}\}", "_____")  # כאשר יש {{ }} ריק, ממלא עם "_____"
# #     line = re.sub(r"\{\{\s*", "{{", line)  # הסרת רווחים לפני {{
# #     line = re.sub(r"\s*\}\}", "}}", line)  # הסרת רווחים אחרי }}
# #     return line


# # def process_pdf_text(pdf_text, cursor, variables_not_found, sql_id, values):
# #     lines = pdf_text.split('\n')
# #     processed_lines = []

# #     for line in lines:
# #         matches = list(re.finditer(VARIABLE_REGEX, line))
# #         print("🔍 שורה מקורית:", line)
# #         print("🔎 משתנים שנמצאו:", matches)
# #         if not matches:
# #             processed_lines.append(line)
# #             continue

# #         original_text = line
# #         last_end = 0
# #         processed_text = ""

# #         for match in matches:
# #             start, end = match.span()
# #             var_text = match.group(1)
# #             parts = var_text.split(',')

# #             before = original_text[last_end:start]
# #             if before:
# #                 processed_text += re.sub(r'\s+', ' ', before)

# #             if len(parts) < 5:
# #                 processed_text += match.group(0)
# #                 last_end = end
# #                 continue

# #             var_name, var_type, var_len, var_required, var_description = [p.strip() for p in parts]

# #             cursor.execute("SELECT COUNT(*) FROM Fields WHERE name = ?", (var_name,))
# #             if cursor.fetchone()[0] == 0:
# #                 cursor.execute("INSERT INTO Fields (name, type, length, required, description) VALUES (?, ?, ?, ?, ?)",
# #                                (var_name, var_type, int(var_len), int(var_required == '*'), var_description))
# #                 cursor.connection.commit()

# #             value = values.get(var_name)
# #             field_errors = []

# #             if value is not None:
# #                 sql_type = f"{var_type}({var_len})" if var_len else var_type
# #                 validated_value = validate_value_by_type(value, sql_type, field_name=var_name, errors=field_errors)

# #                 if validated_value != "_____":
# #                     processed_text += str(validated_value)
# #                 else:
# #                     variables_not_found.append(var_name)
# #                     processed_text += "_____"
# #             else:
# #                 variables_not_found.append(var_name)
# #                 processed_text += "_____"
# #             last_end = end
# #         after = original_text[last_end:]
# #         if after:
# #             processed_text += re.sub(r'\s+', ' ', after)

# #         processed_lines.append(processed_text)

# #     return processed_lines, variables_not_found

# # def process_pdf(path, sql_id):
# #     values = values_collection.find_one({"sql_id": sql_id}) or {}

# #     pdf_text = extract_text_from_pdf(path)
# #     variables_not_found = []

# #     processed_lines, variables_not_found = process_pdf_text(pdf_text, cursor, variables_not_found, sql_id, values)

# #     dir_path = os.path.dirname(path)
# #     filename_wo_ext = os.path.splitext(os.path.basename(path))[0]
# #     output_path = os.path.join(dir_path, f"{filename_wo_ext} טופל.pdf")

# #     # font_path = "../fonts/NotoSansHebrew-Regular.ttf"
# #     font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSansHebrew-Regular.ttf"))
# #     if not os.path.exists(font_path):
# #         raise FileNotFoundError(f"Font file not found: {font_path}")
# #     print("📁 font_path:", font_path)
# #     pdfmetrics.registerFont(TTFont("HebrewFont", font_path))

# #     pdf_output = BytesIO()
# #     c = canvas.Canvas(pdf_output, pagesize=(595, 842))
# #     c.setFont("HebrewFont", 12)
# #     y_position = 800

# #     for line in processed_lines:
# #         bidi_text = get_display(line)

# #         if y_position <= 50:
# #             c.showPage()
# #             c.setFont("HebrewFont", 12)
# #             y_position = 800
# #         c.drawRightString(540, y_position, bidi_text)
# #         y_position -= 15
        
# #     c.save()

# #     with open(output_path, "wb") as f:
# #         f.write(pdf_output.getvalue())

# #     print("✅ קובץ PDF נשמר כ:", output_path)
# #     if variables_not_found:
# #         print("⚠️ משתנים שלא נמצאו:", variables_not_found)
# #     return variables_not_found



# # # ---------- Flask Route ----------

# # @Pdf_documents_bp.route('/process_pdf/<sql_id>', methods=['POST'])
# # def process_pdf_route(sql_id):
# #     data = request.get_json()
# #     print("📁 data:", data  )
# #     file_path = data.get("file_path")
# #     if not os.path.exists(file_path):
# #         return jsonify({"message": "קובץ לא נמצא"}), 404
    
# #     if not file_path:
# #         return jsonify({"message": "יש לספק נתיב לקובץ"}), 400
# #     # print("📁 file_path שהתקבל:", file_path)
# #     # print("📁 os.path.exists(file_path):", os.path.exists(file_path))
    
# #     try:
# #         missing_vars = process_pdf(file_path, sql_id)
# #         return jsonify({
# #             "message": "עיבוד הושלם",
# #             "missing_variables": missing_vars
# #         }), 200
# #     except Exception as e:
# #         return jsonify({"message": f"שגיאה: {str(e)}"}), 500
    




# @app.route('/process_pdf/<sql_id>', methods=['POST'])
# def process_pdf_route(sql_id):
#     data = request.get_json()
#     file_path = data.get("file_path")

#     if not file_path:
#         return jsonify({"message": "יש לספק נתיב לקובץ"}), 400

#     try:
#         # הנחתה שהקובץ בפורמט PDF
#         missing_vars = process_pdf(file_path, sql_id, cursor, values)
#         return jsonify({
#             "message": "עיבוד הושלם",
#             "missing_variables": missing_vars
#         }), 200
#     except Exception as e:
#         return jsonify({"message": f"שגיאה: {str(e)}"}), 500
#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)

# if __name__ == "__main__":
#     app.run(debug=True)