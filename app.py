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

# At the top of your file
if os.environ.get('FLASK_ENV') == 'production':
    UPLOAD_FOLDER = '/opt/render/project/src/static/uploads/resumes'
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
        # Convert is_paid from string to boolean
        is_paid = request.form.get('is_paid') == 'true'
        
        # Handle payment amount
        payment_amount = None
        if is_paid and request.form.get('payment_amount'):
            try:
                payment_amount = float(request.form.get('payment_amount'))
            except ValueError:
                payment_amount = None

        updates = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'link': request.form['link'],
            'company': request.form.get('company'),
            'location': request.form.get('location'),
            'deadline': request.form.get('deadline'),
            'status': request.form['status'],
            'is_paid': is_paid,
            'payment_amount': payment_amount
        }
        
        # Remove None values to avoid overwriting with null
        updates = {k: v for k, v in updates.items() if v is not None}
        
        db.opportunities.update_one(
            {'_id': ObjectId(opportunity_id)},
            {'$set': updates}
        )
        flash('Opportunity updated successfully!', 'success')
        return redirect(url_for('manage_opportunities'))
    
    opportunity = db.opportunities.find_one({'_id': ObjectId(opportunity_id)})
    return render_template('admin/edit_opportunity.html', opportunity=opportunity)

#---------------------------------------------------------------------------------------------------------------------------------#

@app.route('/admin/opportunity/add', methods=['GET', 'POST'])
@admin_required
def add_opportunity():
    if request.method == 'POST':
        # Convert is_paid from string to boolean
        is_paid = request.form.get('is_paid') == 'true'
        
        # Handle payment amount
        payment_amount = None
        if is_paid and request.form.get('payment_amount'):
            try:
                payment_amount = float(request.form.get('payment_amount'))
            except ValueError:
                payment_amount = None

        opportunity = {
            'title': request.form['title'],
            'description': request.form['description'],
            'type': request.form['type'],
            'link': request.form['link'],
            'company': request.form.get('company'),
            'location': request.form.get('location'),
            'deadline': request.form.get('deadline'),
            'created_at': datetime.utcnow(),
            'status': 'active',
            'is_paid': is_paid,
            'payment_amount': payment_amount
        }
        
        # Remove None values to avoid storing null
        opportunity = {k: v for k, v in opportunity.items() if v is not None}
        
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
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + secure_filename(resume.filename)
            
            # Ensure the upload directory exists
            uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'resumes')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Save the file
            resume_path = os.path.join(uploads_dir, filename)
            resume.save(resume_path)
            
            # Store only the filename in the database
            application = {
                'opportunity_id': ObjectId(opportunity_id),
                'opportunity_type': opportunity_type,
                'name': name,
                'email': email,
                'phone': phone,
                'resume_path': filename,  # Store only filename
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
def verify_pdf_file(file_path):
    """Verify if a file is a valid PDF"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            # Check for PDF magic number
            return header.startswith(b'%PDF')
    except Exception as e:
        print(f"Error verifying PDF: {e}")
        return False
    
# Add this new route to serve resume files securely
@app.route('/admin/resume/<application_id>')
@admin_required
def serve_resume(application_id):
    try:
        # Get application
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if not application or 'resume_path' not in application:
            flash('Resume not found', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Setup paths
        base_dir = os.path.dirname(__file__)
        uploads_dir = os.path.join(base_dir, 'static', 'uploads', 'resumes')
        filename = os.path.basename(application['resume_path'])
        full_path = os.path.join(uploads_dir, filename)
        
        # Check if file exists
        if not os.path.exists(full_path):
            flash('Resume file is missing', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Verify PDF integrity
        if not verify_pdf_file(full_path):
            flash('Invalid or corrupted PDF file', 'danger')
            return redirect(url_for('manage_applications'))
        
        # Serve the file with proper headers
        response = send_from_directory(
            uploads_dir, 
            filename,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
        # Add additional headers for PDF handling
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        print(f"Error in serve_resume: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        flash('Error accessing resume file', 'danger')
        return redirect(url_for('manage_applications'))
    
#---------------------------------------------------------------------------------------------------------------------------------#
@app.route('/admin/debug-resume/<application_id>')
@admin_required
def debug_resume(application_id):
    try:
        # Check database entry
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if not application:
            return jsonify({'error': 'Application not found'})

        # Get paths
        base_dir = os.path.dirname(__file__)
        uploads_dir = os.path.join(base_dir, 'static', 'uploads', 'resumes')
        
        # Create diagnostic info
        info = {
            'application_data': {
                'id': str(application['_id']),
                'resume_path': application.get('resume_path'),
                'created_at': application.get('created_at').isoformat()
            },
            'paths': {
                'base_dir': base_dir,
                'uploads_dir': uploads_dir,
                'uploads_dir_exists': os.path.exists(uploads_dir),
                'uploads_dir_contents': os.listdir(uploads_dir) if os.path.exists(uploads_dir) else []
            }
        }
        
        # Check if file exists
        if 'resume_path' in application:
            full_path = os.path.join(uploads_dir, application['resume_path'])
            info['file'] = {
                'full_path': full_path,
                'exists': os.path.exists(full_path),
                'is_file': os.path.isfile(full_path) if os.path.exists(full_path) else False,
                'size': os.path.getsize(full_path) if os.path.exists(full_path) else None
            }
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()})
    
#---------------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run()