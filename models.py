#models.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

class User:
    """User model for both admins and regular users"""
    def __init__(self, username, email, role='user', password=None):
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(db, username, email, password, role='user'):
        user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.utcnow()
        }
        return db.users.insert_one(user)

    @staticmethod
    def get_by_username(db, username):
        return db.users.find_one({'username': username})

class Opportunity:
    """Model for managing opportunities (jobs, internships, hackathons)"""
    @staticmethod
    def create(db, title, description, type, link, company=None, location=None, deadline=None):
        opportunity = {
            'title': title,
            'description': description,
            'type': type,
            'link': link,
            'company': company,
            'location': location,
            'deadline': deadline,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        return db.opportunities.insert_one(opportunity)

    @staticmethod
    def update(db, opportunity_id, updates):
        return db.opportunities.update_one(
            {'_id': ObjectId(opportunity_id)},
            {'$set': updates}
        )

    @staticmethod
    def delete(db, opportunity_id):
        return db.opportunities.delete_one({'_id': ObjectId(opportunity_id)})

    @staticmethod
    def get_all(db, type=None, status='active'):
        query = {'status': status}
        if type:
            query['type'] = type
        return list(db.opportunities.find(query).sort('created_at', -1))