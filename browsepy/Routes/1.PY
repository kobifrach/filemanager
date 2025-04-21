# from flask import Blueprint, request, jsonify
# from ..database import get_db_connection

# duplicate_folder_bp = Blueprint('duplicate_folder', __name__)  # יצירת Blueprint
# #פונקציה זו יוצרת עותק של תיקייה קיימת, כולל כל הקבצים המשויכים אליה.
# @duplicate_folder_bp.route('/duplicate_folder', methods=['POST'])
# def duplicate_folder():
#     data = request.get_json()
#     folder_id = data.get('folder_id')
#     new_folder_name = data.get('new_folder_name')

#     if not folder_id or not new_folder_name:
#         return jsonify({"error": "חסר מידע הכרחי"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # שליפת פרטי התיקייה המקורית
#     cursor.execute('SELECT name, description FROM Folders WHERE id = ?', (folder_id,))
#     original_folder = cursor.fetchone()

#     if not original_folder:
#         return jsonify({"error": "התיקייה לא נמצאה"}), 404

#     # יצירת תיקייה חדשה עם השם החדש
#     cursor.execute('INSERT INTO Folders (name, description) VALUES (?, ?)', (new_folder_name, original_folder[1]))
#     conn.commit()

#     # קבלת ה-ID של התיקייה החדשה
#     new_folder_id = cursor.lastrowid

#     # שליפת כל הקבצים מהתיקייה המקורית
#     cursor.execute('SELECT file_id FROM Folders_Files WHERE folder_id = ?', (folder_id,))
#     files = cursor.fetchall()

#     # הוספת כל הקבצים לתיקייה החדשה
#     for file in files:
#         cursor.execute('INSERT INTO Folders_Files (folder_id, file_id) VALUES (?, ?)', (new_folder_id, file[0]))

#     conn.commit()
#     cursor.close()

#     return jsonify({"message": "התיקייה שוכפלה בהצלחה", "new_folder_id": new_folder_id}), 200

# #------------------------------------------------------------

# from flask import Blueprint, request, jsonify
# from ..database import get_db_connection

# move_file_bp = Blueprint('move_file', __name__)  # יצירת Blueprint
# # פונקציה זו מאפשרת למשתמש להעביר קובץ מתיקייה אחת לאחרת מבלי לשכפל אותו.
# @move_file_bp.route('/move_file', methods=['POST'])
# def move_file():
#     data = request.get_json()
#     file_id = data.get('file_id')
#     source_folder_id = data.get('source_folder_id')
#     target_folder_id = data.get('target_folder_id')

#     if not file_id or not source_folder_id or not target_folder_id:
#         return jsonify({"error": "חסר מידע הכרחי"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # בדיקה אם הקובץ נמצא בתיקיית המקור
#     cursor.execute('SELECT * FROM Folders_Files WHERE folder_id = ? AND file_id = ?', (source_folder_id, file_id))
#     file_in_source = cursor.fetchone()

#     if not file_in_source:
#         return jsonify({"error": "הקובץ לא נמצא בתיקיית המקור"}), 404

#     # מחיקת הקובץ מתיקיית המקור
#     cursor.execute('DELETE FROM Folders_Files WHERE folder_id = ? AND file_id = ?', (source_folder_id, file_id))

#     # הוספת הקובץ לתיקיית היעד
#     cursor.execute('INSERT INTO Folders_Files (folder_id, file_id) VALUES (?, ?)', (target_folder_id, file_id))

#     conn.commit()
#     cursor.close()

#     return jsonify({"message": "הקובץ הועבר בהצלחה"}), 200


# #---------------------------------------------------------------

# from flask import Blueprint, request, jsonify
# from ..database import get_db_connection
# # פונקציה שמאפשרת חיפוש לפי שם, סוג קובץ, או תאריך יצירה, עם אופציה לסינון לפי תיקייה או משתמש.
# search_bp = Blueprint('search', __name__)  # יצירת Blueprint

# @search_bp.route('/search', methods=['GET'])
# def search_files_and_folders():
#     name = request.args.get('name', '')
#     file_type = request.args.get('file_type', '')
#     customer_id = request.args.get('customer_id', None)
#     folder_id = request.args.get('folder_id', None)

#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     query = '''
#         SELECT f.id, f.name, f.file_type, f.File_URL, 'file' AS type
#         FROM Files f
#         WHERE (f.name LIKE ? OR ? = '')
#         AND (f.file_type LIKE ? OR ? = '')
#     '''
#     params = [f'%{name}%', name, f'%{file_type}%', file_type]

#     if folder_id:
#         query += ' AND f.id IN (SELECT file_id FROM Folders_Files WHERE folder_id = ?)'
#         params.append(folder_id)

#     query += '''
#         UNION ALL
#         SELECT fo.id, fo.name, NULL AS file_type, NULL AS File_URL, 'folder' AS type
#         FROM Folders fo
#         WHERE (fo.name LIKE ? OR ? = '')
#     '''
#     params.extend([f'%{name}%', name])

#     if customer_id:
#         query += ' AND fo.id IN (SELECT folder_id FROM Customers_Folders WHERE customer_id = ?)'
#         params.append(customer_id)

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     cursor.close()

#     items = [{"id": row[0], "name": row[1], "file_type": row[2], "file_url": row[3], "type": row[4]} for row in results]

#     return jsonify(items), 200


# #------------------------------------------------------------

# from flask import Blueprint, jsonify
# from ..database import get_db_connection
# # פונקציה זו מחזירה את מבנה התיקיות בצורה היררכית, כך שניתן לראות אילו תיקיות מקוננות בתוך אחרות.
# folders_hierarchy_bp = Blueprint('folders_hierarchy', __name__)  # יצירת Blueprint

# @folders_hierarchy_bp.route('/folders/hierarchy', methods=['GET'])
# def get_folders_hierarchy():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # שליפת כל התיקיות מהמערכת
#     cursor.execute('SELECT id, name FROM Folders')
#     folders = cursor.fetchall()

#     # שליפת כל הקשרים של תיקיות מקוננות (לדוגמה: תיקיית על -> תת-תיקייה)
#     cursor.execute('SELECT folder_id, parent_folder_id FROM Folder_Hierarchy')  # נדרש ליצור טבלה זו
#     hierarchy = cursor.fetchall()
    
#     cursor.close()
    
#     # בניית מבנה היררכי
#     folder_dict = {folder[0]: {"id": folder[0], "name": folder[1], "subfolders": []} for folder in folders}
    
#     for folder_id, parent_id in hierarchy:
#         if parent_id in folder_dict:
#             folder_dict[parent_id]["subfolders"].append(folder_dict[folder_id])

#     # חיפוש תיקיות עליונות שאין להן הורה (Root folders)
#     root_folders = [folder for folder in folder_dict.values() if all(folder["id"] != h[0] for h in hierarchy)]
    
#     return jsonify(root_folders), 200

# # 📌 מה עושה הפונקציה?
# # 🔹 טוענת את כל התיקיות ממסד הנתונים.
# # 🔹 יוצרת מבנה היררכי בעזרת מילון Python.
# # 🔹 מחזירה JSON שמציג את הקשרים בין התיקיות.

# # 🛠 שימו לב: פונקציה זו מסתמכת על טבלה Folder_Hierarchy שיש לה שדות folder_id ו- parent_folder_id.
# # אם היא לא קיימת במסד הנתונים, צריך להוסיף אותה כדי לתמוך בתיקיות מקוננות.

# #----------------------------------------------------------------------

# from flask import Blueprint, request, jsonify
# from ..database import get_db_connection
# # פונקציה זו מאפשרת להגדיר למי יש גישה לכל קובץ או תיקייה על ידי שמירת ההרשאות בטבלת Permissions.
# permissions_bp = Blueprint('permissions', __name__)  # יצירת Blueprint

# # הוספת הרשאה למשתמש עבור קובץ או תיקייה
# @permissions_bp.route('/permissions', methods=['POST'])
# def add_permission():
#     data = request.json
#     user_id = data.get("user_id")
#     folder_id = data.get("folder_id")
#     file_id = data.get("file_id")
#     can_view = data.get("can_view", False)
#     can_edit = data.get("can_edit", False)
#     can_delete = data.get("can_delete", False)

#     if not user_id or (not folder_id and not file_id):
#         return jsonify({"error": "user_id ו-folder_id/file_id נדרשים"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO Permissions (user_id, folder_id, file_id, can_view, can_edit, can_delete)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (user_id, folder_id, file_id, can_view, can_edit, can_delete))
#     conn.commit()
#     cursor.close()

#     return jsonify({"message": "הרשאה נוספה בהצלחה"}), 201


# # קבלת הרשאות למשתמש מסוים
# @permissions_bp.route('/permissions/user/<int:user_id>', methods=['GET'])
# def get_user_permissions(user_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         SELECT * FROM Permissions WHERE user_id = ?
#     ''', (user_id,))
#     rows = cursor.fetchall()
#     cursor.close()

#     permissions = [{"id": row[0], "user_id": row[1], "folder_id": row[2], "file_id": row[3], 
#                     "can_view": row[4], "can_edit": row[5], "can_delete": row[6]} for row in rows]
    
#     return jsonify(permissions), 200


# # שינוי בעלות על קובץ או תיקייה
# @permissions_bp.route('/permissions/change_owner', methods=['PUT'])
# def change_owner():
#     data = request.json
#     old_user_id = data.get("old_user_id")
#     new_user_id = data.get("new_user_id")
#     folder_id = data.get("folder_id")
#     file_id = data.get("file_id")

#     if not old_user_id or not new_user_id or (not folder_id and not file_id):
#         return jsonify({"error": "old_user_id, new_user_id ו-folder_id/file_id נדרשים"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         UPDATE Permissions SET user_id = ? 
#         WHERE user_id = ? AND (folder_id = ? OR file_id = ?)
#     ''', (new_user_id, old_user_id, folder_id, file_id))
#     conn.commit()
#     cursor.close()

#     return jsonify({"message": "הבעלות שונתה בהצלחה"}), 200
# # 📌 מה עושה הפונקציה?
# # 🔹 מאפשרת להוסיף הרשאות למשתמשים על קבצים ותיקיות.
# # 🔹 מאפשרת לשלוף את כל ההרשאות של משתמש מסוים.
# # 🔹 מאפשרת לשנות בעלות על קובץ או תיקייה למשתמש אחר.

# # 🛠 שימו לב: פונקציה זו מבוססת על טבלת Permissions עם השדות:

# # user_id – מזהה המשתמש.

# # folder_id או file_id – מזהה התיקייה או הקובץ.

# # can_view, can_edit, can_delete – הרשאות גישה.

# #-------------------------------------------------------------------

