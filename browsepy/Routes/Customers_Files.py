#עובד

from flask import Blueprint, request, jsonify
from ..database import get_db_connection

customer_files_bp = Blueprint('customer_files', __name__)


#הצגת כל הקבצים של לקוח
@customer_files_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
def get_customer_files(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # שליפת הקבצים שמשויכים ללקוח
        cursor.execute('''
            SELECT f.id AS file_id, f.name, f.file_type, f.File_URL
            FROM Customers_Folders cf
            JOIN Folders_Files ff ON cf.folder_id = ff.folder_id
            JOIN Files f ON ff.file_id = f.id
            WHERE cf.customer_id = ?
        ''', (customer_id,))

        files = cursor.fetchall()

        # אם יש קבצים
        if files:
            return jsonify({"files": [{"file_id": file[0], "name": file[1], "file_type": file[2], "File_URL": file[3]} for file in files]}), 200
        else:
            return jsonify({"message": "No files found for this customer."}), 204

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()



#מחיקת קובץ מטבלת קבצי לקוחות
@customer_files_bp.route('/customer/file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # בדיקה אם הקובץ קיים בטבלת Customers_Files
        cursor.execute('SELECT COUNT(*) FROM Customers_Files WHERE id = ?', (file_id,))
        file_exists = cursor.fetchone()[0]
        
        if file_exists == 0:
            return jsonify({"message": f"Error: File with ID {file_id} does not exist."}), 400

        # מחיקת הקובץ מטבלת Customers_Files
        cursor.execute('DELETE FROM Customers_Files WHERE id = ?', (file_id,))

        conn.commit()
        return jsonify({"message": f"File with ID {file_id} deleted successfully."}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()


# # הצגת קבצים בתיקיה
# @customer_files_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>/files', methods=['GET'])
# def get_customer_files_by_folder(customer_id, folder_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute('''
#             SELECT f.id, f.file_name
#             FROM Files f
#             JOIN Folders_Files ff ON f.id = ff.file_id
#             WHERE ff.folder_id = ?
#         ''', (folder_id,))

#         files = cursor.fetchall()
#         file_list = [{"id": file[0], "file_name": file[1]} for file in files]
#         return jsonify({"files": file_list}), 200

#     except Exception as e:
#         return jsonify({"message": f"Error: {str(e)}"}), 500

#     finally:
#         cursor.close()

# # הוספת קובץ לתיקייה של לקוח
# @customer_files_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>/file', methods=['POST'])
# def add_file_to_customer_folder(customer_id, folder_id):
#     data = request.get_json()
#     file_name = data.get('file_name')

#     if not file_name:
#         return jsonify({"message": "Error: 'file_name' is required"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute('SELECT id FROM Folders WHERE id = ?', (folder_id,))
#         folder = cursor.fetchone()
#         if not folder:
#             return jsonify({"message": f"Error: Folder with ID {folder_id} does not exist"}), 400

#         cursor.execute('INSERT INTO Files (file_name) OUTPUT INSERTED.id VALUES (?)', (file_name,))
#         file_id = cursor.fetchone()[0]

#         cursor.execute('''
#             INSERT INTO Folders_Files (folder_id, file_id)
#             VALUES (?, ?)
#         ''', (folder_id, file_id))

#         conn.commit()
#         return jsonify({"message": "File added to folder successfully!", "file_id": file_id}), 201

#     except Exception as e:
#         conn.rollback()
#         return jsonify({"message": f"Error: {str(e)}"}), 500

#     finally:
#         cursor.close()

# # מחיקת קובץ מתוך תיקיית לקוח
# @customer_files_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>/file/<int:file_id>', methods=['DELETE'])
# def delete_file_from_customer_folder(customer_id, folder_id, file_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute('''
#             DELETE FROM Folders_Files 
#             WHERE folder_id = ? AND file_id = ?
#         ''', (folder_id, file_id))

#         conn.commit()
#         return jsonify({"message": "File deleted successfully!"}), 200

#     except Exception as e:
#         conn.rollback()
#         return jsonify({"message": f"Error: {str(e)}"}), 500

#     finally:
#         cursor.close()
