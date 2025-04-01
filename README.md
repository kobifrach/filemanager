# filemanager
# README - מערכת ניהול משתמשים ותיקיות ב-Flask

## התקנה והגדרה

### דרישות מערכת:
- Python 3.8+
- Flask
- SQLite (או מסד נתונים אחר נתמך)

### התקנת התלויות:
```
pip install flask
```

### הרצת השרת:
```
flask run
```

## מסלולי API

### 1. ניהול תיקיות (Folders)

#### יצירת תיקייה חדשה
**בקשה:**
```
POST /folder
{
  "folder_name": "שם התיקייה",
  "folder_description": "תיאור אופציונלי",
  "file_ids": [1, 2, 3]
}
```
**תגובה:**
```
{
  "message": "Folder created successfully",
  "folder_id": 1
}
```

#### הצגת תיקייה מסוימת
**בקשה:**
```
GET /folder/{id}
```
**תגובה:**
```
{
  "id": 1,
  "name": "שם התיקייה",
  "description": "תיאור אופציונלי",
  "file_ids": [1, 2, 3]
}
```

#### עדכון תיקייה
**בקשה:**
```
PUT /folder/{id}
{
  "folder_name": "שם חדש",
  "folder_description": "תיאור חדש"
}
```

#### מחיקת תיקייה
**בקשה:**
```
DELETE /folder/{id}
```

### 2. ניהול סוגי משתמשים (User Types)

#### יצירת סוג משתמש חדש
**בקשה:**
```
POST /user_type
{
  "name": "Admin",
  "can_create_admin": true,
  "can_create_user": true
}
```
**תגובה:**
```
{
  "message": "User Type created successfully"
}
```

#### הצגת כל סוגי המשתמשים
**בקשה:**
```
GET /user_types
```

#### עדכון סוג משתמש
**בקשה:**
```
PUT /user_type/{id}
{
  "name": "Technician",
  "can_create_user": false
}
```

#### מחיקת סוג משתמש
**בקשה:**
```
DELETE /user_type/{id}
```

### 3. ניהול משתמשים (Users)

#### יצירת משתמש חדש
**בקשה:**
```
POST /user
{
  "first_name": "משה",
  "last_name": "כהן",
  "email": "moshe@example.com",
  "phone": "123456789",
  "password": "secret",
  "role": "Admin"
}
```

#### הצגת משתמש מסוים
**בקשה:**
```
GET /user/{id}
```

#### עדכון משתמש
**בקשה:**
```
PUT /user/{id}
{
  "first_name": "משה",
  "last_name": "לוי"
}
```

#### מחיקת משתמש
**בקשה:**
```
DELETE /user/{id}
```

---

## מסד נתונים

המערכת משתמשת במסד נתונים מבוסס SQLite עם הטבלאות הבאות:

### טבלת `Users`
| id | first_name | last_name | email | phone | role | password |
|----|-----------|-----------|-------|-------|------|----------|

### טבלת `User_Type`
| id | name | can_create_admin | can_create_user | ... |
|----|------|-----------------|-----------------|-----|

### טבלת `Folders`
| id | name | description |
|----|------|-------------|

### טבלת `Folders_Files`
| folder_id | file_id |
|-----------|--------|

---

## מידע נוסף
- המערכת מאובטחת באמצעות אימות פרטי משתמשים.
- API זה מיועד למערכת ניהול ארגונית.
- יש להרחיב את ההרשאות בהתאם לצורכי המערכת.

