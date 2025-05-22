
from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route

folders_bp = Blueprint('folders', __name__)

# Helper function to handle database connection and cursor management
def execute_db_query(query, params=None, fetchone=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.fetchone() if fetchone else cursor.fetchall()
    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# Create a new generic folder and optionally link files to it
@folders_bp.route('/folder', methods=['POST'])
@safe_route
def create_folder():
    data = request.get_json()

    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "שגיאה: יש לציין שם תיקייה"}), 400

    folder_description = data.get('folder_description', None)

    try:
        current_app.logger.info(f"📂 Trying to insert folder: {folder_name}, Description: {folder_description}")

        result = execute_db_query('''
            INSERT INTO Folders (name, description)
            OUTPUT INSERTED.id
            VALUES (?, ?)
        ''', (folder_name, folder_description), fetchone=True)

        if not result:
            current_app.logger.error("⚠️ INSERTED.id returned NULL!")
            return jsonify({"message": "שגיאה: לא ניתן היה לקבל את מזהה התיקייה"}), 500

        folder_id = result[0]
        current_app.logger.info(f"✅ Folder ID retrieved: {folder_id}")

        file_ids = data.get('file_ids', [])
        if file_ids:
            current_app.logger.info(f"📁 Checking if files exist: {file_ids}")
            
            placeholders = ','.join(['?'] * len(file_ids))
            existing_files = {row[0] for row in execute_db_query(f'''
                SELECT id FROM Files WHERE id IN ({placeholders})
            ''', tuple(file_ids))}

            missing_files = [fid for fid in file_ids if fid not in existing_files]
            if missing_files:
                return jsonify({"message": f"שגיאה: קבצים לא נמצאו: {missing_files}"}), 400

            for file_id in file_ids:
                current_app.logger.info(f"🔗 Linking file {file_id} to folder {folder_id}")
                execute_db_query('''
                    INSERT INTO Folders_Files (folder_id, file_id)
                    VALUES (?, ?)
                ''', (folder_id, file_id))

        return jsonify({"message": "התיקייה נוצרה בהצלחה", "folder_id": folder_id}), 201

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500


# Retrieve metadata and linked file IDs of a specific folder
@folders_bp.route('/folder/<int:id>', methods=['GET'])
@safe_route
def get_folder(id):
    try:
        folder = execute_db_query('''
            SELECT id, name, description FROM Folders WHERE id = ?
        ''', (id,), fetchone=True)

        if folder is None:
            return jsonify({"message": "התיקייה לא נמצאה"}), 404

        file_ids = [file[0] for file in execute_db_query('''
            SELECT file_id FROM Folders_Files WHERE folder_id = ?
        ''', (id,))]

        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "description": folder[2],
            "file_ids": file_ids
        }

        return jsonify(folder_data), 200

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500


# Update a folder's name and optional description
@folders_bp.route('/folder/<int:id>', methods=['PUT'])
@safe_route
def update_folder(id):
    data = request.get_json()
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "יש להזין שם תיקייה"}), 400

    folder_description = data.get('folder_description', None)

    try:
        # Check if the folder exists
        folder = execute_db_query('''
            SELECT id FROM Folders WHERE id = ?
        ''', (id,), fetchone=True)
        
        if not folder:
            return jsonify({"message": "התיקייה לא נמצאה"}), 404

        execute_db_query('''
            UPDATE Folders
            SET name = ?, description = ?
            WHERE id = ?
        ''', (folder_name, folder_description, id))

        return jsonify({"message": "התיקייה עודכנה בהצלחה"}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500


# Delete a folder and remove all its associated file links
@folders_bp.route('/folder/<int:id>', methods=['DELETE'])
@safe_route
def delete_folder(id):
    try:
        # Check if the folder exists
        folder = execute_db_query('''
            SELECT id FROM Folders WHERE id = ?
        ''', (id,), fetchone=True)

        if not folder:
            return jsonify({"message": "התיקייה לא נמצאה"}), 404

        execute_db_query('DELETE FROM Folders_Files WHERE folder_id = ?', (id,))
        execute_db_query('DELETE FROM Folders WHERE id = ?', (id,))

        return jsonify({"message": "התיקייה נמחקה בהצלחה"}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500


# Retrieve the list of all generic folders (ID and name)
@folders_bp.route('/folders', methods=['GET'])
@safe_route
def get_all_folders():
    try:
        folders = [{"id": row[0], "name": row[1]} for row in execute_db_query('''
            SELECT id, name FROM Folders
        ''')]

        return jsonify({"folders": folders}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500


# Retrieve all unique files linked to the given folder IDs
@folders_bp.route('/folders/files', methods=['POST'])
@safe_route
def get_files_by_folders():
    data = request.get_json()
    folder_ids = data.get('folder_ids', [])

    if not folder_ids:
        return jsonify({"message": "לא התקבלו מזהי תיקיות"}), 400

    try:
        placeholders = ','.join(['?'] * len(folder_ids))

        files = [{"id": row[0], "name": row[1], "type": row[2], "path": row[3]} for row in execute_db_query(f'''
            SELECT DISTINCT f.id, f.name, f.file_type, f.File_URL
            FROM Files f
            JOIN Folders_Files ff ON f.id = ff.file_id
            WHERE ff.folder_id IN ({placeholders})
        ''', tuple(folder_ids))]

        return jsonify({"files": files}), 200

    except Exception as e:
        current_app.logger.error(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500
