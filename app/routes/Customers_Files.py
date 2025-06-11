from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
from ..utils.jwt_decorator import token_required

customer_files_bp = Blueprint('customer_files', __name__)

def dict_cursor(cursor):
    # Convert SQL cursor results to a list of dictionaries
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Retrieve files for a specific customer
@customer_files_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
@safe_route
@token_required()
def get_customer_files(customer_id):
    current_app.logger.info(f"בקשה לקבלת קבצים עבור לקוח ID {customer_id}")
    print(f"Received request to retrieve files for customer ID {customer_id}")

    user_id = request.user['id']
    user_role = request.user['role']
    print(f"User ID: {user_id}, User Role: {user_role}")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # בדיקה אם הלקוח קיים
        cursor.execute('SELECT 1 FROM Customers WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            current_app.logger.warning(f"לקוח עם מזהה {customer_id} לא קיים")
            return jsonify({"message": f"שגיאה: לקוח עם מזהה {customer_id} לא קיים."}), 404

        # בדיקת הרשאה אם המשתמש הוא לקוח ורוצה לגשת ללקוח אחר
        if user_role == 'customer' and user_id != customer_id:
            print(f"User {user_id} with role {user_role} tried to access files of customer {customer_id}")
            return jsonify({"message": "אין לך הרשאה לגשת לקבצים של לקוח אחר."}), 403
        print(f"User {user_id} has permission to access files of customer {customer_id}")

        # שליפת הקבצים של הלקוח מכל התיקיות
        cursor.execute('''
            SELECT 
                cf_files.id,                     -- מזהה קובץ
                cf_files.original_file_id,       -- הפניה לקובץ המקורי
                cf_files.customer_file_name,     -- שם הקובץ אצל הלקוח
                cf_files.file_type,              -- סוג הקובץ
                cf_files.file_path,              -- נתיב
                cf_folders.folder_name           -- שם תיקייה
            FROM Customers_Files cf_files
            JOIN Customers_Folders cf_folders ON cf_files.folder_id = cf_folders.id
            WHERE cf_folders.customer_id = ?
        ''', (customer_id,))
        
        files = dict_cursor(cursor)
        print(f"Retrieved {len(files)} files for customer ID {customer_id}")

        if files:
            current_app.logger.info(f"נמצאו {len(files)} קבצים עבור לקוח {customer_id}")
            return jsonify({"files": files}), 200
        else:
            current_app.logger.info(f"לא נמצאו קבצים עבור לקוח {customer_id}")
            return jsonify({"message": "לא נמצאו קבצים עבור הלקוח."}), 404

    except Exception as e:
        current_app.logger.error(f"שגיאה בשליפת קבצים ללקוח {customer_id}: {str(e)}")
        return jsonify({"message": "שגיאה בשרת. נסה שוב מאוחר יותר."}), 500

    finally:
        cursor.close()
        conn.close()

# Retrieve files for a specific customer within a specific folder
@customer_files_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>/files', methods=['GET'])
@safe_route
@token_required()
def get_customer_files_by_folder(customer_id, folder_id):
    current_app.logger.info(f"בקשה לקבצים עבור לקוח {customer_id} מתוך תיקייה {folder_id}")

    user_id = request.user['id']
    user_role = request.user['role']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # בדיקה אם הלקוח קיים
        cursor.execute('SELECT 1 FROM Customers WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            return jsonify({"message": f"שגיאה: לקוח עם מזהה {customer_id} לא קיים."}), 404

        # בדיקת הרשאה
        if user_role == 'customer' and user_id != customer_id:
            return jsonify({"message": "אין לך הרשאה לגשת לקבצים של לקוח אחר."}), 403

        # בדיקה אם התיקייה שייכת ללקוח
        #זה רק בדיקת אבטחה, כי אם התיקייה לא קיימת או לא שייכת ללקוח, לא יהיו קבצים
        cursor.execute('''
            SELECT 1 FROM Customers_Folders 
            WHERE id = ? AND customer_id = ?
        ''', (folder_id, customer_id))
        if not cursor.fetchone():
            return jsonify({"message": "התיקייה לא קיימת או לא שייכת ללקוח."}), 404
        print(f"Folder {folder_id} exists and belongs to customer {customer_id}")

        # שליפת קבצים מתוך התיקייה
        cursor.execute('''
            SELECT 
                cf_files.id,
                cf_files.original_file_id,
                cf_files.customer_file_name,
                cf_files.file_type,
                cf_files.file_path,
                cf_folders.folder_name
            FROM Customers_Files cf_files
            JOIN Customers_Folders cf_folders ON cf_files.folder_id = cf_folders.id
            WHERE cf_folders.customer_id = ? AND cf_folders.id = ?
            
        ''', (customer_id, folder_id))

        files = dict_cursor(cursor)

        if files:
            return jsonify({"files": files}), 200
        else:
            return jsonify({"message": "לא נמצאו קבצים בתיקייה."}), 404

    except Exception as e:
        current_app.logger.error(f"שגיאה בשליפת קבצים: {str(e)}")
        return jsonify({"message": "שגיאה בשרת."}), 500

    finally:
        cursor.close()
        conn.close()

#delete a file by its ID
@customer_files_bp.route('/customer/file/<int:file_id>', methods=['DELETE'])
@safe_route
@token_required()
def delete_file(file_id):
    # Log the request to delete a file with a specific ID
    current_app.logger.info(f"Request to delete file with ID {file_id}")  
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the file exists in the Customers_Files table
        cursor.execute('SELECT 1 FROM Customers_Files WHERE id = ?', (file_id,))
        file_exists = cursor.fetchone()

        if not file_exists:
            # Log a warning if the file does not exist
            current_app.logger.warning(f"File with ID {file_id} does not exist")  
            return jsonify({"message": f"שגיאה: קובץ עם מזהה {file_id} לא קיים."}), 404

        # Delete the file
        cursor.execute('DELETE FROM Customers_Files WHERE id = ?', (file_id,))
        conn.commit()

        # Log success after deleting the file
        current_app.logger.info(f"File with ID {file_id} successfully deleted")  
        return jsonify({"message": "הקובץ נמחק בהצלחה."}), 200
    except Exception as e:
        # Log an error if there is a problem deleting the file
        current_app.logger.error(f"Error deleting file with ID {file_id}: {str(e)}")  
        conn.rollback()  # Rollback in case of error
        return jsonify({"message": "שגיאה בשרת. אנא נסה שוב מאוחר יותר."}), 500
    finally:
        cursor.close()
        conn.close()
