from functools import wraps
from flask import request, abort
from .JWT import decode_token

def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                abort(401, description="Authorization header missing")

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                abort(401, description="Authorization header must be Bearer token")

            token = parts[1]
            try:
                payload = decode_token(token)
                user_role = payload.get('role')
                if allowed_roles and user_role not in allowed_roles:
                    abort(403, description="You do not have permission to access this resource")

                request.user = {
                    'id': payload.get('user_id'),
                    'type': payload.get('user_type'),
                    'role': user_role
                }
            except Exception:
                abort(401, description="Invalid or expired token")

            return f(*args, **kwargs)
        return decorated
    return decorator

