from flask import Blueprint, request, jsonify
from ..database import get_db_connection
from browsepy.Utils.decorators import safe_route


folders_bp = Blueprint('folders', __name__)

# Create a new generic folder and optionally link files to it
@folders_bp.route('/folder', methods=['POST'])
@safe_route
def create_folder():
    data = request.get_json()

    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "שגיאה: יש לציין שם תיקייה"}), 400

    folder_description = data.get('folder_description', None)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(f"📂 Trying to insert folder: {folder_name}, Description: {folder_description}")

        cursor.execute('''
            INSERT INTO Folders (name, description)
            OUTPUT INSERTED.id
            VALUES (?, ?)
        ''', (folder_name, folder_description))

        result = cursor.fetchone()
        print(f"🔍 Raw result from OUTPUT INSERTED.id: {result}")

        if result and result[0]:
            folder_id = result[0]
            print(f"✅ Folder ID retrieved: {folder_id}")
        else:
            print("⚠️ INSERTED.id returned NULL!")
            return jsonify({"message": "שגיאה: לא ניתן היה לקבל את מזהה התיקייה"}), 500

        file_ids = data.get('file_ids', [])
        if file_ids:
            print(f"📁 Checking if files exist: {file_ids}")

            cursor.execute(f'''
                SELECT id FROM Files WHERE id IN ({','.join(['?'] * len(file_ids))})
            ''', tuple(file_ids))
            existing_files = {row[0] for row in cursor.fetchall()}

            missing_files = [fid for fid in file_ids if fid not in existing_files]
            if missing_files:
                print(f"⚠️ Files not found: {missing_files}")
                return jsonify({"message": f"שגיאה: קבצים לא נמצאו: {missing_files}"}), 400

            for file_id in file_ids:
                print(f"🔗 Linking file {file_id} to folder {folder_id}")
                cursor.execute('''
                    INSERT INTO Folders_Files (folder_id, file_id)
                    VALUES (?, ?)
                ''', (folder_id, file_id))
            print("✅ All file links inserted successfully!")

        conn.commit()

        return jsonify({"message": "התיקייה נוצרה בהצלחה", "folder_id": folder_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()


# Retrieve metadata and linked file IDs of a specific folder
@folders_bp.route('/folder/<int:id>', methods=['GET'])
@safe_route
def get_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(''' 
        SELECT id, name, description FROM Folders WHERE id = ? 
    ''', (id,))
    folder = cursor.fetchone()

    if folder is None:
        return jsonify({"message": "התיקייה לא נמצאה"}), 404

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


# Update a folder's name and optional description
@folders_bp.route('/folder/<int:id>', methods=['PUT'])
@safe_route
def update_folder(id):
    data = request.get_json()
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "יש להזין שם תיקייה"}), 400
    
    folder_description = data.get('folder_description', None)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (id,))
    if cursor.fetchone() is None:
        return jsonify({"message": "התיקייה לא נמצאה"}), 404

    cursor.execute('''
        UPDATE Folders
        SET name = ?, description = ?
        WHERE id = ?
    ''', (folder_name, folder_description, id))
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "התיקייה עודכנה בהצלחה"}), 200


# Delete a folder and remove all its associated file links
@folders_bp.route('/folder/<int:id>', methods=['DELETE'])
@safe_route
def delete_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()    
    
    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (id,))
    if cursor.fetchone() is None:
        return jsonify({"message": "התיקייה לא נמצאה"}), 404

    cursor.execute('DELETE FROM Folders_Files WHERE folder_id = ?', (id,))    
    cursor.execute('DELETE FROM Folders WHERE id = ?', (id,))    
    
    conn.commit()
    cursor.close()    
    
    return jsonify({"message": "התיקייה נמחקה בהצלחה"}), 200


# Retrieve the list of all generic folders (ID and name)
@folders_bp.route('/folders', methods=['GET'])
@safe_route
def get_all_folders():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name FROM Folders
    ''')
    folders = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

    cursor.close()
    return jsonify({"folders": folders}), 200


# Retrieve all unique files linked to the given folder IDs
@folders_bp.route('/folders/files', methods=['POST'])
@safe_route
def get_files_by_folders():
    data = request.get_json()
    folder_ids = data.get('folder_ids', [])

    if not folder_ids:
        return jsonify({"message": "לא התקבלו מזהי תיקיות"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?'] * len(folder_ids))

    cursor.execute(f'''
        SELECT DISTINCT f.id, f.name, f.file_type, f.File_URL
        FROM Files f
        JOIN Folders_Files ff ON f.id = ff.file_id
        WHERE ff.folder_id IN ({placeholders})
    ''', tuple(folder_ids))

    files = [{"id": row[0], "name": row[1], "type": row[2], "path": row[3]} for row in cursor.fetchall()]

    cursor.close()
    return jsonify({"files": files}), 200
