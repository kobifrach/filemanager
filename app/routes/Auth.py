from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from ..utils.JWT import generate_token
from ..database.database import get_db_connection

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
    return user

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        token = generate_token(user['id'], user['user_type'], user['role'])
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid username or password'}), 401
