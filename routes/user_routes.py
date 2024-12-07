from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User, db
from flask_bcrypt import Bcrypt


user_routes = Blueprint('user_routes', __name__)
bcrypt = Bcrypt()
@user_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        email = request.form["email"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for("user_routes.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!")
            return redirect(url_for("user_routes.register"))

        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login")
        return redirect(url_for("user_routes.login"))
    return render_template("register.html")

@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("user_routes.dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("user_routes.login"))
    return render_template("login.html")

@user_routes.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user)
    return redirect(url_for("user_routes.login"))
@user_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("user_routes.login"))