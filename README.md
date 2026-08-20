# Placement-portal

A robust, full-stack web application designed to streamline the campus recruitment process. The portal establishes a secure ecosystem connecting Students, Companies, and Administrators, allowing seamless job posting, profile management, and recruitment tracking.

<ul>
    <li><strong>Role-Based Access Control (RBAC):</strong> Secure, isolated, and privilege-specific dashboards for Admins, Companies, and Students using a unified login gateway.</li>
    <li><strong>Triple-Filter Eligibility Algorithm:</strong> A dynamic backend evaluation engine that strictly matches a student's Degree, Branch, and CGPA against specific job requirements. Ineligible students are programmatically restricted from viewing or applying to unmatched postings.</li>
    <li><strong>Asynchronous Background Tasks:</strong> Integrates <strong>Celery</strong> and <strong>Redis</strong> to handle heavy background processes (like sending bulk status update emails to students) without blocking the main web server, ensuring a lightning-fast UI.</li>
    <li><strong>Admin Moderation Workflow:</strong> Protects the platform's integrity by forcing all new company registrations and job postings into a 'Pending' state until explicitly approved by the Placement Cell Admin.</li>
    <li><strong>Application Tracking Engine:</strong> Real-time visibility into the recruitment pipeline. Students and companies can track application states (Pending, Accepted, Rejected) instantly.</li>
</ul>

<h2>Tech Stack</h2>
<table border="1">
    <thead>
        <tr>
            <th>Component</th>
            <th>Technology</th>
            <th>Purpose</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Backend</strong></td>
            <td>Python, Flask</td>
            <td>Core application logic, routing, and API endpoints.</td>
        </tr>
        <tr>
            <td><strong>Database</strong></td>
            <td>SQLite, SQLAlchemy</td>
            <td>Object Relational Mapping (ORM) and relational data storage.</td>
        </tr>
        <tr>
            <td><strong>Task Queue</strong></td>
            <td>Celery, Redis</td>
            <td>Message brokering and asynchronous background task processing.</td>
        </tr>
        <tr>
            <td><strong>Frontend</strong></td>
            <td>HTML5, Jinja2, Bootstrap 5</td>
            <td>Dynamic template rendering and responsive, mobile-friendly UI.</td>
        </tr>
        <tr>
            <td><strong>Security</strong></td>
            <td>Flask-Session, bcrypt</td>
            <td>Secure session management and password hashing.</td>
        </tr>
    </tbody>
</table>

<h2>Database Schema & Relationships</h2>
<p>The system is built on a highly relational data model:</p>
<ul>
    <li><strong>Entities:</strong> <code>admin</code>, <code>student</code>, <code>company</code>, <code>job</code>, <code>application</code>, <code>placement</code></li>
    <li><strong>Relationships:</strong>
        <ul>
            <li><code>Company</code> &rarr; <code>Job</code> (One-to-Many)</li>
            <li><code>Job</code> &rarr; <code>Application</code> (One-to-Many)</li>
            <li><code>Student</code> &rarr; <code>Application</code> (One-to-Many)</li>
        </ul>
    </li>
</ul>

<h2>Core API Endpoints</h2>
<table border="1">
    <thead>
        <tr>
            <th>Endpoint</th>
            <th>Method</th>
            <th>Role</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>/login</code></td>
            <td>POST</td>
            <td>All</td>
            <td>Authenticates users and initializes specific role sessions.</td>
        </tr>
        <tr>
            <td><code>/company/post_job</code></td>
            <td>POST</td>
            <td>Company</td>
            <td>Creates a new job posting with strict eligibility parameters.</td>
        </tr>
        <tr>
            <td><code>/student/apply/&lt;job_id&gt;</code></td>
            <td>POST</td>
            <td>Student</td>
            <td>Evaluates eligibility and submits a student application.</td>
        </tr>
        <tr>
            <td><code>/admin/approve/&lt;company_id&gt;</code></td>
            <td>POST</td>
            <td>Admin</td>
            <td>Moderation endpoint to activate pending recruiter accounts.</td>
        </tr>
        <tr>
            <td><code>/company/update_app/&lt;app_id&gt;</code></td>
            <td>POST</td>
            <td>Company</td>
            <td>Updates application status and triggers async email notification.</td>
        </tr>
    </tbody>
</table>
