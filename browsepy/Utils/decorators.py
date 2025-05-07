from functools import wraps
from flask import jsonify

def safe_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            return response
        except Exception as e:
            return jsonify({"message": f"שגיאה פנימית: {str(e)}"}), 500
        
    return wrapper