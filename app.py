#apps.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from models import User, Opportunity
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# MongoDB connection
try:
    MONGODB_URI = os.getenv('MONGODB_URI')  # Get from environment variable
    client = MongoClient(MONGODB_URI)
    db = client['career_portal']
    # Test the connection
    client.server_info()  # This will raise an exception if connection fails
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check in users collection instead of admins
        user = db.users.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['is_admin'] = user.get('is_admin', False)
            session['user_id'] = str(user['_id'])
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/internships')
def internships():
    opportunities = list(db.opportunities.find({'type': 'internship'}))
    return render_template('opportunity_list.html', 
                         category='internship', 
                         opportunities=opportunities)

@app.route('/jobs')
def jobs():
    opportunities = list(db.opportunities.find({'type': 'job'}))
    return render_template('opportunity_list.html', 
                         category='job', 
                         opportunities=opportunities)

@app.route('/hackathons')
def hackathons():
    opportunities = list(db.opportunities.find({'type': 'hackathon'}))
    return render_template('opportunity_list.html', 
                         category='hackathon', 
                         opportunities=opportunities)

@app.route('/mock-tests')
def mock_tests():
    tests = list(db.mock_tests.find())
    return render_template('mock_tests.html', tests=tests)

@app.route('/activity-points')
def activity_points():
    return render_template('activity_points.html')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required  # Using the decorator we created
def admin_homepage():
    # Redirect to admin dashboard if no specific admin page is requested
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics for the dashboard
    stats = {
        'total_opportunities': db.opportunities.count_documents({}),
        'active_applications': db.applications.count_documents({'status': 'pending'}),
        'total_users': db.users.count_documents({}),
        'new_applications': db.applications.count_documents({
            'created_at': {'$gte': datetime.utcnow() - timedelta(days=1)}
        })
    }
    
    # Get recent activities
    recent_activities = list(db.activity_log.find().sort('timestamp', -1).limit(10))
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_activities=recent_activities)

@app.route('/admin/opportunities', methods=['GET'])
@admin_required
def manage_opportunities():
    opportunities = Opportunity.get_all(db)
    return render_template('admin/manage_opportunities.html', opportunities=opportunities)

@app.route('/admin/opportunity/<opportunity_id>', methods=['GET', 'POST'])
@admin_required
def edit_opportunity(opportunity_id):
    if request.method == 'POST':
        updates = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'link': request.form['link'],
            'status': request.form['status']
        }
        Opportunity.update(db, opportunity_id, updates)
        flash('Opportunity updated successfully!', 'success')
        return redirect(url_for('manage_opportunities'))
    
    opportunity = db.opportunities.find_one({'_id': ObjectId(opportunity_id)})
    return render_template('admin/edit_opportunity.html', opportunity=opportunity)

@app.route('/admin/opportunity/delete/<opportunity_id>', methods=['POST'])
@admin_required
def delete_opportunity(opportunity_id):
    Opportunity.delete(db, opportunity_id)
    flash('Opportunity deleted successfully!', 'success')
    return redirect(url_for('manage_opportunities'))

@app.route('/admin/applications')
@admin_required
def manage_applications():
    applications = list(db.applications.find().sort('created_at', -1))
    return render_template('admin/manage_applications.html', applications=applications)

@app.route('/admin/users')
@admin_required
def manage_users():
    users = list(db.users.find())
    return render_template('admin/manage_users.html', users=users)


if __name__ == '__main__':
    app.run()