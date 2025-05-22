from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
import os
from ..utils.decorators import safe_route

files_bp = Blueprint('files', __name__)  # Blueprint for file management

# Create a new file entry
@files_bp.route('/file', methods=['POST'])
@safe_route
def create_file():
    data = request.get_json()
    file_name = data.get('name')
    file_url = data.get('file_url')

    # Validate required fields
    if not file_name or not file_url:
        return jsonify({"message": "חובה לספק שם קובץ וכתובת קובץ"}), 400

    # Determine file type
    file_type = data.get('file_type')
    if not file_type:
        _, file_extension = os.path.splitext(file_name)
        file_type = file_extension.lstrip('.') if file_extension else 'docx'

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO Files (name, file_type, File_URL)
            VALUES (?, ?, ?)
        ''', (file_name, file_type, file_url))
        conn.commit()
        return jsonify({"message": "הקובץ נוצר בהצלחה"}), 201

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error while creating a file: {e}")
        return jsonify({"message": "אירעה שגיאה בעת יצירת הקובץ", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Retrieve all files
@files_bp.route('/files', methods=['GET'])
@safe_route
def get_files():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM Files')
        rows = cursor.fetchall()

        if not rows:
            return jsonify([]), 200

        files = [{"id": row[0], "name": row[1], "file_type": row[2], "file_url": row[3]} for row in rows]
        return jsonify(files), 200

    except Exception as e:
        current_app.logger.error(f"Error while retrieving all files: {e}")
        return jsonify({"message": "אירעה שגיאה בעת שליפת הקבצים", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Retrieve a specific file by ID
@files_bp.route('/file/<int:file_id>', methods=['GET'])
@safe_route
def get_file_by_id(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM Files WHERE id = ?', (file_id,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"message": f"קובץ עם מזהה {file_id} לא נמצא"}), 404

        file = {"id": row[0], "name": row[1], "file_type": row[2], "file_url": row[3]}
        return jsonify(file), 200

    except Exception as e:
        current_app.logger.error(f"Error while retrieving file by ID: {file_id}: {e}")
        return jsonify({"message": "אירעה שגיאה בעת שליפת הקובץ", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Update existing file metadata
@files_bp.route('/file/<int:id>', methods=['PUT'])
@safe_route
def update_file(id):
    data = request.get_json()
    name = data.get('name')
    file_type = data.get('file_type')
    file_url = data.get('file_url')

    # Validate required fields
    if not name or not file_url:
        return jsonify({"message": "חובה לספק שם קובץ וכתובת קובץ"}), 400

    # Determine file type if not given
    if not file_type:
        _, file_extension = os.path.splitext(name)
        file_type = file_extension.lstrip('.') if file_extension else 'docx'

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE Files
            SET name = ?, file_type = ?, File_URL = ?
            WHERE id = ?
        ''', (name, file_type, file_url, id))
        conn.commit()
        return jsonify({"message": "הקובץ עודכן בהצלחה"}), 200

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error while updating file {id}: {e}")
        return jsonify({"message": "אירעה שגיאה בעת עדכון הקובץ", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Delete a file by ID
@files_bp.route('/file/<int:id>', methods=['DELETE'])
@safe_route
def delete_file(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM Files WHERE id = ?', (id,))
        conn.commit()
        return jsonify({"message": "הקובץ נמחק בהצלחה"}), 200

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error while deleting file {id}: {e}")
        return jsonify({"message": "אירעה שגיאה בעת מחיקת הקובץ", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
