import jwt
from flask import current_app
import datetime
from flask import abort

def generate_token(user_id, user_type, role):
    now = datetime.datetime.utcnow()
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'role': role,
        'iat': now,
        'exp': now + datetime.timedelta(hours=8),  # Token expires in 8 hours
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        abort(401, description="Token expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")
    except Exception as e:
        current_app.logger.error(f"Error decoding token: {str(e)}")
        abort(401, description="Token decoding error")