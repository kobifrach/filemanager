from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
import pyodbc  # או כל דרייבר אחר של DB שלך
from ..utils.JWT import generate_token
from ..database.database import get_db_connection

auth_bp = Blueprint('auth', __name__)

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    # שאילתת UNION שמחזירה user_type ו-role לפי הטבלה
    query = """
    SELECT id, username, password_hash, 'user' AS user_type, role
    FROM Users
    WHERE email = ?
    UNION
    SELECT id, username, password_hash, 'customer' AS user_type, role
    FROM Customers
    WHERE email = ?
    """

    cursor.execute(query, (username, username))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    # המרת תוצאה לאובייקט או dict נוח לשימוש
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
