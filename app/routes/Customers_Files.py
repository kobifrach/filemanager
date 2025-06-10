from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
from ..utils.jwt_decorator import token_required

customer_files_bp = Blueprint('customer_files', __name__)

def dict_cursor(cursor):
    # Convert SQL cursor results to a list of dictionaries
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# @customer_files_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
# @safe_route
# @token_required()  
# def get_customer_files(customer_id):
#     current_app.logger.info(f"Request to retrieve files for customer ID {customer_id}")  
#     print(f"Received request to retrieve files for customer ID {customer_id}")
#     print(request)
#     print("data:", request.data)
#     # קבל את מזהה המשתמש מהבקשה
#     user_id = request.user['id']  # מזהה המשתמש מה-payload
#     user_role = request.user['role']  # תפקיד המשתמש מה-payload

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         # בדוק אם הלקוח קיים
#         cursor.execute('SELECT 1 FROM Customers WHERE id = ?', (customer_id,))
#         customer_exists = cursor.fetchone()

#         if not customer_exists:
#             current_app.logger.warning(f"customer with ID {customer_id} does not exist")  
#             return jsonify({"message": f"שגיאה: לקוח עם מזהה {customer_id} לא קיים."}), 404

#         # אם המשתמש הוא לקוח, בדוק אם הוא מנסה לגשת ללקוח שלו בלבד
#         if user_role == 'customer' and user_id != customer_id:
#             return jsonify({"message": "אין לך הרשאה לגשת לקבצים של לקוח אחר."}), 403

#         # # Execute the query to fetch files
#         # cursor.execute(''' 
#         #     SELECT f.id AS file_id, f.name, f.file_type, f.File_URL AS file_url
#         #     FROM Customers_Folders cf
#         #     JOIN Folders_Files ff ON cf.folder_id = ff.folder_id
#         #     JOIN Files f ON ff.file_id = f.id
#         #     WHERE cf.customer_id = ?
#         # ''', (customer_id,))
#         cursor.execute(''' SELECT 
#             cf_files.id,                           -- מזהה ייחודי של קובץ הלקוח
#             cf_files.original_file_id,             -- מאיזה קובץ מערכת הוא נוצר
#             cf_files.Customer_File_Name AS name,   -- שם הקובץ אצל הלקוח
#             cf_files.file_type,                    -- סוג קובץ
#             cf_files.file_path AS file_url,        -- הנתיב לקובץ
#             folders.folder_name AS folder_name     -- (רשות) שם התיקייה
#             FROM Customer_Files cf_files
#             JOIN Customers_Folders cf ON cf_files.folder_id = cf.folder_id
#             LEFT JOIN Folders folders ON cf.folder_id = folders.id
#             WHERE cf.customer_id = ?
#         ''', (customer_id,))

#         files = dict_cursor(cursor)

#         if files:
#             current_app.logger.info(f"Found {len(files)} files for customer ID {customer_id}")  
#             return jsonify({"files": files}), 200
#         else:
#             current_app.logger.warning(f"No files found for customer ID {customer_id}")  
#             return jsonify({"message": "לא נמצאו קבצים עבור הלקוח."}), 404
#     except Exception as e:
#         current_app.logger.error(f"Error retrieving files for customer ID {customer_id}: {str(e)}")  
#         return jsonify({"message": "שגיאה בשרת. אנא נסה שוב מאוחר יותר."}), 500
#     finally:
#         cursor.close()
#         conn.close()

@customer_files_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
@safe_route
@token_required()  
def get_customer_files(customer_id):
    current_app.logger.info(f"Request to retrieve files for customer ID {customer_id}")  
    
    # Get user ID and role from request
    user_id = request.user['id']
    user_role = request.user['role']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if customer exists
        cursor.execute('SELECT 1 FROM customer WHERE id = ?', (customer_id,))
        customer_exists = cursor.fetchone()

        if not customer_exists:
            current_app.logger.warning(f"Customer with ID {customer_id} does not exist")  
            return jsonify({"message": f"שגיאה: לקוח עם מזהה {customer_id} לא קיים."}), 404

        # If user is a customer, check if they can only access their own files
        if user_role == 'customer' and user_id != customer_id:
            return jsonify({"message": "אין לך הרשאה לגשת לקבצים של לקוח אחר."}), 403

        # CORRECTED: Query the customer files table with correct column names
        cursor.execute(''' 
            SELECT 
                cf_files.id,                                    -- Main database ID for deletion
                cf_files.original_file_id,                      -- Reference to original file
                cf_files.customer_file_name,                    -- Customer's file name
                cf_files.file_type,                             -- File type
                cf_files.file_path,                             -- Customer file path
                cf_folders.folder_name                          -- Folder name
            FROM customer_files cf_files
            JOIN customer_folder cf_folders ON cf_files.folder_id = cf_folders.id
            WHERE cf_folders.customer_id = ?
            ORDER BY cf_files._created_at DESC
        ''', (customer_id,))

        files = dict_cursor(cursor)

        if files:
            current_app.logger.info(f"Found {len(files)} customer files for customer ID {customer_id}")  
            return jsonify({"files": files}), 200
        else:
            current_app.logger.warning(f"No customer files found for customer ID {customer_id}")  
            return jsonify({"message": "לא נמצאו קבצים עבור הלקוח."}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error retrieving customer files for customer ID {customer_id}: {str(e)}")  
        return jsonify({"message": "שגיאה בשרת. אנא נסה שוב מאוחר יותר."}), 500
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
