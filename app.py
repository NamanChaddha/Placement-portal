from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
app.secret_key = 'super_secret_placement_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement_portal.db'
db=SQLAlchemy(app)

class admin(db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)

class student(db.Model):
    scholar_id=db.Column(db.String(20),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(250),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    degree=db.Column(db.String(5),nullable=False)
    skills = db.Column(db.String(200))

class company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    email=db.Column(db.String(250),nullable=False)
    password=db.Column(db.String(50),nullable=False)
    status=db.Column(db.String(20),default="Pending")

class job_position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    salary = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Active") 
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

class application(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('student.scholar_id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'), nullable=False)
    status = db.Column(db.String(20), default="Applied")

class placement(db.Model):
    id = db.Column(db.Integer,primary_key=True)    
    student_id = db.Column(db.String(20),db.ForeignKey('student.scholar_id'),nullable=False)
    job_id = db.Column(db.Integer,db.ForeignKey('job_position.id'),nullable=False)

class job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)

@app.route('/register/student',methods=['GET','POST'])
def register_student():
    if request.method=='POST':
        s_id=request.form['scholar_id']
        s_name=request.form['name']
        s_email=request.form['email']
        s_password=request.form['password']
        s_degree=request.form['degree']
        s_skills=request.form['skills']

        new_student = student(scholar_id=s_id, name=s_name, email=s_email, password=s_password, degree=s_degree, skills=s_skills)
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

        new_company = company(id=c_id,name=c_name,email=c_email,password=c_password)
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
            if found_student and found_student.password == password:
                session['student_id'] = found_student.scholar_id
                session['student_name'] = found_student.name
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('invalid_credentials'))
                
        elif role2=='company':
            company_find=company.query.filter_by(email=identifier).first()
            if company_find and company_find.password==password:
                if company_find.status == "Pending":
                    return "Your account is still pending admin Approval."
                elif company_find.status == "Active":
                    session['company_name'] = company_find.name
                    session['role'] = 'company' 
                    return redirect(url_for('company_dashboard'))
            else:
                return redirect(url_for('invalid_credentials'))
                
        elif role2== 'admin':
            found_admin = admin.query.filter_by(username=identifier).first()
            if found_admin and found_admin.password==password:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('invalid_credentials'))
                
    return render_template('xp.html')
@app.route('/admin/dashboard')
@app.route('/admin/dashboard')
def admin_dashboard():
    # if session.get('role') != 'admin':
    #     return redirect(url_for('login'))

    waiting = company.query.filter_by(status='Pending').all()
    
    total_students_count = student.query.count()
    total_companies_count = company.query.count()
    total_jobs_count = job.query.count()
    total_apps_count = application.query.count()
    pending_count = len(waiting) 
    return render_template('admin_dashboard.html', 
                           pending=waiting, 
                           total_students=total_students_count, 
                           total_companies=total_companies_count,
                           total_jobs=total_jobs_count,
                           total_apps=total_apps_count,
                           pending_companies=pending_count)

@app.route('/admin/approve/<int:company_id>', methods=['POST'])
def approve_company(company_id):
    company_to_approve = company.query.get(company_id)
    if company_to_approve:
        company_to_approve.status='Active'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:company_id>', methods=['POST'])
def reject_company(company_id):
    company_to_reject = company.query.get(company_id)
    if company_to_reject:
        company_to_reject.status='Rejected'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/company/dashboard')
def company_dashboard():
    if 'company_name' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
    c_name = session['company_name']
    company_jobs = job.query.filter_by(company_name=c_name).all()
    company_apps = application.query.filter_by(company_name=c_name).all()
    return render_template('company_dashboard.html', name=c_name, jobs=company_jobs, applications=company_apps)

@app.route("/student/dashboard")
def student_dashboard():
    # Security check
    if 'student_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    jobs = job.query.all()
    student_id = session['student_id']
    applied_apps = application.query.filter_by(student_id=student_id).all()    
    application_statuses = {app.job_id: app.status for app in applied_apps}
    student_name = session.get('student_name', 'Student')
    return render_template('student_dashboard.html', 
                           name=student_name, 
                           jobs=jobs, 
                           application_statuses=application_statuses)

@app.route('/student/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'student_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    s_id = session['student_id']
    applied_job = job.query.get(job_id)
    already_applied = application.query.filter_by(student_id=s_id, job_id=job_id).first()
    
    if not already_applied:
        new_app = application(student_id=s_id, job_id=job_id, company_name=applied_job.company_name)
        db.session.add(new_app)
        db.session.commit()
    return redirect(url_for('student_dashboard'))
@app.route('/company/post_job', methods=['POST'])
def post_job():
    j_title = request.form['title']
    j_desc = request.form['description']
    j_salary = request.form['salary']
    c_name = session.get('company_name', 'Unknown Company')
    new_job = job(title=j_title, description=j_desc, salary=j_salary, company_name=c_name)
    db.session.add(new_job)
    db.session.commit()
    return redirect(url_for('company_dashboard'))
@app.route('/company/update_app/<int:app_id>/<string:new_status>', methods=['POST'])
def update_application(app_id, new_status):
    if 'company_name' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
    app_to_update = application.query.get(app_id)
    if app_to_update and app_to_update.company_name == session['company_name']:
        app_to_update.status = new_status
        db.session.commit()
    return redirect(url_for('company_dashboard'))

with app.app_context():
    db.create_all()
    print("DATABASE DEPLOYED")
    admin_user=admin.query.filter_by(username='admin').first()
    if not admin_user:
        my_admin=admin(username='admin',admin_id=1,password='qwerty')
        db.session.add(my_admin)
        db.session.commit()

        print("created adminz")
if __name__=='__main__':
    app.run(debug=True,port=5001)
