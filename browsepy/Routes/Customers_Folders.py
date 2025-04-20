#הכל עובד

from flask import Blueprint, jsonify, request
from ..database import get_db_connection

customer_folders_bp = Blueprint('customer_folders', __name__)


#הצגת כל התיקיות של לקוח מסוים
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
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()





#מחיקת תיקייה ללקוחVVVVV
@customer_folders_bp.route('/customer/<int:customer_id>/folder/<int:folder_id>', methods=['DELETE'])
def delete_customer_folder(customer_id, folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("123456789")
        # בדיקה אם הלקוח קיים
        cursor.execute('SELECT id FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            print("not customer")
            return jsonify({"message": "Error: Customer not found"}), 400

        # בדיקה אם תיקייה קיימת עבור הלקוח
        cursor.execute('SELECT id FROM Customers_Folders WHERE customer_id = ? AND folder_id = ?', (customer_id, folder_id))
        folder = cursor.fetchone()
        if not folder:
            print("not folder")
            return jsonify({"message": "Error: Folder not found for this customer"}), 400

        customer_folder_id = folder[0]

        # מחיקת קבצים הקשורים לתיקייה
        cursor.execute('DELETE FROM Customers_Files WHERE folder_id = ?', (customer_folder_id,))

        # מחיקת הקשר לתיקייה
        cursor.execute('DELETE FROM Customers_Folders WHERE id = ?', (customer_folder_id,))

        conn.commit()
        return jsonify({"message": "Folder deleted successfully!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()





#הוספת תיקייה ללקוח+הוספת הקבציםVVVVVVVVVVVVVV
@customer_folders_bp.route('/customer/<int:customer_id>/folder', methods=['POST'])
def add_folder_to_customer(customer_id):
    data = request.get_json()
    folder_id = data.get('folder_id')

    if not folder_id:
        return jsonify({"message": "Error: 'folder_id' is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # בדיקה אם התיקייה קיימת
        cursor.execute('SELECT id, name FROM Folders WHERE id = ?', (folder_id,))
        folder = cursor.fetchone()
        if not folder:
            return jsonify({"message": f"Error: Folder with ID {folder_id} does not exist"}), 400

        # קבלת מספר הזהות של הלקוח
        cursor.execute('SELECT id_number FROM Customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"message": f"Error: Customer with ID {customer_id} does not exist"}), 400
        
        id_number = customer[0]  # מספר הזהות של הלקוח
        folder_name = f"{folder[1]}_{id_number}"  # שם התיקייה החדשה

        # הוספת קשר בין הלקוח לתיקייה
        cursor.execute('''
            INSERT INTO Customers_Folders (customer_id, folder_id, Folder_Name) 
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        ''', (customer_id, folder_id, folder_name))
        customer_folder_id = cursor.fetchone()[0]  # קבלת ה-ID החדש של התיקייה שנוצרה

        # קבלת כל הקבצים הקשורים לתיקייה הזו
        cursor.execute('''
            SELECT id, File_URL, file_type, name FROM Files 
            WHERE id IN (SELECT file_id FROM Folders_Files WHERE folder_id = ?)
        ''', (folder_id,))
        files = cursor.fetchall()

        # הוספת קשרים בין הלקוח לקבצים
        for file in files:
            file_id, file_path, file_type, original_name = file
            
            # יצירת שם חדש לקובץ
            file_extension = original_name.split('.')[-1]  # סיומת הקובץ
            file_base_name = '.'.join(original_name.split('.')[:-1])  # שם הקובץ בלי הסיומת
            new_file_name = f"{file_base_name}_{id_number}.{file_extension}"  # שם חדש עם מספר זהות

            cursor.execute('''
                INSERT INTO Customers_Files (folder_id, original_file_id, file_path, file_type, created_at, customer_file_name)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            ''', (customer_folder_id, file_id, file_path, file_type, new_file_name))

        conn.commit()
        return jsonify({"message": "Folder and files added to customer successfully!"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()