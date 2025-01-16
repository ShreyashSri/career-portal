from functools import wraps
from flask import session, redirect, url_for, flash, request
from datetime import datetime

def admin_required(f):
    """Decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to require user login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(f):
    """Decorator to log admin activities"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the result from the route
        result = f(*args, **kwargs)
        
        # Log the activity
        if session.get('is_admin'):
            activity = {
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'action': f.__name__,
                'timestamp': datetime.utcnow(),
                'ip_address': request.remote_addr,
                'endpoint': request.endpoint,
                'method': request.method
            }
            # You would need to pass db to this decorator somehow
            # db.activity_log.insert_one(activity)
        
        return result
    return decorated_function