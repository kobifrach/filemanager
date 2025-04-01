from flask import Blueprint, request, jsonify
from ..database import get_db_connection

folders_bp = Blueprint('folders', __name__)  # יצירת Blueprint

# יצירת תיקייה
@folders_bp.route('/folder', methods=['POST'])
def create_folder():
    data = request.get_json()
    
    folder_name = data['folder_name']
    folder_description = data.get('folder_description', None)  # תיאור אופציונלי
    
    # יצירת תיקייה חדשה בטבלה Folders
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Folders (name, description)
        VALUES (?, ?)
    ''', (folder_name, folder_description))
    
    folder_id = cursor.lastrowid  # מקבלים את ה-ID של התיקייה החדשה
    conn.commit()

    # קשר בין תיקייה לקבצים - יש להוסיף לכל קובץ שנבחר עבור התיקייה
    file_ids = data.get('file_ids', [])
    if file_ids:
        for file_id in file_ids:
            cursor.execute('''
                INSERT INTO Folders_Files (folder_id, file_id)
                VALUES (?, ?)
            ''', (folder_id, file_id))
        conn.commit()

    cursor.close()
    return jsonify({"message": "Folder created successfully", "folder_id": folder_id}), 201

# הצגת פרטי תיקייה ספציפית
@folders_bp.route('/folder/<int:id>', methods=['GET'])
def get_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # קבלת פרטי תיקייה
    cursor.execute('''
        SELECT id, name, description FROM Folders WHERE id = ?
    ''', (id,))
    folder = cursor.fetchone()

    if folder is None:
        return jsonify({"message": "Folder not found"}), 404

    # קבלת קבצים קשורים לתיקייה
    cursor.execute('''
        SELECT file_id FROM Folders_Files WHERE folder_id = ?
    ''', (id,))
    files = cursor.fetchall()
    file_ids = [file[0] for file in files]

    cursor.close()

    folder_data = {
        "id": folder[0],
        "name": folder[1],
        "description": folder[2],
        "file_ids": file_ids
    }

    return jsonify(folder_data), 200

# קבלת כל התיקיות
@folders_bp.route('/folders', methods=['GET'])
def get_folders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Folders')
    rows = cursor.fetchall()
    cursor.close()    
    folders = [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]
    return jsonify(folders), 200

# עדכון פרטי תיקייה
@folders_bp.route('/folder/<int:id>', methods=['PUT'])
def update_folder(id):
    data = request.get_json()
    folder_name = data['folder_name']
    folder_description = data.get('folder_description', None)  # תיאור אופציונלי    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Folders
        SET name = ?, description = ?
        WHERE id = ?
    ''', (folder_name, folder_description, id))
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "Folder updated successfully"}), 200

# מחיקת תיקייה וכל השיוכים שלה לקבצים
@folders_bp.route('/folder/<int:id>', methods=['DELETE'])
def delete_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()    
    
    # מחיקת כל קשרי תיקייה-קובץ
    cursor.execute('DELETE FROM Folders_Files WHERE folder_id = ?', (id,))    
    
    # מחיקת התיקייה עצמה
    cursor.execute('DELETE FROM Folders WHERE id = ?', (id,))    
    
    conn.commit()
    cursor.close()    
    
    return jsonify({"message": "Folder deleted successfully"}), 200

# הוספת קובץ לתיקייה
@folders_bp.route('/folder/<int:folder_id>/file', methods=['POST'])
def add_file_to_folder(folder_id):
    data = request.get_json()
    file_ids = data.get('file_ids', [])
    
    if not file_ids:
        return jsonify({"message": "No file IDs provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # הוספת קבצים לתיקייה
    for file_id in file_ids:
        cursor.execute('''
            INSERT INTO Folders_Files (folder_id, file_id)
            VALUES (?, ?)
        ''', (folder_id, file_id))
    
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "Files added to folder successfully"}), 201

# מחיקת קובץ מתיקייה
@folders_bp.route('/folder/<int:folder_id>/file/<int:file_id>', methods=['DELETE'])
def delete_file_from_folder(folder_id, file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # מחיקת הקשר בין הקובץ לתיקייה
    cursor.execute('''
        DELETE FROM Folders_Files WHERE folder_id = ? AND file_id = ?
    ''', (folder_id, file_id))
    
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "File deleted from folder successfully"}), 200
