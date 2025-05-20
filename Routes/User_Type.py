from flask import Blueprint, request, jsonify, current_app
from ..database import get_db_connection
from browsepy.Utils.decorators import safe_route


userTypes_bp = Blueprint('userTypes', __name__)  # יצירת Blueprint


# יצירת סוג משתמש חדש
@userTypes_bp.route('/user_type', methods=['POST'])
@safe_route
def create_user_type():
    try:
        data = request.get_json()

        name = data.get('name', '')  # אם אין שם, יתקבל מחרוזת ריקה
        can_create_admin = data.get('can_create_admin', False)
        can_create_technician = data.get('can_create_technician', False)
        can_create_user = data.get('can_create_user', False)
        can_create_customer = data.get('can_create_customer', False)
        can_create_folder = data.get('can_create_folder', False)
        can_upload_file = data.get('can_upload_file', False)
        can_delete_customer = data.get('can_delete_customer', False)
        can_create_file = data.get('can_create_file', False)
        can_add_folder_type = data.get('can_add_folder_type', False)
        can_delete_file = data.get('can_delete_file', False)
        can_delete_folder_type = data.get('can_delete_folder_type', False)
        can_update_file = data.get('can_update_file', False)
        can_view_folder_types = data.get('can_view_folder_types', False)
        can_update_customer_details = data.get('can_update_customer_details', False)
        can_update_user_details = data.get('can_update_user_details', False)
        can_update_technician_details = data.get('can_update_technician_details', False)
        can_update_admin_details = data.get('can_update_admin_details', False)
        can_update_folder_details = data.get('can_update_folder_details', False)
        can_view_customers = data.get('can_view_customers', False)
        can_view_users = data.get('can_view_users', False)
        can_view_technicians = data.get('can_view_technicians', False)
        can_view_admins = data.get('can_view_admins', False)
        can_add_folder_to_customer = data.get('can_add_folder_to_customer', False)
        can_delete_folder_from_customer = data.get('can_delete_folder_from_customer', False)
        can_view_customer_folders = data.get('can_view_customer_folders', False)
        can_upload_documents_to_customer = data.get('can_upload_documents_to_customer', False)
        can_delete_documents_from_customer = data.get('can_delete_documents_from_customer', False)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO User_Type (name, can_create_admin, can_create_technician, can_create_user, can_create_customer,
                                   can_create_folder, can_upload_file, can_delete_customer, can_create_file,
                                   can_add_folder_type, can_delete_file, can_delete_folder_type,
                                   can_update_file, can_view_folder_types, can_update_customer_details, can_update_user_details,
                                   can_update_technician_details, can_update_admin_details, can_update_folder_details,
                                   can_view_customers, can_view_users, can_view_technicians, can_view_admins,
                                   can_add_folder_to_customer, can_delete_folder_from_customer, can_view_customer_folders,
                                   can_upload_documents_to_customer, can_delete_documents_from_customer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, can_create_admin, can_create_technician, can_create_user, can_create_customer, can_create_folder,
              can_upload_file, can_delete_customer, can_create_file, can_add_folder_type,
              can_delete_file, can_delete_folder_type, can_update_file, can_view_folder_types, can_update_customer_details,
              can_update_user_details, can_update_technician_details, can_update_admin_details, can_update_folder_details,
              can_view_customers, can_view_users, can_view_technicians, can_view_admins, can_add_folder_to_customer,
              can_delete_folder_from_customer, can_view_customer_folders, can_upload_documents_to_customer,
              can_delete_documents_from_customer))
        conn.commit()
        cursor.close()

        current_app.logger.info(f"User Type '{name}' created successfully.")
        return jsonify({"message": "User Type created successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Error creating user type: {e}")
        return jsonify({"message": "An error occurred while creating the user type"}), 500


# קריאה של כל סוגי המשתמשים
@userTypes_bp.route('/user_types', methods=['GET'])
@safe_route
def get_user_types():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User_Type')
        rows = cursor.fetchall()
        cursor.close()

        user_types = [{"id": row[0], "name": row[1]} for row in rows]
        current_app.logger.info(f"Retrieved {len(user_types)} user types.")
        return jsonify(user_types), 200

    except Exception as e:
        current_app.logger.error(f"Error retrieving user types: {e}")
        return jsonify({"message": "An error occurred while retrieving user types"}), 500


# עדכון סוג משתמש
@userTypes_bp.route('/user_type/<int:id>', methods=['PUT'])
@safe_route
def update_user_type(id):
    try:
        data = request.get_json()

        name = data.get('name', '')
        can_create_admin = data.get('can_create_admin', False)
        can_create_technician = data.get('can_create_technician', False)
        can_create_user = data.get('can_create_user', False)
        can_create_customer = data.get('can_create_customer', False)
        can_create_folder = data.get('can_create_folder', False)
        can_upload_file = data.get('can_upload_file', False)
        can_delete_customer = data.get('can_delete_customer', False)
        can_create_file = data.get('can_create_file', False)
        can_add_folder_type = data.get('can_add_folder_type', False)
        can_delete_file = data.get('can_delete_file', False)
        can_delete_folder_type = data.get('can_delete_folder_type', False)
        can_update_file = data.get('can_update_file', False)
        can_view_folder_types = data.get('can_view_folder_types', False)
        can_update_customer_details = data.get('can_update_customer_details', False)
        can_update_user_details = data.get('can_update_user_details', False)
        can_update_technician_details = data.get('can_update_technician_details', False)
        can_update_admin_details = data.get('can_update_admin_details', False)
        can_update_folder_details = data.get('can_update_folder_details', False)
        can_view_customers = data.get('can_view_customers', False)
        can_view_users = data.get('can_view_users', False)
        can_view_technicians = data.get('can_view_technicians', False)
        can_view_admins = data.get('can_view_admins', False)
        can_add_folder_to_customer = data.get('can_add_folder_to_customer', False)
        can_delete_folder_from_customer = data.get('can_delete_folder_from_customer', False)
        can_view_customer_folders = data.get('can_view_customer_folders', False)
        can_upload_documents_to_customer = data.get('can_upload_documents_to_customer', False)
        can_delete_documents_from_customer = data.get('can_delete_documents_from_customer', False)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE User_Type
            SET name = ?, can_create_admin = ?, can_create_technician = ?, can_create_user = ?, can_create_customer = ?,
                can_create_folder = ?, can_upload_file = ?, can_delete_customer = ?, can_create_file = ?, 
                can_add_folder_type = ?, can_delete_file = ?, can_delete_folder_type = ?, 
                can_update_file = ?, can_view_folder_types = ?, can_update_customer_details = ?, can_update_user_details = ?, 
                can_update_technician_details = ?, can_update_admin_details = ?, can_update_folder_details = ?, 
                can_view_customers = ?, can_view_users = ?, can_view_technicians = ?, can_view_admins = ?, 
                can_add_folder_to_customer = ?, can_delete_folder_from_customer = ?, can_view_customer_folders = ?, 
                can_upload_documents_to_customer = ?, can_delete_documents_from_customer = ?
            WHERE id = ?
        ''', (name, can_create_admin, can_create_technician, can_create_user, can_create_customer, can_create_folder,
              can_upload_file, can_delete_customer, can_create_file, can_add_folder_type,
              can_delete_file, can_delete_folder_type, can_update_file, can_view_folder_types, can_update_customer_details,
              can_update_user_details, can_update_technician_details, can_update_admin_details, can_update_folder_details,
              can_view_customers, can_view_users, can_view_technicians, can_view_admins, can_add_folder_to_customer,
              can_delete_folder_from_customer, can_view_customer_folders, can_upload_documents_to_customer,
              can_delete_documents_from_customer, id))
        conn.commit()
        cursor.close()

        current_app.logger.info(f"User Type with ID {id} updated successfully.")
        return jsonify({"message": "User Type updated successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating user type with ID {id}: {e}")
        return jsonify({"message": "An error occurred while updating the user type"}), 500


# מחיקת סוג משתמש
@userTypes_bp.route('/user_type/<int:id>', methods=['DELETE'])
@safe_route
def delete_user_type(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # בדיקה אם המשתמש קיים
        cursor.execute('SELECT COUNT(*) FROM User_Type WHERE id = ?', (id,))
        result = cursor.fetchone()

        if result[0] == 0:
            cursor.close()
            return jsonify({"message": "User Type not found"}), 404  # לא שגיאה, הודעה בלבד

        # אם המשתמש קיים - מבצעים מחיקה
        cursor.execute('DELETE FROM User_Type WHERE id = ?', (id,))
        conn.commit()
        cursor.close()

        current_app.logger.info(f"User Type with ID {id} deleted successfully.")
        return jsonify({"message": "User Type deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting user type with ID {id}: {e}")
        return jsonify({"message": "An error occurred while deleting the user type"}), 500
