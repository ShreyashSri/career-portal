from datetime import datetime
from bson import ObjectId
import re

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_pagination_params(request, default_per_page=10):
    """Get pagination parameters from request"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', default_per_page))
    except ValueError:
        page = 1
        per_page = default_per_page
    return page, per_page

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def get_opportunity_stats(db):
    """Get statistics about opportunities"""
    return {
        'total': db.opportunities.count_documents({}),
        'active': db.opportunities.count_documents({'status': 'active'}),
        'by_type': {
            'internship': db.opportunities.count_documents({'type': 'internship'}),
            'job': db.opportunities.count_documents({'type': 'job'}),
            'hackathon': db.opportunities.count_documents({'type': 'hackathon'})
        }
    }

def get_application_stats(db):
    """Get statistics about applications"""
    return {
        'total': db.applications.count_documents({}),
        'pending': db.applications.count_documents({'status': 'pending'}),
        'accepted': db.applications.count_documents({'status': 'accepted'}),
        'rejected': db.applications.count_documents({'status': 'rejected'})
    }

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ''
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Convert special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text