import os
import jwt
from functools import wraps
from flask import request, jsonify
from jwt import ExpiredSignatureError, InvalidTokenError

def internal_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 1. Check Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({
                    "success": False,
                    "message": "Missing Authorization header"
                }), 401

            # 2. Ensure Bearer format
            if not auth_header.startswith("Bearer "):
                return jsonify({
                    "success": False,
                    "message": "Invalid Authorization header format"
                }), 401

            # 3. Extract token
            token = auth_header.split(" ")[1].strip()
            if not token:
                return jsonify({
                    "success": False,
                    "message": "Token not provided"
                }), 401

            # 4. Validate secret exists
            secret = os.getenv("INTERNAL_JWT_SECRET")
            if not secret:
                return jsonify({
                    "success": False,
                    "message": "Server misconfiguration: INTERNAL_JWT_SECRET missing"
                }), 500

            # 5. Decode token
            try:
                jwt.decode(token, secret, algorithms=["HS256"])
            except ExpiredSignatureError:
                return jsonify({
                    "success": False,
                    "message": "Token expired"
                }), 401
            except InvalidTokenError:
                return jsonify({
                    "success": False,
                    "message": "Invalid token"
                }), 401

            # 6. Allow access
            return f(*args, **kwargs)

        except Exception as e:
            # Universal catch-all fallback (no internal server error leaks)
            return jsonify({
                "success": False,
                "message": "Authorization failed"
            }), 401

    return decorated
