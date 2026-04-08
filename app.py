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


if __name__ == "__main__":
    app.run(debug=True)