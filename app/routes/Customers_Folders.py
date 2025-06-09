from flask import Blueprint, jsonify, request, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
from ..utils.jwt_decorator import token_required

customer_folders_bp = Blueprint('customer_folders', __name__)

# Utility function to format the SQL query results as a dictionary
def dict_cursor(cursor):
    # Convert SQL cursor results to a list of dictionaries
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Get all folders for a specific customer
@customer_folders_bp.route('/customer/<int:customer_id>/folders', methods=['GET'])
@safe_route
@token_required()  # Anyone with a valid token can access
def get_customer_folders(customer_id):
    current_app.logger.info(f"Request to retrieve folders for customer ID {customer_id}")  # Log the request
    
    
    # Assume: user information is available in the request payload after token validation
    current_user_id = request.user['id']  # Get the current user's ID from the request
    current_user_role = request.user['role']  # Get the current user's role from the request

    if current_user_role == 'customer' and current_user_id != customer_id:
        return jsonify({"message": "שגיאה: לקוח יכול לגשת רק לתיקיות שלו."}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the customer exists
        cursor.execute('SELECT 1 FROM Customers WHERE id = ?', (customer_id,))
        customer_exists = cursor.fetchone()

        if not customer_exists:
            current_app.logger.warning(f"customer with ID {customer_id} does not exist")  
            return jsonify({"message": f"שגיאה: לקוח עם מזהה {customer_id} לא קיים."}), 404

        cursor.execute(''' 
            SELECT f.id, f.name
            FROM Folders f
            JOIN Customers_Folders cf ON f.id = cf.folder_id
            WHERE cf.customer_id = ?
        ''', (customer_id,))

        folders = dict_cursor(cursor)

        if folders:
            current_app.logger.info(f"Found {len(folders)} folders for customer ID {customer_id}")  
            return jsonify({"folders": folders}), 200
        else:
            current_app.logger.warning(f"No folders found for customer ID {customer_id}")  
            return jsonify({"message": "לא נמצאו תיקיות עבור הלקוח."}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching folders for customer ID {customer_id}: {str(e)}")  
        return jsonify({"message": "שגיאה בשרת. אנא נסה שוב מאוחר יותר."}), 500
    finally:
        cursor.close()
        conn.close()


# Delete a folder linked to a customer, including its associated files
@customer_folders_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>', methods=['DELETE'])
@safe_route
@token_required(allowed_roles=["user","manager","admin"])
def delete_customer_folder(customer_id, folder_id):
    current_app.logger.info(f"Request to delete folder with ID {folder_id} for customer ID {customer_id}")  # Log request
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Validate that the customer exists
        cursor.execute('SELECT id FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            current_app.logger.warning(f"Customer ID {customer_id} not found")  # Log customer not found
            return jsonify({"message": "שגיאה: לקוח לא נמצא"}), 404

        # Validate that the folder exists for the customer
        cursor.execute('SELECT id FROM Customers_Folders WHERE customer_id = ? AND folder_id = ?', (customer_id, folder_id))
        folder = cursor.fetchone()
        if not folder:
            current_app.logger.warning(f"Folder ID {folder_id} not linked to customer ID {customer_id}")  # Log folder not linked
            return jsonify({"message": "שגיאה: התיקייה לא משויכת ללקוח זה"}), 404

        customer_folder_id = folder[0]

        # Begin transaction block
        cursor.execute('DELETE FROM Customers_Files WHERE folder_id = ?', (customer_folder_id,))
        cursor.execute('DELETE FROM Customers_Folders WHERE id = ?', (customer_folder_id,))

        conn.commit()
        current_app.logger.info(f"Folder ID {folder_id} successfully deleted for customer ID {customer_id}")  # Log success
        return jsonify({"message": "התיקייה נמחקה בהצלחה!"}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting folder ID {folder_id} for customer ID {customer_id}: {str(e)}")  # Log error
        conn.rollback()  # Rollback transaction in case of error
        return jsonify({"message": "שגיאה בשרת, נסה שוב מאוחר יותר"}), 500
    finally:
        cursor.close()
        conn.close()

# Add a generic folder and all its files to a specific customer
@customer_folders_bp.route('/customer/<int:customer_id>/folder', methods=['POST'])
@safe_route
@token_required(allowed_roles=["user","manager","admin"])
def add_folder_to_customer(customer_id):
    data = request.get_json()
    folder_id = data.get('folder_id')

    if not folder_id or not isinstance(folder_id, int):
        current_app.logger.warning(f"Invalid folder ID provided: {folder_id}")  # Log invalid input
        return jsonify({"message": "שגיאה: חובה לציין מזהה תיקייה חוקי (folder_id)"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:     
        # Validate that the folder exists
        cursor.execute('SELECT id, name FROM Folders WHERE id = ?', (folder_id,))
        folder = cursor.fetchone()
        if not folder:
            current_app.logger.warning(f"Folder ID {folder_id} not found")  # Log folder not found
            return jsonify({"message": f"שגיאה: לא נמצאה תיקייה עם מזהה {folder_id}"}), 404

        # Validate that the customer exists and get their ID number
        cursor.execute('SELECT id_number FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            current_app.logger.warning(f"Customer ID {customer_id} not found")  # Log customer not found
            return jsonify({"message": f"שגיאה: לא נמצא לקוח עם מזהה {customer_id}"}), 404

        id_number = customer[0]
        folder_name = f"{folder[1]}_{id_number}"

        # Begin transaction block
        cursor.execute(''' 
            INSERT INTO Customers_Folders (customer_id, folder_id, Folder_Name)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        ''', (customer_id, folder_id, folder_name))
        customer_folder_id = cursor.fetchone()[0]

        # Get all generic files linked to the folder
        cursor.execute(''' 
            SELECT id, File_URL, file_type, name
            FROM Files 
            WHERE id IN (SELECT file_id FROM Folders_Files WHERE folder_id = ?)
        ''', (folder_id,))
        files = cursor.fetchall()

        # Copy files to the customer-folder with customized names
        for file in files:
            file_id, file_path, file_type, original_name = file

            # Ensure filename has no issues
            new_file_name = f"{original_name}_{id_number}" if '.' not in original_name else f"{original_name.split('.')[0]}_{id_number}.{original_name.split('.')[-1]}"

            cursor.execute(''' 
                INSERT INTO Customers_Files (folder_id, original_file_id, file_path, file_type, created_at, customer_file_name)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            ''', (customer_folder_id, file_id, file_path, file_type, new_file_name))

        conn.commit()
        current_app.logger.info(f"Folder ID {folder_id} and associated files successfully added to customer ID {customer_id}")  # Log success
        return jsonify({"message": "התיקייה והקבצים נוספו ללקוח בהצלחה!"}), 201
    except Exception as e:
        current_app.logger.error(f"Error adding folder ID {folder_id} to customer ID {customer_id}: {str(e)}")  # Log error
        conn.rollback()  # Rollback in case of error
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# Get all customer folders (from Customers_Folders)
@customer_folders_bp.route('/customer-folders', methods=['GET'])
@safe_route
@token_required(allowed_roles=["user", "manager", "admin"])
def get_all_customer_folders():
    current_app.logger.info("Request to retrieve all customer folders")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT cf.id AS customer_folder_id,
                   cf.customer_id,
                   c.first_name + ' ' + c.last_name AS customer_name,
                   cf.folder_id,
                   f.name AS folder_template_name,
                   cf.Folder_Name AS customer_folder_name
            FROM Customers_Folders cf
            JOIN Customers c ON cf.customer_id = c.id
            JOIN Folders f ON cf.folder_id = f.id
        ''')
        folders = dict_cursor(cursor)

        if folders:
            current_app.logger.info(f"Retrieved {len(folders)} customer folders")  # לוג הצלחה
            return jsonify({"customer_folders": folders}), 200
        else:
            current_app.logger.warning("No customer folders found")  # לוג ריק
            return jsonify({"message": "לא נמצאו תיקיות של לקוחות"}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving customer folders: {str(e)}")  # לוג שגיאה
        return jsonify({"message": "שגיאה בשרת, נסה שוב מאוחר יותר"}), 500
    finally:
        cursor.close()
        conn.close()