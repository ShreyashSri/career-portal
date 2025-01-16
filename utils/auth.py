from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Auth:
    def __init__(self, db):
        self.db = db

    def create_user(self, username, email, password, role='user'):
        """Create a new user in the database"""
        user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        return self.db.users.insert_one(user)

    def verify_user(self, username, password):
        """Verify user credentials"""
        user = self.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            self.db.users.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return user
        return None

    def change_password(self, user_id, new_password):
        """Change user password"""
        return self.db.users.update_one(
            {'_id': user_id},
            {'$set': {'password': generate_password_hash(new_password)}}
        )

    def get_user_by_email(self, email):
        """Get user by email"""
        return self.db.users.find_one({'email': email})

    def generate_reset_token(self, email):
        """Generate password reset token"""
        # Implementation for password reset token generation
        pass

    def verify_reset_token(self, token):
        """Verify password reset token"""
        # Implementation for token verification
        pass