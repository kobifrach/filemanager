from flask import Blueprint, jsonify, request
from ..database import get_db_connection

customer_folders_bp = Blueprint('customer_folders', __name__)


# Get all folders for a specific customer
@customer_folders_bp.route('/customer/<int:customer_id>/folders', methods=['GET'])
def get_customer_folders(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT f.id, f.name
            FROM Folders f
            JOIN Customers_Folders cf ON f.id = cf.folder_id
            WHERE cf.customer_id = ?
        ''', (customer_id,))

        folders = cursor.fetchall()
        folder_list = [{"id": folder[0], "name": folder[1]} for folder in folders]
        return jsonify({"folders": folder_list}), 200

    except Exception as e:
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()


# Delete a folder linked to a customer, including its associated files
@customer_folders_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>', methods=['DELETE'])
def delete_customer_folder(customer_id, folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Validate that the customer exists
        cursor.execute('SELECT id FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"message": "שגיאה: לקוח לא נמצא"}), 404

        # Validate that the folder exists for the customer
        cursor.execute('SELECT id FROM Customers_Folders WHERE customer_id = ? AND folder_id = ?', (customer_id, folder_id))
        folder = cursor.fetchone()
        if not folder:
            return jsonify({"message": "שגיאה: התיקייה לא משויכת ללקוח זה"}), 404

        customer_folder_id = folder[0]

        # Delete all files associated with this customer-folder
        cursor.execute('DELETE FROM Customers_Files WHERE folder_id = ?', (customer_folder_id,))

        # Delete the link between the customer and the folder
        cursor.execute('DELETE FROM Customers_Folders WHERE id = ?', (customer_folder_id,))

        conn.commit()
        return jsonify({"message": "התיקייה נמחקה בהצלחה!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()


# Add a generic folder and all its files to a specific customer
@customer_folders_bp.route('/customer/<int:customer_id>/folder', methods=['POST'])
def add_folder_to_customer(customer_id):
    data = request.get_json()
    folder_id = data.get('folder_id')

    if not folder_id or not isinstance(folder_id, int):
        return jsonify({"message": "שגיאה: חובה לציין מזהה תיקייה חוקי (folder_id)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Validate that the folder exists
        cursor.execute('SELECT id, name FROM Folders WHERE id = ?', (folder_id,))
        folder = cursor.fetchone()
        if not folder:
            return jsonify({"message": f"שגיאה: לא נמצאה תיקייה עם מזהה {folder_id}"}), 404

        # Validate that the customer exists and get their ID number
        cursor.execute('SELECT id_number FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"message": f"שגיאה: לא נמצא לקוח עם מזהה {customer_id}"}), 404

        id_number = customer[0]
        folder_name = f"{folder[1]}_{id_number}"

        # Insert new customer-folder link and get the generated ID
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
            if '.' in original_name:
                file_extension = original_name.split('.')[-1]
                file_base_name = '.'.join(original_name.split('.')[:-1])
                new_file_name = f"{file_base_name}_{id_number}.{file_extension}"
            else:
                new_file_name = f"{original_name}_{id_number}"

            cursor.execute('''
                INSERT INTO Customers_Files (folder_id, original_file_id, file_path, file_type, created_at, customer_file_name)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            ''', (customer_folder_id, file_id, file_path, file_type, new_file_name))

        conn.commit()
        return jsonify({"message": "התיקייה והקבצים נוספו ללקוח בהצלחה!"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()
