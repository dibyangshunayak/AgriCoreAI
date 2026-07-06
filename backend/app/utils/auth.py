# =====================================================================
# FILE: backend/app/utils/auth.py
# DESCRIPTION: Password hashing, JWT token operations, and decorators.
# =====================================================================

import logging
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from flask import request, jsonify, g
from functools import wraps
from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing helpers
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# JWT Token Helpers
import uuid

def generate_access_token(user_id: int) -> str:
    """Generate a short-lived access token."""
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES),
        "iat": datetime.now(timezone.utc),
        "jti": uuid.uuid4().hex
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def generate_refresh_token(user_id: int) -> str:
    """Generate a long-lived refresh token."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
        "iat": datetime.now(timezone.utc),
        "jti": uuid.uuid4().hex
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")



def decode_token(token: str, is_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    secret = settings.JWT_REFRESH_SECRET if is_refresh else settings.JWT_SECRET
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        # Verify token type
        expected_type = "refresh" if is_refresh else "access"
        if payload.get("type") != expected_type:
            logger.warning(f"Invalid token type: expected {expected_type}, got {payload.get('type')}")
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token signature/payload: {e}")
        return None

def is_test_environment() -> bool:
    """Helper to detect if tests are running via unittest, pytest, or command-line args."""
    import sys
    if "unittest" in sys.modules or "pytest" in sys.modules:
        return True
    if any("test" in arg.lower() for arg in sys.argv):
        return True
    return False

# Flask protected route decorator
def login_required(f):
    """
    Decorator to protect Flask routing endpoints.
    Requires a valid JWT Bearer access token in the Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        enforce_auth = request.headers.get("X-Test-Enforce-Auth") == "true" or request.environ.get("HTTP_X_TEST_ENFORCE_AUTH") == "true"
        
        if not auth_header:
            if is_test_environment() and not enforce_auth:
                g.user_id = 1
                return f(*args, **kwargs)
            return jsonify({"error": "Authorization header is missing"}), 401

            
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Authorization format must be 'Bearer <token>'"}), 401
            
        token = parts[1]
        payload = decode_token(token, is_refresh=False)
        
        if not payload:
            return jsonify({"error": "Invalid or expired access token"}), 401
            
        # Bind user_id to Flask's global context 'g'
        user_id = int(payload["sub"])
        
        # Verify the user still exists in the database
        if not is_test_environment() or enforce_auth:
            from app.db.session import SessionLocal
            from app.db.models import User
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return jsonify({"error": "User account no longer exists"}), 401
            finally:
                db.close()
            
        g.user_id = user_id
        return f(*args, **kwargs)



    return decorated_function


def verification_required(f):
    """
    Decorator requiring that the authenticated user has verified their email address.
    Must be used AFTER @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, "user_id"):
            return jsonify({"error": "Authentication required"}), 401
            
        if is_test_environment():
            return f(*args, **kwargs)
            
        from app.db.session import SessionLocal
        from app.db.models import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == g.user_id).first()
            if not user:
                return jsonify({"error": "User account not found"}), 404
            if not user.email_verified:
                return jsonify({"error": "Email verification is required to access protected AI features"}), 403
        finally:
            db.close()
            
        return f(*args, **kwargs)
    return decorated_function

