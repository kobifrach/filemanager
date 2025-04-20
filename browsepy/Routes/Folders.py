#נבדק, עובד מושלם

from flask import Blueprint, request, jsonify
from ..database import get_db_connection

folders_bp = Blueprint('folders', __name__)

# יצירת תיקייה
@folders_bp.route('/folder', methods=['POST'])
def create_folder():
    data = request.get_json()

    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "Error: 'folder_name' is required"}), 400

    folder_description = data.get('folder_description', None)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(f"📂 Trying to insert folder: {folder_name}, Description: {folder_description}")

        # הכנסת תיקייה והחזרת ה-ID
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
            return jsonify({"message": "Error: Could not retrieve folder_id"}), 500

        # הכנסת קשרי קבצים לתיקייה עם בדיקת קיום
        file_ids = data.get('file_ids', [])
        if file_ids:
            print(f"📁 Checking if files exist: {file_ids}")

            # בדיקה האם כל הקבצים קיימים
            cursor.execute(f'''
                SELECT id FROM Files WHERE id IN ({','.join(['?'] * len(file_ids))})
            ''', tuple(file_ids))
            existing_files = {row[0] for row in cursor.fetchall()}

            missing_files = [fid for fid in file_ids if fid not in existing_files]
            if missing_files:
                print(f"⚠️ Files not found: {missing_files}")
                return jsonify({"message": f"Error: Files not found: {missing_files}"}), 400

            # הוספת הקבצים הקיימים לתיקייה
            for file_id in file_ids:
                print(f"🔗 Linking file {file_id} to folder {folder_id}")
                cursor.execute('''
                    INSERT INTO Folders_Files (folder_id, file_id)
                    VALUES (?, ?)
                ''', (folder_id, file_id))
            print("✅ All file links inserted successfully!")

        conn.commit()  # עושים commit רק אחרי שכל הנתונים הוכנסו בהצלחה

        return jsonify({"message": "Folder created successfully", "folder_id": folder_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()



# הצגת פרטי תיקייה ספציפית
@folders_bp.route('/folder/<int:id>', methods=['GET'])
def get_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(''' 
        SELECT id, name, description FROM Folders WHERE id = ? 
    ''', (id,))
    folder = cursor.fetchone()

    if folder is None:
        return jsonify({"message": "Folder not found"}), 404

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



# עדכון פרטי תיקייה
@folders_bp.route('/folder/<int:id>', methods=['PUT'])
def update_folder(id):
    data = request.get_json()
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({"message": "folder_name is required"}), 400
    
    folder_description = data.get('folder_description', None)  # תיאור אופציונלי    
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # וולידציה אם התיקייה קיימת
    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (id,))
    if cursor.fetchone() is None:
        return jsonify({"message": "Folder not found"}), 404

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
    
    # וולידציה אם התיקייה קיימת
    cursor.execute(''' 
        SELECT id FROM Folders WHERE id = ? 
    ''', (id,))
    if cursor.fetchone() is None:
        return jsonify({"message": "Folder not found"}), 404

    # מחיקת כל קשרי תיקייה-קובץ
    cursor.execute('DELETE FROM Folders_Files WHERE folder_id = ?', (id,))    
    
    # מחיקת התיקייה עצמה
    cursor.execute('DELETE FROM Folders WHERE id = ?', (id,))    
    
    conn.commit()
    cursor.close()    
    
    return jsonify({"message": "Folder deleted successfully"}), 200


# הצגת כל שמות התיקיות
@folders_bp.route('/folders', methods=['GET'])
def get_all_folders():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name FROM Folders
    ''')
    folders = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

    cursor.close()
    return jsonify({"folders": folders}), 200


# הצגת כל הקבצים שקשורים לרשימת תיקיות
@folders_bp.route('/folders/files', methods=['POST'])
def get_files_by_folders():
    data = request.get_json()
    folder_ids = data.get('folder_ids', [])

    if not folder_ids:
        return jsonify({"message": "No folder IDs provided"}), 400

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
