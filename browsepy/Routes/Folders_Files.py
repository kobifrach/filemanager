from flask import Blueprint, request, jsonify, current_app
from ..database import get_db_connection
from browsepy.Utils.decorators import safe_route

foldersFiles_bp = Blueprint('foldersFiles', __name__)  # Blueprint for managing folder-file relationships

# Retrieve all folder-file relationships
@foldersFiles_bp.route('/folder_files', methods=['GET'])
@safe_route
def get_folder_files():
    current_app.logger.info("Fetching all folder-file relationships...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM Folders_Files')
        rows = cursor.fetchall()
        cursor.close()

        folder_files = [{"id": row[0], "folder_id": row[1], "file_id": row[2]} for row in rows]
        current_app.logger.info(f"Retrieved {len(folder_files)} folder-file relationships.")
        return jsonify(folder_files), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching folder-file relationships: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

# Move a file from one folder to another
@foldersFiles_bp.route('/folder_files', methods=['PUT'])
@safe_route
def move_file():
    data = request.get_json()
    file_id = data.get('file_id')
    new_folder_id = data.get('new_folder_id')
    
    current_app.logger.info(f"Moving file with ID {file_id} to folder {new_folder_id}...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the file entry exists in Folders_Files
        cursor.execute('''SELECT COUNT(*) FROM Folders_Files WHERE id = ?''', (file_id,))
        file_exists = cursor.fetchone()[0]

        if file_exists < 1:
            current_app.logger.warning(f"File ID {file_id} not found.")
            return jsonify({'message': 'לא נמצא קובץ תואם'}), 400

        # Check if the target folder exists
        cursor.execute('''SELECT COUNT(*) FROM Folders WHERE id = ?''', (new_folder_id,))
        folder_exists = cursor.fetchone()[0]

        if folder_exists < 1:
            current_app.logger.warning(f"Folder ID {new_folder_id} not found.")
            return jsonify({'message': 'לא נמצאה תיקייה עם מזהה זה'}), 400

        # Perform the update
        cursor.execute('''UPDATE Folders_Files SET folder_id = ? WHERE id = ?''', (new_folder_id, file_id))
        conn.commit()
        conn.close()

        current_app.logger.info(f"File {file_id} moved successfully to folder {new_folder_id}.")
        return jsonify({'message': 'הקובץ הועבר בהצלחה'}), 200

    except Exception as e:
        current_app.logger.error(f"Error moving file {file_id} to folder {new_folder_id}: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

# Add one or more files to a folder
@foldersFiles_bp.route('/folder/<int:folder_id>/file', methods=['POST'])
@safe_route
def add_file_to_folder(folder_id):
    data = request.get_json()
    file_ids = data.get('file_ids', [])
    
    current_app.logger.info(f"Adding files {file_ids} to folder {folder_id}...")

    if not file_ids:
        current_app.logger.warning("No file IDs provided.")
        return jsonify({"message": "לא סופקו מזהי קבצים"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verify folder existence
        cursor.execute('''SELECT id FROM Folders WHERE id = ?''', (folder_id,))
        if cursor.fetchone() is None:
            cursor.close()
            current_app.logger.warning(f"Folder ID {folder_id} not found.")
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
            cursor.execute('''SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ?''', (folder_id, file_id))
            if cursor.fetchone():
                skipped_files.append(file_id)
            else:
                cursor.execute('''INSERT INTO Folders_Files (folder_id, file_id) VALUES (?, ?)''', (folder_id, file_id))
                added_files.append(file_id)

        conn.commit()
        cursor.close()

        current_app.logger.info(f"Files added: {added_files}, Files skipped: {skipped_files}.")
        return jsonify({
            "message": "הפעולה הושלמה",
            "קבצים שנוספו": added_files,
            "קבצים שדוּלגו": skipped_files
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error adding files {file_ids} to folder {folder_id}: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

# Remove a file from a folder
@foldersFiles_bp.route('/folder/<int:folder_id>/file/<int:file_id>', methods=['DELETE'])
@safe_route
def delete_file_from_folder(folder_id, file_id):
    current_app.logger.info(f"Deleting file {file_id} from folder {folder_id}...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if folder exists
        cursor.execute('''SELECT id FROM Folders WHERE id = ?''', (folder_id,))
        if cursor.fetchone() is None:
            cursor.close()
            current_app.logger.warning(f"Folder ID {folder_id} not found.")
            return jsonify({"message": "התיקייה לא נמצאה"}), 404

        # Check if file exists in the folder
        cursor.execute('''SELECT 1 FROM Folders_Files WHERE folder_id = ? AND file_id = ?''', (folder_id, file_id))
        if cursor.fetchone() is None:
            cursor.close()
            current_app.logger.warning(f"File ID {file_id} not found in folder {folder_id}.")
            return jsonify({"message": "הקובץ לא נמצא בתיקייה"}), 404

        # Delete the relationship
        cursor.execute('''DELETE FROM Folders_Files WHERE folder_id = ? AND file_id = ?''', (folder_id, file_id))
        conn.commit()
        cursor.close()

        current_app.logger.info(f"File {file_id} successfully deleted from folder {folder_id}.")
        return jsonify({"message": "הקובץ נמחק מהתיקייה בהצלחה"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_id} from folder {folder_id}: {e}")
        return jsonify({"message": "Internal Server Error"}), 500
