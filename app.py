from flask import Flask, render_template, request, redirect, session
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

#LOGIN

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        db = get_db()
        cur = db.cursor()
        if role == "admin":
            cur.execute("SELECT * FROM admin WHERE username=? AND password=?",
                        (email,password))
            user = cur.fetchone()
            if user:
                session["admin"] = email
                return redirect("/admin/dashboard")
        elif role == "student":
            cur.execute("""
            SELECT * FROM students 
            WHERE email=? AND password=? AND status='active'
            """,(email,password))
            user = cur.fetchone()
            if user:
                session["student"] = user["id"]
                return redirect("/student/dashboard")
        elif role == "company":
            cur.execute("""
            SELECT * FROM companies
            WHERE email=? AND password=?
            AND status='approved'
            """,(email,password))
            user = cur.fetchone()
            if user:
                session["company"] = user["id"]
                return redirect("/company/dashboard")
    return render_template("login.html")

@app.route("/register/student", methods=["GET","POST"])
def register_student():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        contact = request.form["contact"]
        resume = request.form["resume"]
        db = get_db()
        db.execute("""
        INSERT INTO students(name,email,password,contact,resume)
        VALUES(?,?,?,?,?)
        """,(name,email,password,contact,resume))
        db.commit()
        return redirect("/")
    return render_template("register_student.html")

@app.route("/register/company", methods=["GET","POST"])
def register_company():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        website = request.form["website"]
        hr = request.form["hr"]
        db = get_db()
        db.execute("""
        INSERT INTO companies(name,email,password,website,hr_contact)
        VALUES(?,?,?,?,?)
        """,(name,email,password,website,hr))
        db.commit()
        return redirect("/")
    return render_template("register_company.html")

#ADMIN

@app.route("/admin/dashboard")
def admin_dashboard():
    db = get_db()
    students = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    companies = db.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    drives = db.execute("SELECT COUNT(*) FROM drives").fetchone()[0]
    applications = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    return render_template(
        "admin/dashboard.html",
        students=students,
        companies=companies,
        drives=drives,
        applications=applications
    )

@app.route("/admin/companies")
def view_companies():
    db = get_db()
    companies = db.execute("SELECT * FROM companies").fetchall()
    return render_template("admin/companies.html",companies=companies)

@app.route("/admin/approve_company/<int:id>")
def approve_company(id):
    db = get_db()
    db.execute("UPDATE companies SET status='approved' WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/companies")

@app.route("/admin/reject_company/<int:id>")
def reject_company(id):
    db = get_db()
    db.execute("UPDATE companies SET status='rejected' WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/companies")

@app.route("/admin/blacklist_company/<int:id>")
def blacklist_company(id):
    db = get_db()
    db.execute("UPDATE companies SET status='blacklisted' WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/companies")

@app.route("/admin/students")
def admin_students():
    if "admin" not in session:
        return redirect("/")
    db = get_db()
    students = db.execute("""
        SELECT * FROM students
    """).fetchall()
    return render_template("admin/students.html", students=students)

@app.route("/admin/blacklist_student/<int:id>")
def blacklist_student(id):
    db = get_db()
    db.execute("""
        UPDATE students SET status='blacklisted'
        WHERE id=?
    """,(id,))
    db.commit()
    return redirect("/admin/students")

@app.route("/admin/search")
def admin_search():
    query = request.args.get("q")
    db = get_db()
    students = db.execute("""
        SELECT * FROM students WHERE name LIKE ?
    """,('%'+query+'%',)).fetchall()
    companies = db.execute("""
        SELECT * FROM companies WHERE name LIKE ?
    """,('%'+query+'%',)).fetchall()
    return render_template("admin/search.html",
                           students=students,
                           companies=companies)

@app.route("/admin/drives")
def admin_drives():
    if "admin" not in session:
        return redirect("/")
    db = get_db()
    drives = db.execute("""
        SELECT drives.*, companies.name AS company_name
        FROM drives
        JOIN companies ON drives.company_id = companies.id
    """).fetchall()
    return render_template("admin/drives.html", drives=drives)

@app.route("/admin/approve_drive/<int:id>")
def approve_drive(id):
    if "admin" not in session:
        return redirect("/")
    db = get_db()
    db.execute("""
        UPDATE drives SET status='approved'
        WHERE id=?
    """, (id,))
    db.commit()
    return redirect("/admin/drives")

@app.route("/admin/reject_drive/<int:id>")
def reject_drive(id):
    if "admin" not in session:
        return redirect("/")
    db = get_db()
    db.execute("""
        UPDATE drives SET status='rejected'
        WHERE id=?
    """, (id,))
    db.commit()
    return redirect("/admin/drives")

@app.route("/admin/applications")
def admin_applications():
    if "admin" not in session:
        return redirect("/")
    db = get_db()
    applications = db.execute("""
        SELECT applications.*,
               students.name AS student_name,
               drives.job_title,
               companies.name AS company_name
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN drives ON applications.drive_id = drives.id
        JOIN companies ON drives.company_id = companies.id
    """).fetchall()
    return render_template("admin/applications.html", applications=applications)

#COMPANY

@app.route("/company/dashboard")
def company_dashboard():
    if "company" not in session:
        return redirect("/")
    db = get_db()
    drives = db.execute("""
        SELECT * FROM drives
        WHERE company_id=?
    """, (session["company"],)).fetchall()
    return render_template("company/dashboard.html", drives=drives)

@app.route("/company/update_status/<int:app_id>/<status>")
def update_status(app_id, status):
    if "company" not in session:
        return redirect("/")
    db = get_db()
    db.execute("""
        UPDATE applications
        SET status=?
        WHERE id=?
    """, (status, app_id))
    db.commit()
    return redirect(request.referrer)

@app.route("/company/applications/<int:drive_id>")
def company_applications(drive_id):
    if "company" not in session:
        return redirect("/")
    db = get_db()
    apps = db.execute("""
    SELECT applications.*, 
           students.name, 
           students.resume,
           drives.job_title
    FROM applications
    JOIN students ON applications.student_id = students.id
    JOIN drives ON applications.drive_id = drives.id
    WHERE drives.company_id=? 
    AND drives.id=?
    AND students.status != 'blacklisted'
    """, (session["company"], drive_id)).fetchall()
    return render_template("company/applications.html", apps=apps)

@app.route("/company/create_drive", methods=["GET","POST"])
def create_drive():
    if "company" not in session:
        return redirect("/")
    if request.method == "POST":
        title = request.form["title"]
        skills = request.form["skills"]
        experience = request.form["experience"]
        salary = request.form["salary"]
        db = get_db()
        db.execute("""
        INSERT INTO drives(company_id, job_title, skills, experience, salary)
        VALUES(?,?,?,?,?)
    """,(session["company"], title, skills, experience, salary))
        db.commit()
        return redirect("/company/dashboard")
    return render_template("company/create_drive.html")

@app.route("/company/close_drive/<int:id>")
def close_drive(id):
    db = get_db()
    db.execute("""
        UPDATE drives SET status='closed'
        WHERE id=?
    """,(id,))
    db.commit()
    return redirect("/company/dashboard")

@app.route("/company/delete_drive/<int:id>")
def delete_drive(id):
    db = get_db()
    db.execute("DELETE FROM drives WHERE id=?", (id,))
    db.commit()
    return redirect("/company/dashboard")
@app.route("/company/shortlisted/<int:drive_id>")
def company_shortlisted(drive_id):
    if "company" not in session:
        return redirect("/")
    db = get_db()
    apps = db.execute("""
    SELECT applications.*, 
           students.name, 
           students.resume,
           drives.job_title
    FROM applications
    JOIN students ON applications.student_id = students.id
    JOIN drives ON applications.drive_id = drives.id
    WHERE drives.company_id=? 
    AND drives.id=? 
    AND applications.status='Shortlisted'
    AND students.status != 'blacklisted'
    """, (session["company"], drive_id)).fetchall()
    return render_template("company/shortlisted.html", apps=apps)

#STUDENT

@app.route("/student/dashboard")
def student_dashboard():
    if "student" not in session:
        return redirect("/")
    db = get_db()
    # Get all approved jobs
    drives = db.execute("""
    SELECT drives.*, companies.name as company
    FROM drives
    JOIN companies ON drives.company_id = companies.id
    WHERE drives.status='approved'
    AND companies.status != 'blacklisted'
    """).fetchall()
    # Get applied jobs
    applied = db.execute("""
        SELECT drive_id FROM applications 
        WHERE student_id=?
    """, (session["student"],)).fetchall()
    applied_ids = [a["drive_id"] for a in applied]
    return render_template("student/dashboard.html",drives=drives,applied_ids=applied_ids)

@app.route("/student/profile", methods=["GET","POST"])
def student_profile():
    if "student" not in session:
        return redirect("/")
    db = get_db()
    if request.method == "POST":
        resume = request.form["resume"]
        db.execute("""
            UPDATE students SET resume=?
            WHERE id=?
        """,(resume, session["student"]))
        db.commit()
    student = db.execute("""
        SELECT * FROM students WHERE id=?
    """,(session["student"],)).fetchone()
    return render_template("student/profile.html", student=student)

@app.route("/apply/<int:drive_id>", methods=["GET", "POST"])
def apply_job(drive_id):
    if "student" not in session:
        return redirect("/")
    db = get_db()
    student_id = session["student"]
    drive = db.execute("""
        SELECT drives.*, companies.name as company
        FROM drives
        JOIN companies ON drives.company_id = companies.id
        WHERE drives.id=?
    """, (drive_id,)).fetchone()
    if request.method == "POST":
        existing = db.execute("""
            SELECT 1 FROM applications 
            WHERE student_id=? AND drive_id=?
        """, (student_id, drive_id)).fetchone()
        if not existing:
            db.execute("""
                INSERT INTO applications(student_id, drive_id, status)
                VALUES(?, ?, 'Applied')
            """, (student_id, drive_id))
            db.commit()
        return redirect("/student/dashboard")
    return render_template("student/apply.html", drive=drive)

@app.route("/student/search")
def student_search():
    if "student" not in session:
        return redirect("/")
    query = request.args.get("q", "").strip()
    db = get_db()
    if query:
        drives = db.execute("""
        SELECT drives.*, companies.name as company
        FROM drives
        JOIN companies ON drives.company_id = companies.id
        WHERE drives.status='approved'
        AND companies.status != 'blacklisted'
        AND (
            companies.name LIKE ? OR
            drives.job_title LIKE ? OR
            drives.skills LIKE ?
        )
        """, ('%'+query+'%', '%'+query+'%', '%'+query+'%')).fetchall()
    else:
        drives = db.execute("""
        SELECT drives.*, companies.name as company
        FROM drives
        JOIN companies ON drives.company_id = companies.id
        WHERE drives.status='approved'
        """).fetchall()
    return render_template("student/search.html",
                           drives=drives,
                           query=query)

@app.route("/student/applications")
def student_applications():
    if "student" not in session:
        return redirect("/")
    db = get_db()
    apps = db.execute("""
        SELECT applications.*, drives.job_title, companies.name AS company
        FROM applications
        JOIN drives ON applications.drive_id = drives.id
        JOIN companies ON drives.company_id = companies.id
        WHERE student_id=?
    """, (session["student"],)).fetchall()
    return render_template("student/applications.html", apps=apps)


if __name__ == "__main__":
    app.run(debug=True)