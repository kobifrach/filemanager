from flask import Blueprint, request, jsonify
import easyocr
import os

# יצירת בלופרינט
ocr_bp = Blueprint('ocr', __name__)

# אתחול של EasyOCR reader
reader = easyocr.Reader(['he', 'en'])  # הוספנו עברית ואנגלית, אפשר להוסיף עוד שפות

@ocr_bp.route('/ocr', methods=['POST'])
def ocr():
    # אם לא הועלה קובץ
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    # אם לא נבחר קובץ
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # שמירה של הקובץ הזמני
    upload_folder = os.path.join(os.getcwd(), 'uploads')  # תיקיית ההעלאה
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # יצירת התיקיה אם היא לא קיימת
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    # ביצוע OCR על התמונה
    try:
        result = reader.readtext(filepath)
        text = "\n".join([item[1] for item in result])  # הוצאת הטקסט בלבד
        os.remove(filepath)  # מחיקת הקובץ אחרי עיבוד
        return jsonify({"text": text}), 200
    except Exception as e:
        os.remove(filepath)
        return jsonify({"error": str(e)}), 500
