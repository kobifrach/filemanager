import requests
import json

# הגדרת ה-URL של ה-API שלך
url = 'http://127.0.0.1:5000/user_type'

# יצירת דתא שיישלח בבקשה
data = {
    'name': 'Admin',  # שם סוג המשתמש
    'can_create_admin': True,
    'can_create_technician': True,
    'can_create_user': True,
    'can_create_customer': True,
    'can_create_folder': True,
    'can_upload_file': True,
    'can_delete_customer': True
}

# שליחת הבקשה ל-API
response = requests.post(url, json=data)

# הדפסת התגובה
if response.status_code == 201:
    print("User Type created successfully!")
else:
    print(f"Error: {response.status_code} - {response.text}")
