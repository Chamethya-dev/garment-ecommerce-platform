from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth = Blueprint('auth', __name__)

# --- Authentication Routes ---

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Please login.', 'danger')
            return redirect(url_for('auth.login'))

        # Create new user
        new_user = User(name=name, email=email, phone=phone)
        new_user.set_password(password) # Hashes the password automatically
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        # Redirect to the page they were trying to access, or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.home'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# --- Custom Decorators ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) # Forbidden access
        return f(*args, **kwargs)
    return decorated_function