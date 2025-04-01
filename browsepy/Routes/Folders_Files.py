
from flask import Blueprint, request, jsonify
from ..database import get_db_connection

foldersFiles_bp = Blueprint('foldersFiles', __name__)  # יצירת Blueprint


@foldersFiles_bp.route('/folder_file', methods=['POST'])
def create_folder_file():
    data = request.get_json()
    folder_id = data['folder_id']
    file_id = data['file_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Folders_Files (folder_id, file_id)
        VALUES (?, ?)
    ''', (folder_id, file_id))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Folder File created successfully"}), 201

@foldersFiles_bp.route('/folder_files', methods=['GET'])
def get_folder_files():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Folders_Files')
    rows = cursor.fetchall()
    cursor.close()
    
    folder_files = [{"id": row[0], "folder_id": row[1], "file_id": row[2]} for row in rows]
    return jsonify(folder_files), 200

@foldersFiles_bp.route('/folder_file/<int:id>', methods=['DELETE'])
def delete_folder_file(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Folders_Files WHERE id = ?', (id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Folder File deleted successfully"}), 200
