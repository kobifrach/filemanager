from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
import secrets
import string
from werkzeug.security import generate_password_hash
import re  # Import regex module for email validation

customers_bp = Blueprint('customers', __name__)  # Blueprint definition for customer-related routes

# Function to validate email
def validate_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Create a new customer
@customers_bp.route('/customer', methods=['POST'])
@safe_route
def create_customer():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    if not first_name or not last_name:
        return jsonify({"message": "שגיאה: יש להזין שם פרטי ושם משפחה."}), 400
    
    if not email or not validate_email(email):
        return jsonify({"message": "שגיאה: כתובת האימייל אינה תקינה."}), 400

    customer_details = {
        "id_number": data.get('id_number'),
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": data.get('phone'),
        "password": data.get('password')
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check for email uniqueness
        cursor.execute('SELECT COUNT(*) FROM Customers WHERE email = ?', (customer_details['email'],))
        if cursor.fetchone()[0] > 0:
            return jsonify({"message": "שגיאה: כתובת האימייל כבר קיימת במערכת."}), 400

        # Check for ID number uniqueness
        cursor.execute('SELECT COUNT(*) FROM Customers WHERE id_number = ?', (customer_details['id_number'],))
        if cursor.fetchone()[0] > 0:
            return jsonify({"message": "שגיאה: מספר תעודת הזהות כבר קיים במערכת."}), 400

        # Insert new customer and return inserted ID
        cursor.execute(''' 
            INSERT INTO Customers (id_number, first_name, last_name, email, phone, password)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_details['id_number'], first_name, last_name, 
              customer_details.get('email'), customer_details.get('phone'), customer_details.get('password')))

        customer_id = cursor.fetchone()[0]
        folder_ids = data.get('folder_ids', [])

        if folder_ids:
            placeholders = ', '.join('?' for _ in folder_ids)
            cursor.execute(f'SELECT id FROM Folders WHERE id IN ({placeholders})', folder_ids)
            existing_folders = {row[0] for row in cursor.fetchall()}
            missing_ids = set(folder_ids) - existing_folders

            for folder_id in existing_folders:
                # Link customer to selected folders
                cursor.execute(''' 
                    INSERT INTO Customers_Folders (customer_id, folder_id, folder_name) 
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?)
                ''', (customer_id, folder_id, f"New Folder_{customer_details['id_number']}"))

                customer_folder_id = cursor.fetchone()[0]

                # Copy relevant files into customer's folder
                cursor.execute('SELECT file_id FROM Folders_Files WHERE folder_id = ?', (folder_id,))
                for (file_id,) in cursor.fetchall():
                    cursor.execute('SELECT name, File_URL, file_type FROM Files WHERE id = ?', (file_id,))
                    file_data = cursor.fetchone()

                    if file_data:
                        file_name, file_path, file_type = file_data
                        file_parts = file_name.rsplit('.', 1)
                        new_file_name = f"{file_parts[0]}_{customer_details['id_number']}.{file_parts[1]}" if len(file_parts) == 2 else f"{file_name}_{customer_details['id_number']}"

                        cursor.execute(''' 
                            INSERT INTO Customers_Files (folder_id, original_file_id, file_path, file_type, created_at, customer_file_name)
                            VALUES (?, ?, ?, ?, GETDATE(), ?)
                        ''', (customer_folder_id, file_id, file_path, file_type, new_file_name))

                current_app.logger.info(f"Folder ID {folder_id} and associated files successfully added to customer ID {customer_id}")  # Log success

        conn.commit()
        current_app.logger.info(f"Customer ID {customer_id} created successfully")  # Log creation
        return jsonify({"message": "הלקוח נוצר בהצלחה", "customer_id": customer_id}), 201

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error creating customer: {str(e)}")  # Log error
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()

# Delete customer and associated records
@customers_bp.route('/customer/<int:customer_id>', methods=['DELETE'])
@safe_route
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM Customers_Folders WHERE customer_id = ?', (customer_id,))
        customer_folders = cursor.fetchall()

        if customer_folders:
            folder_ids = [folder[0] for folder in customer_folders]

            cursor.execute(''' 
                DELETE FROM Customers_Files 
                WHERE folder_id IN ({}) 
            '''.format(','.join('?' * len(folder_ids))), folder_ids)

            cursor.execute('DELETE FROM Customers_Folders WHERE customer_id = ?', (customer_id,))

        cursor.execute('DELETE FROM Customers WHERE id = ?', (customer_id,))

        conn.commit()
        current_app.logger.info(f"Customer ID {customer_id} deleted successfully")  # Log success
        return jsonify({"message": "הלקוח נמחק בהצלחה!"}), 200

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error deleting customer ID {customer_id}: {str(e)}")  # Log error
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()

# Get all customers
@customers_bp.route('/customers', methods=['GET'])
@safe_route
def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(''' 
            SELECT id, id_number, first_name, last_name, email, phone 
            FROM Customers 
        ''')
        customers = cursor.fetchall()

        if customers:
            current_app.logger.info("Retrieved all customers successfully")
            return jsonify({
                "customers": [
                    {
                        "id": customer[0],
                        "id_number": customer[1],
                        "first_name": customer[2],
                        "last_name": customer[3],
                        "email": customer[4],
                        "phone": customer[5]
                    } for customer in customers
                ]
            }), 200
        else:
            current_app.logger.info("No customers found")
            return jsonify({"message": "לא נמצאו לקוחות."}), 204

    except Exception as e:
        current_app.logger.error(f"Error retrieving customers: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()

# Get specific customer by ID
@customers_bp.route('/customer/<int:customer_id>', methods=['GET'], endpoint='get_customer_by_id')
@safe_route
def get_customer_by_id(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(''' 
            SELECT id, id_number, first_name, last_name, email, phone 
            FROM Customers 
            WHERE id = ? 
        ''', (customer_id,))
        customer = cursor.fetchone()

        if customer:
            current_app.logger.info(f"Customer ID {customer_id} retrieved successfully")
            return jsonify({
                "customer": {
                    "id": customer[0],
                    "id_number": customer[1],
                    "first_name": customer[2],
                    "last_name": customer[3],
                    "email": customer[4],
                    "phone": customer[5]
                }
            }), 200
        else:
            current_app.logger.warning(f"Customer ID {customer_id} not found")
            return jsonify({"message": f"לקוח עם מזהה {customer_id} לא נמצא."}), 404

    except Exception as e:
        current_app.logger.error(f"Error retrieving customer ID {customer_id}: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()

# Update customer details
@customers_bp.route('/customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        data = request.get_json()
        new_email = data.get('email')
        new_id_number = data.get('id_number')

        if new_email:
            cursor.execute('SELECT id FROM Customers WHERE email = ? AND id <> ?', (new_email, customer_id))
            if cursor.fetchone():
                return jsonify({"message": "שגיאה: כתובת האימייל כבר קיימת במערכת."}), 400

        if new_id_number:
            cursor.execute('SELECT id FROM Customers WHERE id_number = ? AND id <> ?', (new_id_number, customer_id))
            if cursor.fetchone():
                return jsonify({"message": "שגיאה: מספר תעודת הזהות כבר קיים במערכת."}), 400

        cursor.execute(''' 
            UPDATE Customers 
            SET id_number = ?, first_name = ?, last_name = ?, email = ?, phone = ? 
            WHERE id = ? 
        ''', (new_id_number, data.get('first_name'), data.get('last_name'), new_email, data.get('phone'), customer_id))

        conn.commit()
        current_app.logger.info(f"Customer ID {customer_id} updated successfully")
        return jsonify({"message": "פרטי הלקוח עודכנו בהצלחה."}), 200

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating customer ID {customer_id}: {str(e)}")
        return jsonify({"message": f"שגיאה: {str(e)}"}), 500

    finally:
        cursor.close()
