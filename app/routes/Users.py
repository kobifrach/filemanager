from flask import Blueprint, request, jsonify, current_app
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
from ..utils.jwt_decorator import token_required
import traceback
import secrets
import string
from werkzeug.security import generate_password_hash


users_bp = Blueprint('users', __name__)


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Create a new user
@users_bp.route('/api/user', methods=['POST'])
@safe_route
@token_required(allowed_roles=["admin","manager"])
def create_user():
    try:
        data = request.get_json()

        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        phone = data['phone']
        role = data.get('role', 'User')

        # יצירת סיסמה אקראית והצפנתה
        raw_password = generate_random_password()
        hashed_password = generate_password_hash(raw_password)

        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the role exists
        cursor.execute('SELECT id FROM User_Type WHERE name = ?', (role,))
        role_check = cursor.fetchone()
        if not role_check:
            return jsonify({"message": "Invalid role. User could not be created."}), 400

        # Check if the email already exists
        cursor.execute('SELECT id FROM Users WHERE email = ?', (email,))
        email_check = cursor.fetchone()
        if email_check:
            return jsonify({"message": f"Email {email} already exists. Please use a different email."}), 400

        # Perform the INSERT operation עם הסיסמה המוצפנת
        cursor.execute('''INSERT INTO Users (first_name, last_name, email, phone, role, password) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (first_name, last_name, email, phone, role, hashed_password))

        # Get the ID of the newly created user
        cursor.execute('SELECT id FROM Users WHERE email = ?', (email,))
        user_id = cursor.fetchone()[0]

        # Commit changes
        conn.commit()
        cursor.close()

        current_app.logger.info(f"User created successfully with ID: {user_id}.")

        # מחזירים את הסיסמה הגולמית יחד עם ההודעה
        return jsonify({
            "message": "משתמש נוצר בהצלחה", 
            "user_id": user_id,
            "password": raw_password
        }), 201

    except Exception as e:
        # In case of an error, perform rollback to cancel changes
        conn.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"message": "Error creating user."}), 500
    

# Fetch specific user details
@users_bp.route('/api/user/<int:id>', methods=['GET'])
@safe_route
@token_required(allowed_roles=["user","admin","manager"])
def get_user(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user details
        cursor.execute('''SELECT id, first_name, last_name, email, phone, role FROM Users WHERE id = ?''', (id,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({"message": "User not found"}), 404

        cursor.close()

        user_data = {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone": user[4],
            "role": user[5]
        }

        return jsonify(user_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching user with ID {id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"message": "Error fetching user."}), 500


# Fetch all users
@users_bp.route('/api/users', methods=['GET'])
@safe_route
@token_required(allowed_roles=["admin","manager"])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users')
        rows = cursor.fetchall()
        cursor.close()

        users = [{"id": row[0], "first_name": row[1], "last_name": row[2], "email": row[3], "phone": row[4], "role": row[5]} for row in rows]
        return jsonify(users), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching all users: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"message": "Error fetching users."}), 500


# Update user details
@users_bp.route('/api/user/<int:id>', methods=['PUT'])
@safe_route
@token_required(allowed_roles=["user","admin","manager"])

def update_user(id):
    print(f"Update user request received for ID: {id}")
    try:
        data = request.get_json()

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        role = data.get('role')
        password = data.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE Users
                          SET first_name = ?, last_name = ?, email = ?, phone = ?, role = ?, password = ?
                          WHERE id = ?''', 
                       (first_name, last_name, email, phone, role, password, id))

        conn.commit()
        cursor.close()

        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating user with ID {id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"message": "Error updating user."}), 500


# Delete a user
@users_bp.route('/api/user/<int:id>', methods=['DELETE'])
@safe_route
@token_required(allowed_roles=["user","admin","manager"])

def delete_user(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Users WHERE id = ?', (id,))
        conn.commit()
        cursor.close()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting user with ID {id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"message": "Error deleting user."}), 500