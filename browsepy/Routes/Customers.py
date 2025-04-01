
from flask import Blueprint, request, jsonify
from ..database import get_db_connection

customers_bp = Blueprint('customers', __name__)  # יצירת Blueprint
@customers_bp.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    id_number = data['id_number']
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone = data['phone']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Customers (id_number, first_name, last_name, email, phone)
        VALUES (?, ?, ?, ?, ?)
    ''', (id_number, first_name, last_name, email, phone))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer created successfully"}), 201

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Customers')
    rows = cursor.fetchall()
    cursor.close()
    
    customers = [{"id": row[0], "first_name": row[2], "last_name": row[3], "email": row[4]} for row in rows]
    return jsonify(customers), 200

@customers_bp.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone = data['phone']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Customers
        SET first_name = ?, last_name = ?, email = ?, phone = ?
        WHERE id = ?
    ''', (first_name, last_name, email, phone, id))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer updated successfully"}), 200

@customers_bp.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Customers WHERE id = ?', (id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer deleted successfully"}), 200
