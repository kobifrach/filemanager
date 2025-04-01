#נבדק, עובד מושלם


from flask import Blueprint, request, jsonify
from ..database import get_db_connection

users_bp = Blueprint('users', __name__)  # יצירת Blueprint

# יצירת משתמש חדש
@users_bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone = data['phone']
    password = data['password']
    
    # קבלת התפקיד, אם לא נמסר תפקיד ברירת המחדל היא 'User'
    role = data.get('role', 'User')

    # חיבור לבסיס נתונים
    conn = get_db_connection()
    cursor = conn.cursor()

    # בדיקת אם התפקיד שנמסר קיים בטבלת User_Type
    cursor.execute('SELECT id FROM User_Type WHERE name = ?', (role,))
    role_check = cursor.fetchone()

    # אם התפקיד לא קיים בטבלה, מחזירים הודעת שגיאה
    if not role_check:
        return jsonify({"message": "Invalid role. User could not be created."}), 400

    # בדיקת אם המייל כבר קיים
    cursor.execute('SELECT id FROM Users WHERE email = ?', (email,))
    email_check = cursor.fetchone()

    # אם המייל קיים, מחזירים הודעה מתאימה
    if email_check:
        return jsonify({"message": f"Email {email} already exists. Please use a different email."}), 400

    # ביצוע ה-INSERT עם התפקיד שנבדק
    cursor.execute('''
        INSERT INTO Users (first_name, last_name, email, phone, role, password)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, email, phone, role, password))

    # קבלת ה-ID של המשתמש החדש
    cursor.execute('SELECT id FROM Users WHERE email = ?', (email,))
    user_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()

    return jsonify({"message": "User created successfully", "user_id": user_id}), 201


# הצגת פרטי משתמש ספציפי
@users_bp.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # קבלת פרטי משתמש
    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, role FROM Users WHERE id = ?
    ''', (id,))
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

# הצגת כל המשתמשים
@users_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    rows = cursor.fetchall()
    cursor.close()
    
    users = [{"id": row[0], "first_name": row[1], "last_name": row[2], "email": row[3], "phone": row[4], "role": row[5]} for row in rows]
    return jsonify(users), 200

# עדכון פרטי משתמש
@users_bp.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Users
        SET first_name = ?, last_name = ?, email = ?, phone = ?, role = ?, password = ?
        WHERE id = ?
    ''', (first_name, last_name, email, phone, role, password, id))
    conn.commit()
    cursor.close()

    return jsonify({"message": "User updated successfully"}), 200

# מחיקת משתמש
@users_bp.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE id = ?', (id,))
    conn.commit()
    cursor.close()

    return jsonify({"message": "User deleted successfully"}), 200
