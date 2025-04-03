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


