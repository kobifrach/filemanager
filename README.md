# filemanager
# 📌 Flask API לניהול משתמשים ותיקיות

## 📖 מבוא
API מבוסס Flask לניהול משתמשים, תיקיות וקבצים במערכת.

---

## ⚙️ התקנה

### 📦 התקנת הספריות הנדרשות:
```bash
pip install flask sqlite3
```

### 🚀 הפעלת השרת:
```bash
flask run
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
