# import os
# import re
# import pyodbc
# import shutil
# import uuid
# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from docx import Document
# from docx.shared import Pt
# import win32com.client
# from docx.enum.text import WD_COLOR_INDEX
# from ..database import get_db_connection
# from datetime import datetime
# from collections import defaultdict

# # ---------- General Definitions ----------
# documents_bp = Blueprint('documents', __name__)

# # Connect to MongoDB
# mongo_client = MongoClient("mongodb://localhost:27017")
# mongo_db = mongo_client["Manage_Files_DB"]
# values_collection = mongo_db["Customers_Fields"]

# conn = get_db_connection()
# cursor = conn.cursor()

# VARIABLE_REGEX = r"\{\{(.*?)\}\}"

# # ---------- Functions ----------


# def convert_doc_to_docx(input_path):#ממיר קובץ doc ל-docx
#     print("convert_doc_to_docx called with input_path:", input_path)
#     try:
#         word = win32com.client.Dispatch("Word.Application")
#         doc = word.Documents.Open(input_path)
#         output_path = os.path.splitext(input_path)[0] + ".docx"
#         doc.SaveAs(output_path, FileFormat=16)  # 16 is docx format
#         doc.Close()
#         word.Quit()
#         return output_path
#     except Exception as e:
#         print("שגיאה בהמרה ל-docx:", e)
#         return None

# def process_docx(path, sql_id):#עיבוד קובץ docx
#     print("process_docx called with path:", path, "sql_id:", sql_id)
#     values = values_collection.find_one({"sql_id": sql_id}) or {}
#     # print(type(values)) 
#     print(f"values: {values}")  # הדפסת התוכן של values

#     # grouped_values = group_fields_by_prefix(values)
#     # grouped_data = combine_grouped_data(grouped_values)
#     doc = Document(path)
#     variables_not_found = []
#     # Body paragraphs
#     process_paragraphs(doc.paragraphs, variables_not_found, sql_id, values)
#     # Tables
#     for table in doc.tables:
#         for row in table.rows:
#             for cell in row.cells:
#                 process_paragraphs(cell.paragraphs, variables_not_found, sql_id, values)

#     # Headers and footers
#     for section in doc.sections:
#         process_paragraphs(section.header.paragraphs, variables_not_found, sql_id, values)
#         process_paragraphs(section.footer.paragraphs, variables_not_found, sql_id, values)
#     # Save document

#     dir_path = os.path.dirname(path)
#     filename_wo_ext = os.path.splitext(os.path.basename(path))[0]
#     output_path = os.path.join(dir_path, f"{filename_wo_ext} טופל.docx")
#     doc.save(output_path)

#     print("✅ קובץ נשמר כ:", output_path)
#     if variables_not_found:
#         print("⚠️ משתנים שלא נמצאו:", variables_not_found)
#     return variables_not_found


# # def group_fields_by_prefix(data):#grouping fields by prefix
# #     print("group_fields_by_prefix called with data")
# #     grouped = defaultdict(dict)
# #     # print("data:", data)

# #     for field, values in data.items():
# #         # print("field:", field)  # הדפסת התוכן של field
# #         # print("values:", values)  # הדפסת התוכן של values   
# #         if field == 'sql_id' or field == '_id':
# #             continue  # מתעלמים מהשדה הזה

# #         # חילוץ התחילית מהשדה (הכל עד התו הראשון של '_' כולל)
# #         if "_" in field and len(values) > 1:
# #             # print("field:", field)  # הדפסת התוכן של field
# #             prefix, suffix = field.split("_", 1)
# #             # print("prefix:", prefix)  # הדפסת התוכן של prefix
# #             group = prefix  # לדוגמה: 'buyer', 'seller', 'property'
# #         else:
# #             continue  # אם אין _, אין התחלה תקפה

# #         grouped[group][field] = values
# #     print("Grouped fields:", grouped)  # הדפסת התוכן של grouped
# #     return grouped


# # def combine_grouped_data(grouped):
# #     print("combine_grouped_data called with grouped:", grouped)
# #     output = []

# #     for group_name, fields in grouped.items():
# #         # לבדוק אם יש שדה שיש לו יותר מערך אחד
# #         needs_zip = any(isinstance(v, list) and len(v) > 1 for v in fields.values())

# #         if not needs_zip:
# #             # אם אין שדה עם מערך גדול מ-1, לא קיבץ את הקבוצה
# #             output.append(" ".join([str(v) for v in fields.values()]))
# #             continue  # לדלג על קבוצה שאין בה שדות עם יותר מערך אחד

# #         # להכין רשימות לכל שדה
# #         field_lists = []
# #         max_length = max(len(v) for v in fields.values() if isinstance(v, list))
        
# #         for field, values in fields.items():
# #             if isinstance(values, list):
# #                 field_lists.append(values)
# #             else:
# #                 field_lists.append([values] * max_length)  # לשכפל ערכים בודדים

# #         zipped = zip(*field_lists)
# #         group_lines = [" ".join(map(str, entry)) for entry in zipped]
# #         output.append(", ".join(group_lines))

# #     print("Combined data:", output)
# #     return output


# def process_paragraphs(paragraphs, variables_not_found, sql_id, values):
#     print("process_paragraphs called")
#     for para in paragraphs:
#         matches = list(re.finditer(VARIABLE_REGEX, para.text))
#         if not matches:
#             continue

#         original_text = para.text
#         para.clear()
#         last_end = 0

#         for match in matches:
#             start, end = match.span()
#             var_text = match.group(1)
#             parts = var_text.split(',')

#             before = original_text[last_end:start]
#             if before:
#                 run = para.add_run(before)
#                 run.font.name = 'Arial'
#                 run.font.size = Pt(12)

#             if len(parts) < 5:
#                 run = para.add_run(match.group(0))
#                 run.font.name = 'Arial'
#                 run.font.size = Pt(12)
#                 last_end = end
#                 continue


#             var_name, var_type, var_len, var_required, var_description = [p.strip() for p in parts]

#             # Check if field exists in SQL, if not insert it
#             cursor.execute("SELECT COUNT(*) FROM Fields WHERE name = ?", (var_name,))
#             if cursor.fetchone()[0] == 0:
#                 cursor.execute("INSERT INTO Fields (name, type, length, required, description) VALUES (?, ?, ?, ?, ?)",
#                                (var_name, var_type, int(var_len), int(var_required == '*'), var_description))
#                 cursor.connection.commit()

#             # Fetch value from MongoDB
#             # value = values.get(var_name)
#             value = values.get(var_name) if isinstance(values, dict) else values

            
#             field_errors = []

#             if isinstance(value, list):# Check if the value is an array and handle it accordingly                
#                 for item in value:  # for each item in the array:
#                     # Validate and insert the item as a separate value in the document
#                     sql_type = f"{var_type}({var_len})" if var_len else var_type
#                     validated_value = validate_value_by_type(item, sql_type, field_name=var_name, errors=field_errors)

#                     if validated_value is not None and validated_value != "_____":
#                         run = para.add_run(str(validated_value)+" ")
#                         run.font.name = 'Arial'
#                         run.font.size = Pt(12)
#                     else:
#                         variables_not_found.append(var_name)
#                         run = para.add_run("_____")
#                         run.font.highlight_color = WD_COLOR_INDEX.YELLOW
#                         run.font.name = 'Arial'
#                         run.font.size = Pt(12)
#             else:  # אם הערך הוא לא מערך, תטפל בו כרגיל
#                 sql_type = f"{var_type}({var_len})" if var_len else var_type
#                 validated_value = validate_value_by_type(value, sql_type, field_name=var_name, errors=field_errors)

#                 if validated_value is not None and validated_value != "_____":
#                     run = para.add_run(str(validated_value))
#                     run.font.name = 'Arial'
#                     run.font.size = Pt(12)
#                 else:
#                     variables_not_found.append(var_name)
#                     run = para.add_run("_____")
#                     run.font.highlight_color = WD_COLOR_INDEX.YELLOW
#                     run.font.name = 'Arial'
#                     run.font.size = Pt(12) 

#             last_end = end

#         after = original_text[last_end:]
#         if after:
#             run = para.add_run(after)
#             run.font.name = 'Arial'
#             run.font.size = Pt(12)

# # def process_paragraphs(paragraphs, variables_not_found, sql_id, values, group_prefix):
# #     print("process_paragraphs called")

# #     for para in paragraphs:
# #         matches = list(re.finditer(VARIABLE_REGEX, para.text))
# #         if not matches:
# #             continue

# #         original_text = para.text
# #         para.clear()
# #         last_end = 0
# #         variables_to_fill = []  # לאסוף את המשתנים שקשורים לקבוצה
# #         variables_other_than_group = []  # לאסוף את יתר המשתנים

# #         # תהליך של זיהוי כל המשתנים שמתחילים בקידומת של הקבוצה או לא
# #         for match in matches:
# #             start, end = match.span()
# #             var_text = match.group(1)
# #             parts = var_text.split(',')

# #             before = original_text[last_end:start]
# #             if before:
# #                 run = para.add_run(before)
# #                 run.font.name = 'Arial'
# #                 run.font.size = Pt(12)

# #             if len(parts) < 5:
# #                 run = para.add_run(match.group(0))
# #                 run.font.name = 'Arial'
# #                 run.font.size = Pt(12)
# #                 last_end = end
# #                 continue

# #             var_name, var_type, var_len, var_required, var_description = [p.strip() for p in parts]

# #             # אם המשתנה שייך לקבוצה, הוסף אותו לרשימה
# #             if var_name.startswith(group_prefix):
# #                 variables_to_fill.append((var_name, var_type, var_len, var_required, var_description, start, end))
# #             else:
# #                 variables_other_than_group.append((var_name, var_type, var_len, var_required, var_description, start, end))

# #             last_end = end
        
# #         after = original_text[last_end:]
# #         if after:
# #             run = para.add_run(after)
# #             run.font.name = 'Arial'
# #             run.font.size = Pt(12)

# #         # עכשיו נמלא את כל המשתנים שקשורים לקבוצה
# #         if variables_to_fill:
# #             found_values = {}  # לאחסן ערכים שהוזנו כדי למנוע כפילויות
# #             for var_name, var_type, var_len, var_required, var_description, start, end in variables_to_fill:
# #                 # אם הערך כבר הוזן, הצב אותו
# #                 if var_name in found_values:
# #                     value = found_values[var_name]
# #                 else:
# #                     # בדוק אם השדה קיים ב-SQL
# #                     cursor.execute("SELECT COUNT(*) FROM Fields WHERE name = ?", (var_name,))
# #                     if cursor.fetchone()[0] == 0:
# #                         cursor.execute("INSERT INTO Fields (name, type, length, required, description) VALUES (?, ?, ?, ?, ?)",
# #                                        (var_name, var_type, int(var_len), int(var_required == '*'), var_description))
# #                         cursor.connection.commit()

# #                     value = values.get(var_name) if isinstance(values, dict) else values
# #                     found_values[var_name] = value  # שמור את הערך שהוזן

# #                 # הצב את הערך
# #                 run = para.add_run(str(value))
# #                 run.font.name = 'Arial'
# #                 run.font.size = Pt(12)

# #                 # עדכן את ה-last_end
# #                 last_end = end

# #         # עכשיו נמלא את כל המשתנים האחרים (שאינם שייכים לקבוצה) עם ערכים ממונגוDB
# #         if variables_other_than_group:
# #             for var_name, var_type, var_len, var_required, var_description, start, end in variables_other_than_group:
# #                 # בצע שאילתא ממונגוDB כדי לקבל את הערך המתאים
# #                 mongo_value = mongo_db.get(var_name)  # לדוגמה, נתון שמחזיר ערך מהמונגו לפי שם המשתנה
                
# #                 # אם לא נמצא ערך במונגו, השתמש בערך ברירת מחדל או אחר
# #                 if mongo_value is None:
# #                     mongo_value = '_____'
# #                     run = para.add_run(mongo_value)
# #                     run.font.name = 'Arial'
# #                     run.font.size = Pt(12)
# #                     run.font.highlight_color = WD_COLOR_INDEX.YELLOW

# #                 # הצב את הערך
# #                 else:
# #                     run = para.add_run(str(mongo_value))
# #                     run.font.name = 'Arial'
# #                     run.font.size = Pt(12)

# #                 # עדכן את ה-last_end
# #                 last_end = end

# #         # עכשיו נמלא את כל ה-after לאחרון
# #         if after:
# #             run = para.add_run(after)
# #             run.font.name = 'Arial'
# #             run.font.size = Pt(12)


# def validate_value_by_type(value, sql_type, field_name=None, errors=None):    
#     print("validate_value_by_type called with value:", value, "sql_type:", sql_type, "field_name:", field_name)
#     if 'id' in (field_name or '').lower():
#         print("ID field found")
#         if not str(value).isdigit():
#             # print("error in ID field")
#             msg = f"שגיאה בשדה '{field_name or 'שדה'}': ערך '{value}' לא מספרי (שדה ID חייב להכיל רק ספרות)"
#             if errors is not None:
#                 errors.append(msg)
#             # אם הערך לא מספרי, תן ערך ריק
#             return "_____"
        

#     type_match = re.match(r"([a-zA-Z]+)\(?(\d*)\)?", sql_type.strip())
#     if not type_match:
#         return value

#     base_type = type_match.group(1).lower()
#     length_str = type_match.group(2)
#     max_length = int(length_str) if length_str.isdigit() else None

#     try:
#         if base_type in ['varchar', 'char', 'nchar', 'nvarchar']:
#             str_value = str(value)
#             if max_length and len(str_value) > max_length:
#                 return str_value[:max_length]
#             return str_value

#         elif base_type in ['int', 'bigint', 'smallint']:
#             print("int value")
#             return int(value)

#         elif base_type in ['float', 'real', 'decimal', 'numeric']:
#             return float(value)

#         elif base_type in ['bit']:
#             return bool(int(value))

#         elif base_type in ['date', 'datetime', 'smalldatetime']:
#             return datetime.fromisoformat(str(value))

#         else:
#             return str(value)

#     except Exception as e:
#         msg = f"שגיאה בשדה '{field_name or 'שדה'}': ערך לא תקין '{value}' לסוג '{sql_type}'"
#         if errors is not None:
#             errors.append(msg)
#             return "_____"
#         else:
#             return "_____"
#             # raise ValueError(msg)


# # ---------- Flask Routes ----------

# @documents_bp.route('/process/<sql_id>', methods=['POST'])
# def process_document_route(sql_id):
#     data = request.get_json()
#     file_path = data.get("file_path")
#     if not file_path:
#         return jsonify({"message": "יש לספק נתיב לקובץ"}), 400

#     try:
#         if file_path.endswith(".doc"):
#             file_path = convert_doc_to_docx(file_path)
#             if not file_path:
#                 return jsonify({"message": "שגיאה בהמרת קובץ ל-docx"}), 500

#         missing_vars = process_docx(file_path, sql_id)
#         # missing_vars = process_docx_advanced(file_path, sql_id)
#         return jsonify({
#             "message": "עיבוד הושלם",
#             "missing_variables": missing_vars
#         }), 200
#     except Exception as e:
#         return jsonify({"message": f"שגיאה: {str(e)}"}), 500
#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)
  