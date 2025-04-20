# נבדק, עובד מושלם

from flask import Blueprint, request, jsonify
from ..database import get_db_connection

foldersFiles_bp = Blueprint('foldersFiles', __name__)  # יצירת Blueprint

# הצגת כל הקשרים בין תיקיות לקבצים
@foldersFiles_bp.route('/folder_files', methods=['GET'])
def get_folder_files():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Folders_Files')
    rows = cursor.fetchall()
    cursor.close()
    
    folder_files = [{"id": row[0], "folder_id": row[1], "file_id": row[2]} for row in rows]
    return jsonify(folder_files), 200


#העברת קבצים בין תיקיות
@foldersFiles_bp.route('/folder_files', methods=['PUT'])
def move_file():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    file_id = data.get('file_id')
    new_folder_id = data.get('new_folder_id')

    # בדוק אם הקובץ קיים
    cursor.execute('''
        SELECT COUNT(*) FROM Folders_Files WHERE id = ?
    ''', (file_id,))
    
    file_exists = cursor.fetchone()[0]

    if file_exists < 1:
        return jsonify({'message': 'No file found'}), 400

    # בדוק אם התיקיה עם ה-ID המבוקש קיימת
    cursor.execute('''
        SELECT COUNT(*) FROM Folders WHERE id = ?
    ''', (new_folder_id,))
    
    folder_exists = cursor.fetchone()[0]

    if folder_exists < 1:
        return jsonify({'message': 'No folder found with the specified ID'}), 400

    # אם הקובץ והתיקיה קיימים, בצע את העדכון
    cursor.execute('''
        UPDATE Folders_Files SET folder_id = ? WHERE id = ?
    ''', (new_folder_id, file_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'File moved successfully'}), 200


# הוספת קובץ לתיקייה
@foldersFiles_bp.route('/folder/<int:folder_id>/file', methods=['POST'])
def add_file_to_folder(folder_id):
    data = request.get_json()
    file_ids = data.get('file_ids', [])
    
    if not file_ids:
        return jsonify({"message": "No file IDs provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # וולידציה אם התיקייה קיימת
    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (folder_id,))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "Folder not found"}), 404

    added_files = []
    skipped_files = []

    for file_id in file_ids:
        # וולידציה אם הקובץ קיים
        cursor.execute("SELECT id FROM Files WHERE id = ?", (file_id,))
        if cursor.fetchone() is None:
            skipped_files.append(file_id)
            continue  # מדלגים על קובץ שלא קיים

        # בדיקה אם הקשר כבר קיים
        cursor.execute('''
            SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ?
        ''', (folder_id, file_id))
        if cursor.fetchone():
            skipped_files.append(file_id)  # מוסיפים לרשימת המדולגים
        else:
            cursor.execute('''
                INSERT INTO Folders_Files (folder_id, file_id)
                VALUES (?, ?)
            ''', (folder_id, file_id))
            added_files.append(file_id)  # מוסיפים לרשימת הקבצים שהתווספו

    conn.commit()
    cursor.close()
    
    return jsonify({
        "message": "Operation completed",
        "added_files": added_files,
        "skipped_files": skipped_files
    }), 201


# מחיקת קובץ מתיקייה
@foldersFiles_bp.route('/folder/<int:folder_id>/file/<int:file_id>', methods=['DELETE'])
def delete_file_from_folder(folder_id, file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # וולידציה אם התיקייה קיימת
    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (folder_id,))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "Folder not found"}), 404

    # וולידציה אם הקובץ קיים בתיקייה
    cursor.execute(''' 
        SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ? 
    ''', (folder_id, file_id))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "File not found in folder"}), 404
    
    # מחיקת הקשר בין הקובץ לתיקייה
    cursor.execute('''
        DELETE FROM Folders_Files WHERE folder_id = ? AND file_id = ?
    ''', (folder_id, file_id))
    
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "File deleted from folder successfully"}), 200
