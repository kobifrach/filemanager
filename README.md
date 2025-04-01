# filemanager
# 📌 Flask API לניהול משתמשים ותיקיות

## 📖 מבוא
API מבוסס Flask לניהול משתמשים, תיקיות וקבצים במערכת.

---

## ⚙️ התקנה

### 📦 התקנת הספריות הנדרשות:
```bash
pip install flask flask-sqlalchemy flask-migrate flask-cors
```

### 🔧 הגדרת מסד הנתונים:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### 🚀 הפעלת השרת:
```bash
flask run
```

---

## 🛠️ מבנה מסד הנתונים (SQL Server)

### 🔹 טבלת משתמשים (`users`)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    first_name NVARCHAR(50),
    last_name NVARCHAR(50),
    email NVARCHAR(100) UNIQUE,
    phone NVARCHAR(20),
    password NVARCHAR(255),
    role NVARCHAR(20)
);
```

### 🔹 טבלת תיקיות (`folders`)
```sql
CREATE TABLE folders (
    id INT PRIMARY KEY IDENTITY(1,1),
    folder_name NVARCHAR(100),
    folder_description NVARCHAR(255)
);
```

---

## 🔗 ראוטים זמינים

### 📂 ניהול תיקיות

#### ✨ יצירת תיקייה
📌 **בקשה:**
```
POST /folder
```
📌 **גוף הבקשה (JSON):**
```json
{
  "folder_name": "מסמכים חשובים",
  "folder_description": "תיקייה למסמכים רגישים",
  "file_ids": [1, 2, 3]
}
```
📌 **תגובת שרת:**
```json
{
  "message": "Folder created successfully",
  "folder_id": 1
}
```

#### 📜 קבלת כל התיקיות
📌 **בקשה:**
```
GET /folders
```
📌 **תגובת שרת:**
```json
[
  { "id": 1, "name": "מסמכים", "description": "תיק כללי" },
  { "id": 2, "name": "חשבוניות", "description": "חשבוניות חודשיות" }
]
```

#### ❌ מחיקת תיקייה
📌 **בקשה:**
```
DELETE /folder/<folder_id>
```
📌 **תגובת שרת:**
```json
{
  "message": "Folder deleted successfully"
}
```

---

### 👤 ניהול משתמשים

#### ➕ יצירת משתמש
📌 **בקשה:**
```
POST /user
```
📌 **גוף הבקשה (JSON):**
```json
{
  "first_name": "ישראל",
  "last_name": "כהן",
  "email": "israel@example.com",
  "phone": "050-1234567",
  "password": "123456",
  "role": "Admin"
}
```
📌 **תגובת שרת:**
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

#### 📋 קבלת כל המשתמשים
📌 **בקשה:**
```
GET /users
```
📌 **תגובת שרת:**
```json
[
  { "id": 1, "first_name": "ישראל", "last_name": "כהן", "email": "israel@example.com", "phone": "050-1234567", "role": "Admin" },
  { "id": 2, "first_name": "דוד", "last_name": "לוי", "email": "david@example.com", "phone": "050-7654321", "role": "User" }
]
```

#### 🗑️ מחיקת משתמש
📌 **בקשה:**
```
DELETE /user/<user_id>
```
📌 **תגובת שרת:**
```json
{
  "message": "User deleted successfully"
}
```

---

## 🔚 סיכום
API פשוט לניהול משתמשים, תיקיות וקבצים. ניתן להרחיב ולהוסיף יכולות נוספות לפי הצורך.

