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

