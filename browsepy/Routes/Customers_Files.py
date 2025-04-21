from flask import Blueprint, request, jsonify
from ..database import get_db_connection

customer_files_bp = Blueprint('customer_files', __name__)


# Retrieve all files associated with a specific customer
@customer_files_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
def get_customer_files(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch all files linked to the customer's folders
        cursor.execute('''
            SELECT f.id AS file_id, f.name, f.file_type, f.File_URL
            FROM Customers_Folders cf
            JOIN Folders_Files ff ON cf.folder_id = ff.folder_id
            JOIN Files f ON ff.file_id = f.id
            WHERE cf.customer_id = ?
        ''', (customer_id,))

        files = cursor.fetchall()

        if files:
            files_list = [
                {
                    "file_id": file[0],
                    "name": file[1],
                    "file_type": file[2],
                    "File_URL": file[3]
                } for file in files
            ]
            return jsonify({"files": files_list}), 200
        else:
            return jsonify({"message": "לא נמצאו קבצים עבור הלקוח."}), 204

    except Exception as e:
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()


# Delete a file from the Customers_Files table
@customer_files_bp.route('/customer/file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Validate that the file exists
        cursor.execute('SELECT COUNT(*) FROM Customers_Files WHERE id = ?', (file_id,))
        file_exists = cursor.fetchone()[0]
        
        if file_exists == 0:
            return jsonify({"message": f"שגיאה: קובץ עם מזהה {file_id} לא קיים."}), 404

        # Delete the file from the customer's files
        cursor.execute('DELETE FROM Customers_Files WHERE id = ?', (file_id,))

        conn.commit()
        return jsonify({"message": f"הקובץ נמחק בהצלחה."}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()
