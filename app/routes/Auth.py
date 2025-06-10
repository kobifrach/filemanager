from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from ..utils.JWT import generate_token
from ..database.database import get_db_connection
from ..utils.decorators import safe_route
from ..utils.jwt_decorator import token_required

auth_bp = Blueprint('auth', __name__)

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, email AS username, password, 'user' AS user_type, role
    FROM Users
    WHERE email = ?
    UNION
    SELECT id, email AS username, password, 'customer' AS user_type, role
    FROM Customers
    WHERE email = ?
    """

    cursor.execute(query, (username, username))
    row = cursor.fetchone()
    print("row", row)  # Debugging line to check the retrieved row
    if not row:
        print(f"No user found with username: {username}")  # Debugging line if no user is found
    cursor.close()
    conn.close()

    if not row:
        return None

    user = {
        'id': row[0],
        'username': row[1],
        'password_hash': row[2],
        'user_type': row[3],
        'role': row[4]
    }
    print(f"Retrieved user: {user}")  # Debugging line to check the retrieved user
    return user

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        # אם role ריק או None – נחזיר במקום זה את user_type
        role_or_type = user['role'] if user['role'] else user['user_type']

        token = generate_token(user['id'], user['username'], role_or_type)

        return jsonify({
            'token': token,
            'userId': user['id'],
            'username': user['username'],
            'role': role_or_type
        })

    return jsonify({'error': 'Invalid username or password'}), 401


#reset password endpoint
@auth_bp.route('/auth/reset-password/<int:id>', methods=['POST'])
@safe_route
@token_required(allowed_roles=["user","admin","manager"])
def reset_password(id):
    return jsonify({"message": "Reset password functionality not implemented yet"}), 200

  
