#נבדק, עובד מושלם


from flask import Blueprint, request, jsonify
from ..database import get_db_connection, execute_db_operation
import os

files_bp = Blueprint('files', __name__)  # יצירת Blueprint

# יצירת קובץ
@files_bp.route('/file', methods=['POST'])
def create_file():
    data = request.get_json()

    file_name = data.get('name')
    file_url = data.get('file_url')
    
    # אם אחד מהשדות חסר, מחזיר שגיאה
    if not file_name or not file_url:
        return jsonify({"message": "File name and file URL are required"}), 400
    
    # בדיקה אם יש סיומת בקובץ 
    file_type = data.get('file_type')  # אם לא סופק סוג קובץ, נבדוק את שם הקובץ
    
    if not file_type:  # אם לא נשלח סוג קובץ
        # בדוק אם יש סיומת בקובץ
        _, file_extension = os.path.splitext(file_name)
        if file_extension:  # אם יש סיומת
            file_type = file_extension.lstrip('.')  # מסיר את ה-'.' מהסיומת
        else:
            file_type = 'docx'  # ברירת מחדל אם אין סיומת
    
    # כאן מניחים שהנתיב לא כולל את שם הקובץ, כלומר file_url הוא הנתיב עד הקובץ
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Files (name, file_type, File_URL)
        VALUES (?, ?, ?)
    ''', (file_name, file_type, file_url))
    
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "File created successfully"}), 201



#קבלת כל הקבצים
@files_bp.route('/files', methods=['GET'])
def get_files():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Files')
        rows = cursor.fetchall()
        cursor.close()

        # אם אין קבצים, מחזירים מערך ריק
        if not rows:
            return jsonify([]), 200  # מערך ריק עם סטטוס 200 (הצלחה)

        # הצגת כל הקבצים עם כל השדות המעודכנים
        files = [{"id": row[0], "name": row[1], "file_type": row[2], "file_url": row[3]} for row in rows]
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching files", "error": str(e)}), 500



#קבלת קובץ ספציפי לפי ID
@files_bp.route('/file/<int:file_id>', methods=['GET'])
def get_file_by_id(file_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Files WHERE id = ?', (file_id,))
        row = cursor.fetchone()
        cursor.close()

        # אם לא נמצא קובץ עם ה-ID הזה, מחזירים הודעת שגיאה מתאימה
        if row is None:
            return jsonify({"message": f"File with ID {file_id} not found"}), 404

        # הצגת פרטי הקובץ
        file = {
            "id": row[0],
            "name": row[1],
            "file_type": row[2],
            "file_url": row[3]  # מחזירים גם את ה-URL של הקובץ
        }
        return jsonify(file), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching the file", "error": str(e)}), 500


# עדכון קובץ
@files_bp.route('/file/<int:id>', methods=['PUT'])
def update_file(id):
    data = request.get_json()
    
    # וולידציה של השדות
    name = data.get('name')
    file_type = data.get('file_type')
    file_url = data.get('file_url')

    # אם אחד מהשדות חסר, מחזירים שגיאה
    if not name or not file_url:
        return jsonify({"message": "File name and file URL are required"}), 400
    
    # אם לא נשלח סוג קובץ, נבדוק את שם הקובץ
    if not file_type:
        _, file_extension = os.path.splitext(name)
        if file_extension:
            file_type = file_extension.lstrip('.')
        else:
            file_type = 'docx'  # ברירת מחדל אם אין סיומת

    # עדכון הקובץ בבסיס הנתונים
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Files
        SET name = ?, file_type = ?, File_URL = ?
        WHERE id = ?
    ''', (name, file_type, file_url, id))
    conn.commit()
    cursor.close()

    return jsonify({"message": "File updated successfully"}), 200


#מחיקת קובץ
@files_bp.route('/file/<int:id>', methods=['DELETE'])
def delete_file(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Files WHERE id = ?', (id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "File deleted successfully"}), 200
