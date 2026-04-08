from flask import Flask, render_template, request, redirect, session
from database import get_db, init_db
import datetime

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

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

if __name__ == "__main__":
    app.run(debug=True)