from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mail import Mail, Message
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 

app= Flask(__name__)
app.secret_key = 'super_secret_placement_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement_portal.db'
app.config['CELERY_BROKER_URL']='redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME']='email_private_hence_not_updated_on_github'
app.config['MAIL_PASSWORD']='my_private_email_passwordf'
mail = Mail(app)
bcrypt = Bcrypt(app)

db=SQLAlchemy(app)

class admin(db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)

class student(db.Model):
    scholar_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    degree = db.Column(db.String(5), nullable=False)
    branch = db.Column(db.String(50), nullable=False, default="Unknown") 
    cgpa = db.Column(db.Float, nullable=False, default=0.0) 
    skills = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Active')

class company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    email=db.Column(db.String(250),nullable=False)
    password=db.Column(db.String(255),nullable=False)
    status=db.Column(db.String(20),default="Pending")

class job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    min_cgpa = db.Column(db.Float, nullable=False, default=0.0)
    eligible_branches = db.Column(db.String(200), nullable=False, default="All")
    eligible_degrees = db.Column(db.String(200), nullable=False, default="All")
    openings = db.Column(db.Integer, nullable=False, default=1)
    
    company = db.relationship('company', backref=db.backref('jobs', lazy=True))

    @property
    def company_name(self):
        return self.company.name if self.company else "Unknown"

class application(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('student.scholar_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(20), default="Applied")

class placement(db.Model):
    id = db.Column(db.Integer,primary_key=True)    
    student_id = db.Column(db.String(20),db.ForeignKey('student.scholar_id'),nullable=False)
    job_id = db.Column(db.Integer,db.ForeignKey('job.id'),nullable=False)

def make_celery(app):
    celery = Celery(
        app.import_name, 
        backend=app.config['CELERY_RESULT_BACKEND'], 
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery= make_celery(app)

@celery.task(name='app.send_application_update_email')
def send_application_update_email(student_email, student_name, company_name, new_status):
    subject = f"Application Status Update: {company_name}"
    sender = "tanmaysharna014@gmail.com" 
    
    msg = Message(subject, sender=sender, recipients=[student_email])
    
    if new_status.lower() == 'accepted':
        msg.body = f"Hello {student_name},\n\nGreat news! Your application for {company_name} has been Accepted."
    else:
        msg.body = f"Hello {student_name},\n\nYour application for {company_name} has been marked as {new_status}."
    
    mail.send(msg)
    return f"Email sent to {student_email} for {company_name}"

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        s_id = request.form.get('scholar_id')
        s_name = request.form.get('name')
        s_email = request.form.get('email')
        s_password = request.form.get('password')
        hashed_password=bcrypt.generate_password_hash(s_password).decode('utf-8')
        s_degree = request.form.get('degree', 'Unknown') 
        s_branch = request.form.get('branch', 'Unknown') 
        
        raw_cgpa = request.form.get('cgpa')
        try:
            s_cgpa = float(raw_cgpa)
        except (ValueError, TypeError):
            s_cgpa = 0.0
            
        skills_list = request.form.getlist('skills')
        s_skills = ", ".join(skills_list) if skills_list else "None listed"

        new_student = student(scholar_id=s_id, name=s_name, email=s_email, 
                              password=hashed_password, degree=s_degree, 
                              branch=s_branch, cgpa=s_cgpa, skills=s_skills)
        
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('login_result'))
        
    return render_template('student_register.html')

@app.route('/login_result')
def login_result():
    return render_template('login_result.html')

@app.route('/invalid_credentials')
def invalid_credentials():
    return render_template("invalid_credentials.html")

@app.route('/register/company',methods=['GET','POST'])
def register_company():
    if request.method=='POST':
        c_id=request.form['company_id']
        c_name=request.form['name']
        c_email=request.form['email']
        c_password=request.form['password']

        hashed_c_pw = bcrypt.generate_password_hash(c_password).decode('utf-8')

        new_company = company(name=c_name, email=c_email, password=hashed_c_pw, status='Pending')        
        db.session.add(new_company)
        db.session.commit()
        return render_template('approval.html')
    return render_template('company_registration.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        role2=request.form['role']
        identifier=request.form['identifier']
        password=request.form['password']
        
        if role2== 'student':
            found_student = student.query.filter_by(scholar_id=identifier).first()
            if found_student and bcrypt.check_password_hash(found_student.password,password):
                session['student_id'] = found_student.scholar_id
                session['student_name'] = found_student.name
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('invalid_credentials'))
                
        elif role2=='company':
            company_find=company.query.filter_by(email=identifier).first()
            if company_find and bcrypt.check_password_hash(company_find.password,password):
                if company_find.status == "Active":
                    session['company_name'] = company_find.name
                    session['company_id'] = company_find.id 
                    session['role'] = 'company' 
                    return redirect(url_for('company_dashboard'))
                elif company_find.status == "Pending":
                    return render_template('approval.html')
                else:
                    return redirect(url_for('invalid_credentials'))
            else:
                return redirect(url_for('invalid_credentials'))
                
        elif role2== 'admin':
            found_admin = admin.query.filter_by(username=identifier).first()
            if found_admin and bcrypt.check_password_hash(found_admin.password, password):
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('invalid_credentials'))
                
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    waiting = company.query.filter_by(status='Pending').all()
    waiting_jobs = job.query.filter_by(status='Pending').all()
    
    total_students_count = student.query.count()
    total_companies_count = company.query.count()
    total_jobs_count = job.query.count()
    total_apps_count = application.query.count()
    pending_count = len(waiting) 
    
    return render_template('admin_dashboard.html', 
                           pending=waiting, 
                           pending_jobs=waiting_jobs, 
                           total_students=total_students_count, 
                           total_companies=total_companies_count,
                           total_jobs=total_jobs_count,
                           total_apps=total_apps_count,
                           pending_companies=pending_count)

@app.route('/admin/approve_job/<int:job_id>', methods=['POST'])
def approve_job(job_id):
    job_to_approve = job.query.get(job_id)
    if job_to_approve:
        job_to_approve.status = 'Active'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_job/<int:job_id>', methods=['POST'])
def reject_job(job_id):
    job_to_reject = job.query.get(job_id)
    if job_to_reject:
        job_to_reject.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/company/dashboard')
def company_dashboard():
    if 'company_name' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
        
    c_name = session['company_name']
    c_id = session.get('company_id')
    
    company_jobs = job.query.filter_by(company_id=c_id).all()
    company_apps = application.query.join(job).filter(job.company_id == c_id).all()
    
    return render_template('company_dashboard.html', name=c_name, jobs=company_jobs, applications=company_apps)

@app.route('/admin/approve/<int:company_id>', methods=['POST'])
def approve_company(company_id):
    company_to_approve = company.query.get(company_id)
    if company_to_approve:
        company_to_approve.status = 'Active'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:company_id>', methods=['POST'])
def reject_company(company_id):
    company_to_reject = company.query.get(company_id)
    if company_to_reject:
        company_to_reject.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/student/dashboard")
def student_dashboard():
    if 'student_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    current_student = student.query.get(student_id)
    student_degree = current_student.degree
    student_branch = current_student.branch
    student_cgpa = current_student.cgpa 
    
    all_active_jobs = job.query.filter_by(status='Active').all()
    
    filtered_jobs = []
    for j in all_active_jobs:
        degree_match = "All" in j.eligible_degrees or student_degree in j.eligible_degrees
        branch_match = "All" in j.eligible_branches or student_branch in j.eligible_branches
        cgpa_match = student_cgpa >= j.min_cgpa
        
        if degree_match and branch_match and cgpa_match:
            filtered_jobs.append(j)
    
    applied_apps = application.query.filter_by(student_id=student_id).all()
    application_statuses = {app.job_id: app.status for app in applied_apps}
    student_name = session.get('student_name', 'Student')
    
    return render_template('student_dashboard.html', 
                           name=student_name, 
                           jobs=filtered_jobs, 
                           application_statuses=application_statuses)

@app.route('/student/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'student_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    s_id = session['student_id']
    already_applied = application.query.filter_by(student_id=s_id, job_id=job_id).first()
    
    if not already_applied:
        new_app = application(student_id=s_id, job_id=job_id)
        db.session.add(new_app)
        db.session.commit()
        
    return redirect(url_for('student_dashboard'))

@app.route('/company/post_job', methods=['POST'])
def post_job():
    j_title = request.form['title']
    j_desc = request.form['description']
    j_salary = request.form['salary']
    j_cgpa = float(request.form.get('min_cgpa', 0.0))
    j_openings = int(request.form.get('openings', 1))
    
    degrees_list = request.form.getlist('eligible_degrees')
    j_degrees = ", ".join(degrees_list) if degrees_list else "All"
    
    branches_list = request.form.getlist('eligible_branches')
    j_branches = ", ".join(branches_list) if branches_list else "All"
        
    c_id = session.get('company_id')
    new_job = job(
        title=j_title, description=j_desc, salary=j_salary, 
        company_id=c_id, status='Pending', min_cgpa=j_cgpa,
        eligible_branches=j_branches, eligible_degrees=j_degrees, openings=j_openings
    )
    
    db.session.add(new_job)
    db.session.commit()
    return redirect(url_for('company_dashboard'))

@app.route('/company/update_app/<int:app_id>/<string:new_status>', methods=['POST'])
def update_application(app_id, new_status):
    if 'company_name' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
        
    app_to_update = application.query.get(app_id)
    c_id = session.get('company_id')
    
    if app_to_update:
        related_job = job.query.get(app_to_update.job_id)
        
        if related_job and related_job.company_id == c_id:
            # 1. Update database
            app_to_update.status = new_status
            db.session.commit()
            
            # 2. Fetch data needed for the email
            student_record = student.query.get(app_to_update.student_id)
            company_record = company.query.get(c_id)
            
            # 3. Trigger background task
            send_application_update_email.delay(
                student_email=student_record.email, 
                student_name=student_record.name, 
                company_name=company_record.name, 
                new_status=new_status
            )
            
    return redirect(url_for('company_dashboard'))

with app.app_context():
    db.create_all()
    print("DATABASE DEPLOYED")
    admin_user=admin.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_admin_pw = bcrypt.generate_password_hash('qwerty').decode('utf-8')
        my_admin = admin(username='admin', admin_id=1, password=hashed_admin_pw)
        db.session.add(my_admin)
        db.session.commit()
        print("created adminz")

if __name__=='__main__':
    app.run(debug=True,port=5001)
