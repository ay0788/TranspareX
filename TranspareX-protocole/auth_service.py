import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User, AuditLog, db
from config import Config

def token_required(f):
    """Decorator to require authentication token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            current_app.logger.warning('Token is missing in request')
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            current_app.logger.info(f'Decoding token: {token[:20]}...')
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['id']).first()
            
            if not current_user or not current_user.is_active:
                current_app.logger.warning(f'User not found or inactive: {data.get("id")}')
                return jsonify({'message': 'User not found or inactive!'}), 401
                
        except jwt.ExpiredSignatureError:
            current_app.logger.warning('Token has expired')
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f'Invalid token: {str(e)}')
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            current_app.logger.error(f'Token verification failed: {str(e)}')
            return jsonify({'message': 'Token verification failed!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def log_audit(user_id, action, details=None, ip_address=None, user_agent=None):
    """Log user actions for audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log audit: {str(e)}")

def register_user(username, email, password, role='user'):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            return {"success": False, "message": "User already exists!"}
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log the registration
        log_audit(
            new_user.id,
            "User Registration",
            f"New user registered: {username}",
            request.remote_addr if request else None,
            request.headers.get('User-Agent') if request else None
        )
        
        return {
            "success": True,
            "message": "User registered successfully!",
            "user": new_user.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Registration failed: {str(e)}"}

def authenticate_user(email, password):
    """Authenticate user login"""
    try:
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.is_active:
            return {"success": False, "message": "Invalid credentials!"}
        
        if not user.check_password(password):
            return {"success": False, "message": "Invalid credentials!"}
        
        # Generate token
        token = user.generate_token()
        
        # Log the login
        log_audit(
            user.id,
            "User Login",
            f"User logged in: {user.username}",
            request.remote_addr if request else None,
            request.headers.get('User-Agent') if request else None
        )
        
        return {
            "success": True,
            "message": "Login successful!",
            "token": token,
            "user": user.to_dict()
        }
        
    except Exception as e:
        return {"success": False, "message": f"Authentication failed: {str(e)}"}

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        user = User.query.filter_by(id=user_id).first()
        if user:
            return {"success": True, "user": user.to_dict()}
        else:
            return {"success": False, "message": "User not found!"}
    except Exception as e:
        return {"success": False, "message": f"Error retrieving user: {str(e)}"}

def update_user_profile(user_id, **kwargs):
    """Update user profile"""
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"success": False, "message": "User not found!"}
        
        # Update allowed fields
        allowed_fields = ['username', 'email']
        for field, value in kwargs.items():
            if field in allowed_fields and value:
                setattr(user, field, value)
        
        db.session.commit()
        
        # Log the update
        log_audit(
            user.id,
            "Profile Update",
            f"User profile updated: {user.username}",
            request.remote_addr if request else None,
            request.headers.get('User-Agent') if request else None
        )
        
        return {
            "success": True,
            "message": "Profile updated successfully!",
            "user": user.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Update failed: {str(e)}"}

def change_password(user_id, old_password, new_password):
    """Change user password"""
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"success": False, "message": "User not found!"}
        
        if not user.check_password(old_password):
            return {"success": False, "message": "Current password is incorrect!"}
        
        user.set_password(new_password)
        db.session.commit()
        
        # Log the password change
        log_audit(
            user.id,
            "Password Change",
            f"Password changed for user: {user.username}",
            request.remote_addr if request else None,
            request.headers.get('User-Agent') if request else None
        )
        
        return {"success": True, "message": "Password changed successfully!"}
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Password change failed: {str(e)}"}

def get_audit_logs(user_id=None, limit=100):
    """Get audit logs"""
    try:
        query = AuditLog.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "logs": [log.to_dict() for log in logs]
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error retrieving audit logs: {str(e)}"}
