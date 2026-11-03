import os
import csv
import io
from functools import wraps
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-key-change-before-deploy")

database_url = os.environ.get("DATABASE_URL", "sqlite:///survivor_don.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(40), nullable=False)
    student_id = db.Column(db.String(80), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


with app.app_context():
    db.create_all()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_text = request.form.get("age", "").strip()
        course = request.form.get("course", "").strip()
        gender = request.form.get("gender", "").strip()
        student_id = request.form.get("student_id", "").strip()

        if not all([name, age_text, course, gender, student_id]):
            flash("Please complete every field.", "danger")
            return render_template("register.html")

        try:
            age = int(age_text)
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            flash("Please enter a valid age.", "danger")
            return render_template("register.html")

        if Student.query.filter_by(student_id=student_id).first():
            flash("That Student ID has already been registered. Please check it and try again.", "danger")
            return render_template("register.html")

        student = Student(
            name=name,
            age=age,
            course=course,
            gender=gender,
            student_id=student_id,
        )
        db.session.add(student)
        db.session.commit()
        return render_template("success.html", student_name=name)

    return render_template("register.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
        password_plain = os.environ.get("ADMIN_PASSWORD", "ChangeThisPassword123!")

        entered_username = request.form.get("username", "")
        entered_password = request.form.get("password", "")

        password_ok = (
            check_password_hash(password_hash, entered_password)
            if password_hash
            else entered_password == password_plain
        )

        if entered_username == username and password_ok:
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))

        flash("Incorrect username or password.", "danger")

    return render_template("login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def dashboard():
    search = request.args.get("q", "").strip()
    query = Student.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Student.name.ilike(like),
                Student.course.ilike(like),
                Student.student_id.ilike(like),
            )
        )
    students = query.order_by(Student.created_at.desc()).all()
    total_students = Student.query.count()
    return render_template("dashboard.html", students=students, total_students=total_students, search=search)


@app.route("/admin/export.csv")
@admin_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Age", "Course", "Gender", "Student ID", "Registration Date"])
    for student in Student.query.order_by(Student.created_at.desc()).all():
        writer.writerow([
            student.name,
            student.age,
            student.course,
            student.gender,
            student.student_id,
            student.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=survivor_don_students.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
