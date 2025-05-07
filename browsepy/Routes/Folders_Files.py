from flask import Blueprint, request, jsonify
from ..database import get_db_connection
from browsepy.Utils.decorators import safe_route

foldersFiles_bp = Blueprint('foldersFiles', __name__)  # Blueprint for managing folder-file relationships

# Retrieve all folder-file relationships
@foldersFiles_bp.route('/folder_files', methods=['GET'])
@safe_route
def get_folder_files():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Folders_Files')
    rows = cursor.fetchall()
    cursor.close()

    folder_files = [{"id": row[0], "folder_id": row[1], "file_id": row[2]} for row in rows]
    return jsonify(folder_files), 200


# Move a file from one folder to another
@foldersFiles_bp.route('/folder_files', methods=['PUT'])
@safe_route
def move_file():
    data = request.get_json()
    file_id = data.get('file_id')
    new_folder_id = data.get('new_folder_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the file entry exists in Folders_Files
    cursor.execute('''
        SELECT COUNT(*) FROM Folders_Files WHERE id = ?
    ''', (file_id,))
    file_exists = cursor.fetchone()[0]

    if file_exists < 1:
        return jsonify({'message': 'לא נמצא קובץ תואם'}), 400

    # Check if the target folder exists
    cursor.execute('''
        SELECT COUNT(*) FROM Folders WHERE id = ?
    ''', (new_folder_id,))
    folder_exists = cursor.fetchone()[0]

    if folder_exists < 1:
        return jsonify({'message': 'לא נמצאה תיקייה עם מזהה זה'}), 400

    # Perform the update
    cursor.execute('''
        UPDATE Folders_Files SET folder_id = ? WHERE id = ?
    ''', (new_folder_id, file_id))

    conn.commit()
    conn.close()

    return jsonify({'message': 'הקובץ הועבר בהצלחה'}), 200


# Add one or more files to a folder
@foldersFiles_bp.route('/folder/<int:folder_id>/file', methods=['POST'])
@safe_route
def add_file_to_folder(folder_id):
    data = request.get_json()
    file_ids = data.get('file_ids', [])

    if not file_ids:
        return jsonify({"message": "לא סופקו מזהי קבצים"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify folder existence
    cursor.execute('''
        SELECT id FROM Folders WHERE id = ?
    ''', (folder_id,))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "התיקייה לא נמצאה"}), 404

    added_files = []
    skipped_files = []

    for file_id in file_ids:
        # Check if file exists
        cursor.execute('SELECT id FROM Files WHERE id = ?', (file_id,))
        if cursor.fetchone() is None:
            skipped_files.append(file_id)
            continue

        # Check for existing folder-file relationship
        cursor.execute('''
            SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ?
        ''', (folder_id, file_id))
        if cursor.fetchone():
            skipped_files.append(file_id)
        else:
            cursor.execute('''
                INSERT INTO Folders_Files (folder_id, file_id)
                VALUES (?, ?)
            ''', (folder_id, file_id))
            added_files.append(file_id)

    conn.commit()
    cursor.close()

    return jsonify({
        "message": "הפעולה הושלמה",
        "קבצים שנוספו": added_files,
        "קבצים שדוּלגו": skipped_files
    }), 201


# Remove a file from a folder
@foldersFiles_bp.route('/folder/<int:folder_id>/file/<int:file_id>', methods=['DELETE'])
@safe_route
def delete_file_from_folder(folder_id, file_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if folder exists
    cursor.execute('''
        SELECT id FROM Folders WHERE id = ?
    ''', (folder_id,))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "התיקייה לא נמצאה"}), 404

    # Check if file exists in the folder
    cursor.execute('''
        SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ?
    ''', (folder_id, file_id))
    if cursor.fetchone() is None:
        cursor.close()
        return jsonify({"message": "הקובץ לא נמצא בתיקייה"}), 404

    # Delete the relationship
    cursor.execute('''
        DELETE FROM Folders_Files WHERE folder_id = ? AND file_id = ?
    ''', (folder_id, file_id))

    conn.commit()
    cursor.close()

    return jsonify({"message": "הקובץ נמחק מהתיקייה בהצלחה"}), 200
