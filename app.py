from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# MongoDB connection
try:
    client = MongoClient('mongodb+srv://ShreyashSri:ggwp@cluster0.bbhp0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['career_portal']
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
        # Get the login details
        username = request.form['username']
        password = request.form['password']
        
        # Fetch admin credentials (For simplicity, using hardcoded data)
        admin_data = db.admins.find_one({'username': username})  # Assumes admins collection in MongoDB
        
        if admin_data and check_password_hash(admin_data['password'], password):
            # Store the session information when login is successful
            session['is_admin'] = True
            session['username'] = username  # Store username for future reference
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
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

@app.route('/apply/<opportunity_type>/<opportunity_id>', methods=['GET', 'POST'])
def apply(opportunity_type, opportunity_id):
    opportunity = db.opportunities.find_one({'_id': opportunity_id})
    
    if request.method == 'POST':
        application = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'resume': request.form['resume'],
            'opportunity_id': opportunity_id,
            'type': opportunity_type,
            'created_at': datetime.utcnow()
        }
        
        try:
            db.applications.insert_one(application)
            flash('Application submitted successfully!', 'success')
        except Exception as e:
            flash('Error submitting application. Please try again.', 'danger')
            print(e)
        
        return redirect(url_for(f'{opportunity_type}s'))
    
    return render_template('application_form.html', 
                         opportunity=opportunity,
                         opportunity_type=opportunity_type)

@app.route('/admin/add-opportunity', methods=['GET', 'POST'])
def add_opportunity():
    # Check if the user is an admin
    if not session.get('is_admin'):
        flash('Unauthorized access! Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Extract form data
        new_opportunity = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],  # e.g., 'internship', 'job', 'hackathon'
            'link': request.form['link'],
            'created_at': datetime.utcnow()
        }

        try:
            # Insert into the database
            db.opportunities.insert_one(new_opportunity)
            flash('Opportunity added successfully!', 'success')
        except Exception as e:
            flash('Error adding opportunity. Please try again.', 'danger')
            print(e)
        
        return redirect(url_for('home'))
    
    return render_template('add_opportunity.html')

if __name__ == '__main__':
    app.run(debug=True)