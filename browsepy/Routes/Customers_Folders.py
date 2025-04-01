from flask import Blueprint, request, jsonify
from ..database import get_db_connection

customersFolders_bp = Blueprint('customersFolders', __name__)  # יצירת Blueprint

@customersFolders_bp.route('/customer_folder', methods=['POST'])
def create_customer_folder():
    data = request.get_json()
    customer_id = data['customer_id']
    folder_id = data['folder_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Customers_Folders (customer_id, folder_id)
        VALUES (?, ?)
    ''', (customer_id, folder_id))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer Folder created successfully"}), 201

@customersFolders_bp.route('/customer_folders', methods=['GET'])
def get_customer_folders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Customers_Folders')
    rows = cursor.fetchall()
    cursor.close()
    
    customer_folders = [{"id": row[0], "customer_id": row[1], "folder_id": row[2]} for row in rows]
    return jsonify(customer_folders), 200

@customersFolders_bp.route('/customer_folder/<int:id>', methods=['DELETE'])
def delete_customer_folder(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Customers_Folders WHERE id = ?', (id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer Folder deleted successfully"}), 200
