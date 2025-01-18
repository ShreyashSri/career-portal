#apps.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, send_from_directory
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import os.path
from functools import wraps
from models import User, Opportunity
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static/uploads/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#---------------------------------------------------------------------------------------------------------------------------------#

@app.template_filter('datetime')
def format_datetime(value):
    if value is None:
        return ""
    return value.strftime('%Y-%m-%d %H:%M:%S')

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

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('home.html')

#---------------------------------------------------------------------------------------------------------------------------------#

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.users.find_one({'username': username})
        
        try:
            if user and check_password_hash(user['password'], password):
                session['is_admin'] = user.get('is_admin', False)
                session['user_id'] = str(user['_id'])
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
        except ValueError as e:
            print(f"Password verification error: {e}")
            # Log the error but don't expose it to the user
        
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/internships')
def internships():
    opportunities = list(db.opportunities.find({'type': 'internship'}))
    return render_template('opportunity_list.html', 
                         category='internship', 
                         opportunities=opportunities)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/jobs')
def jobs():
    opportunities = list(db.opportunities.find({'type': 'job'}))
    return render_template('opportunity_list.html', 
                         category='job', 
                         opportunities=opportunities)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/hackathons')
def hackathons():
    opportunities = list(db.opportunities.find({'type': 'hackathon'}))
    return render_template('opportunity_list.html', 
                         category='hackathon', 
                         opportunities=opportunities)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/mock-tests')
def mock_tests():
    tests = list(db.mock_tests.find())
    return render_template('mock_tests.html', tests=tests)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/activity-points')
def activity_points():
    return render_template('activity_points.html')

#---------------------------------------------------------------------------------------------------------------------------------#

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin')
@admin_required  # Using the decorator we created
def admin_homepage():
    # Redirect to admin dashboard if no specific admin page is requested
    return redirect(url_for('admin_dashboard'))

#---------------------------------------------------------------------------------------------------------------------------------#

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

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/opportunities', methods=['GET'])
@admin_required
def manage_opportunities():
    opportunities = Opportunity.get_all(db)
    # Define opportunity types
    opportunity_types = ['internship', 'job', 'hackathon']
    return render_template(
        'admin/manage_opportunities.html', 
        opportunities=opportunities,
        opportunity_types=opportunity_types
    )

#---------------------------------------------------------------------------------------------------------------------------------#

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

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/opportunity/add', methods=['GET', 'POST'])
@admin_required
def add_opportunity():
    if request.method == 'POST':
        opportunity = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'link': request.form['link'],
            'company': request.form.get('company'),
            'location': request.form.get('location'),
            'deadline': request.form.get('deadline'),
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        
        db.opportunities.insert_one(opportunity)
        flash('New opportunity added successfully!', 'success')
        return redirect(url_for('manage_opportunities'))
    
    return render_template('admin/add_opportunity.html')

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/opportunity/delete/<opportunity_id>', methods=['POST'])
@admin_required
def delete_opportunity(opportunity_id):
    Opportunity.delete(db, opportunity_id)
    flash('Opportunity deleted successfully!', 'success')
    return redirect(url_for('manage_opportunities'))

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/applications')
@admin_required
def manage_applications():
    # Get all applications and populate with opportunity details
    applications = list(db.applications.find().sort('created_at', -1))
    
    # Populate each application with its opportunity title
    for application in applications:
        opportunity = db.opportunities.find_one({'_id': application['opportunity_id']})
        if opportunity:
            application['opportunity_title'] = opportunity.get('title', 'Unknown Opportunity')
        else:
            application['opportunity_title'] = 'Opportunity Not Found'

    return render_template('admin/manage_applications.html', applications=applications)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/applications/<application_id>')
@admin_required
def view_application(application_id):
    try:
        # Find the application
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if not application:
            flash('Application not found', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Get the associated opportunity
        opportunity = db.opportunities.find_one({'_id': application['opportunity_id']})
        if opportunity:
            application['opportunity_title'] = opportunity.get('title', 'Unknown Opportunity')
        else:
            application['opportunity_title'] = 'Opportunity Not Found'
        
        # Add resume filename for display
        if 'resume_path' in application:
            application['resume_filename'] = os.path.basename(application['resume_path'])
        
        return render_template('admin/view_application.html', 
                            application=application)
    except Exception as e:
        flash(f'Error viewing application: {str(e)}', 'danger')
        return redirect(url_for('manage_applications'))
    
#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/users')
@admin_required
def manage_users():
    users = list(db.users.find())
    return render_template('admin/manage_users.html', users=users)

#---------------------------------------------------------------------------------------------------------------------------------#


@app.route('/admin/reset-user-password/<user_id>', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    new_password = request.form['new_password']
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password': hashed_password}}
    )
    flash('Password updated successfully', 'success')
    return redirect(url_for('manage_users'))

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/apply/<opportunity_type>/<opportunity_id>', methods=['GET', 'POST'])
def apply(opportunity_type, opportunity_id):
    opportunity = db.opportunities.find_one({'_id': ObjectId(opportunity_id)})
    if not opportunity:
        flash('Opportunity not found', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'danger')
            return redirect(request.url)
        
        resume = request.files['resume']
        if resume.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if resume and allowed_file(resume.filename):
            # Create a unique filename using timestamp
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + secure_filename(resume.filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Save the file
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)
            
            # Create application record with just the filename
            application = {
                'opportunity_id': ObjectId(opportunity_id),
                'opportunity_type': opportunity_type,
                'name': name,
                'email': email,
                'phone': phone,
                'resume_path': filename,  # Store just the filename
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            db.applications.insert_one(application)
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('internships' if opportunity_type == 'internship' 
                                  else 'jobs' if opportunity_type == 'job' 
                                  else 'hackathons'))
        else:
            flash('Invalid file type. Please upload PDF, DOC, or DOCX files only.', 'danger')
            return redirect(request.url)
    
    return render_template('application_form.html', opportunity=opportunity)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/applications/delete/<application_id>', methods=['POST'])
@admin_required
def delete_application(application_id):
    try:
        # Get the application to find the resume path
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if application and 'resume_path' in application:
            # Delete the resume file if it exists
            try:
                os.remove(application['resume_path'])
            except (OSError, FileNotFoundError):
                # Log this error but continue with application deletion
                print(f"Could not delete resume file: {application['resume_path']}")
        
        # Delete the application from database
        result = db.applications.delete_one({'_id': ObjectId(application_id)})
        if result.deleted_count:
            return jsonify({'success': True, 'message': 'Application deleted successfully'})
        return jsonify({'success': False, 'message': 'Application not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/applications/bulk-action', methods=['POST'])
@admin_required
def bulk_action_applications():
    action = request.form.get('action')
    application_ids = request.form.getlist('ids[]')
    
    if not action or not application_ids:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    try:
        if action == 'delete':
            for app_id in application_ids:
                # Get application to find resume path
                application = db.applications.find_one({'_id': ObjectId(app_id)})
                if application and 'resume_path' in application:
                    try:
                        os.remove(application['resume_path'])
                    except (OSError, FileNotFoundError):
                        print(f"Could not delete resume file: {application['resume_path']}")
                
                # Delete application from database
                db.applications.delete_one({'_id': ObjectId(app_id)})
            
            message = 'Selected applications deleted successfully'
        
        elif action in ['approve', 'reject']:
            status = 'accepted' if action == 'approve' else 'rejected'
            db.applications.update_many(
                {'_id': {'$in': [ObjectId(id) for id in application_ids]}},
                {'$set': {'status': status}}
            )
            message = f'Selected applications {status} successfully'
        
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})
        
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
#---------------------------------------------------------------------------------------------------------------------------------#
    
# Add this new route to serve resume files securely
@app.route('/admin/resume/<application_id>')
@admin_required
def serve_resume(application_id):
    try:
        # Find the application
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if not application or 'resume_path' not in application:
            flash('Resume not found', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Extract just the filename from the full path
        filename = os.path.basename(application['resume_path'])
        
        # Get the uploads directory path
        uploads_dir = os.path.abspath(UPLOAD_FOLDER)
        
        # Ensure the file exists
        full_path = os.path.join(uploads_dir, filename)
        if not os.path.exists(full_path):
            flash('Resume file is missing', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Serve the file from the uploads directory
        return send_from_directory(
            uploads_dir,
            filename,
            as_attachment=True
        )
    except Exception as e:
        print(f"Error serving resume: {e}")  # Log the error
        flash('Error accessing resume file', 'danger')
        return redirect(url_for('manage_applications'))
    
#---------------------------------------------------------------------------------------------------------------------------------#


if __name__ == '__main__':
    app.run()