
from flask import Blueprint, request, jsonify
from ..database import get_db_connection

customers_bp = Blueprint('customers', __name__)  # יצירת Blueprint


@customers_bp.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not first_name or not last_name:
        return jsonify({"message": "Error: 'first_name' and 'last_name' are required"}), 400

    customer_details = {
        "id_number": data.get('id_number'),
        "first_name": first_name,
        "last_name": last_name,
        "email": data.get('email'),
        "phone": data.get('phone'),
        "password": data.get('password')
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT COUNT(*) FROM Customers WHERE email = ?', (customer_details['email'],))
        if cursor.fetchone()[0] > 0:
            return jsonify({"message": "Error: The email address already exists in the system."}), 400

        cursor.execute('SELECT COUNT(*) FROM Customers WHERE id_number = ?', (customer_details['id_number'],))
        if cursor.fetchone()[0] > 0:
            return jsonify({"message": "Error: The ID number already exists in the system."}), 400

        cursor.execute(''' 
            INSERT INTO Customers (id_number, first_name, last_name, email, phone, password)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_details['id_number'], first_name, last_name, 
              customer_details.get('email'), customer_details.get('phone'), customer_details.get('password')))

        customer_id = cursor.fetchone()[0]
        folder_ids = data.get('folder_ids', [])
        missing_ids = []
        
        if folder_ids:
            placeholders = ', '.join('?' for _ in folder_ids)
            cursor.execute(f'SELECT id FROM Folders WHERE id IN ({placeholders})', folder_ids)
            existing_folders = {row[0] for row in cursor.fetchall()}
            missing_ids = set(folder_ids) - existing_folders

            for folder_id in existing_folders:
                cursor.execute(''' 
                    INSERT INTO Customers_Folders (customer_id, folder_id, folder_name) 
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?)
                ''', (customer_id, folder_id, f"New Folder_{customer_details['id_number']}"))
                
                customer_folder_id = cursor.fetchone()[0]

                cursor.execute('SELECT file_id FROM Folders_Files WHERE folder_id = ?', (folder_id,))
                files = cursor.fetchall()
                
                for file in files:
                    file_id = file[0]
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
        
        conn.commit()
        return jsonify({"message": "Customer created successfully", "customer_id": customer_id}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
    finally:
        cursor.close()






#הצגת כל התיקיות של לקוח מסוים
@customers_bp.route('/customer/<int:customer_id>/folders', methods=['GET'])
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





#הצגת כל הקבצים של לקוח
@customers_bp.route('/customer/<int:customer_id>/files', methods=['GET'])
def get_customer_files(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # שליפת הקבצים שמשויכים ללקוח
        cursor.execute('''
            SELECT f.id AS file_id, f.name, f.file_type, f.File_URL
            FROM Customers_Folders cf
            JOIN Folders_Files ff ON cf.folder_id = ff.folder_id
            JOIN Files f ON ff.file_id = f.id
            WHERE cf.customer_id = ?
        ''', (customer_id,))

        files = cursor.fetchall()

        # אם יש קבצים
        if files:
            return jsonify({"files": [{"file_id": file[0], "name": file[1], "file_type": file[2], "File_URL": file[3]} for file in files]}), 200
        else:
            return jsonify({"message": "No files found for this customer."}), 201

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()


#מחיקת לקוח
@customers_bp.route('/customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # מציאת כל ה-folder_id של הלקוח
        cursor.execute('SELECT id FROM Customers_Folders WHERE customer_id = ?', (customer_id,))
        customer_folders = cursor.fetchall()
        print("customer_folders", customer_folders)

        # אם יש תיקיות ללקוח, נמחק את הקבצים הקשורים אליהם
        if customer_folders !=[]:
            # ממציאים את כל ה-folder_ids
            folder_ids = [folder[0] for folder in customer_folders]
            print("folder_ids", folder_ids)

             # מחיקת הקבצים בטבלת Customers_Files (שקשורים לתיקיות של הלקוח)
            cursor.execute('''
                DELETE FROM Customers_Files 
                WHERE folder_id IN ({})
            '''.format(','.join('?' * len(folder_ids))), folder_ids)
            print("Deleted files from Customers_Files")

            # מחיקת הקשר בין הלקוח לתיקיות בטבלת Customers_Folders
            cursor.execute('DELETE FROM Customers_Folders WHERE customer_id = ?', (customer_id,))
        
        # מחיקת הלקוח עצמו
        cursor.execute('DELETE FROM Customers WHERE id = ?', (customer_id,))

        conn.commit()
        return jsonify({"message": "Customer deleted successfully!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()




#הצגת כל הלקוחות
@customers_bp.route('/customers', methods=['GET'])
def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # שליפת כל הלקוחות
        cursor.execute('''
            SELECT id, id_number, first_name, last_name, email, phone
            FROM Customers
        ''')
        customers = cursor.fetchall()
        print("customers", customers)

        # אם יש לקוחות
        if len(customers) > 0:
            print("not null")
            return jsonify({
                "customers": [{"id": customer[0], "id_number": customer[1], "first_name": customer[2], 
                                "last_name": customer[3], "email": customer[4], "phone": customer[5]} for customer in customers]
            }), 200
        else:
            print("no items")
            return jsonify({"message": "No customers found."}), 201



    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()




# הצגת פרטי לקוח לפי ID
@customers_bp.route('/customer/<int:customer_id>', methods=['GET'], endpoint='get_customer_by_id')
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
            return jsonify({"message": f"Customer with ID {customer_id} not found."}), 201

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()





# עדכון פרטי לקוח
@customers_bp.route('/customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        new_email = data.get('email')
        new_id_number = data.get('id_number')

        # בדיקה אם האימייל כבר קיים אצל לקוח אחר
        if new_email:
            cursor.execute('SELECT id FROM Customers WHERE email = ? AND id <> ?', (new_email, customer_id))
            existing_customer = cursor.fetchone()
            if existing_customer:
                return jsonify({"message": "Error: Email address already exists in the system."}), 400

        # בדיקה אם מספר הזהות כבר קיים אצל לקוח אחר
        if new_id_number:
            cursor.execute('SELECT id FROM Customers WHERE id_number = ? AND id <> ?', (new_id_number, customer_id))
            existing_id_customer = cursor.fetchone()
            if existing_id_customer:
                return jsonify({"message": "Error: ID number already exists in the system."}), 400

        # עדכון הלקוח
        cursor.execute('''
            UPDATE Customers 
            SET id_number = ?, first_name = ?, last_name = ?, email = ?, phone = ?
            WHERE id = ?
        ''', (new_id_number, data.get('first_name'), data.get('last_name'), new_email, data.get('phone'), customer_id))

        conn.commit()
        return jsonify({"message": "Customer updated successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        cursor.close()




#הוספת תיקייה ללקוח+הוספת הקבצים
@customers_bp.route('/customer/<int:customer_id>/folder', methods=['POST'])
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



