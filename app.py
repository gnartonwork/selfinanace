from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1'  # Use a secure secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Set a default username and hashed password for demonstration
default_username = 'me'
default_password = '12345678'
hashed_default_password = bcrypt.generate_password_hash(default_password).decode('utf-8')

with app.app_context():
    db.create_all()
    # Check if the default user exists
    if not User.query.filter_by(username=default_username).first():
        default_user = User(username=default_username, password=hashed_default_password)
        db.session.add(default_user)
        db.session.commit()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

# Bổ sung một hàm kiểm tra đăng nhập
def is_logged_in():
    return 'username' in session

# Bổ sung một decorator để kiểm tra đăng nhập trước khi truy cập các trang sau
def login_required_decorator(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if is_logged_in():
            return route_function(*args, **kwargs)
        return redirect(url_for('login'))
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))  # Chuyển hướng đến trang dashboard
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required_decorator
def dashboard():
    # Add logic for your dashboard here
    return render_template('dashboard.html', username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/manage_account')
@login_required_decorator
def manage_account():
    return render_template('manage_account.html', username=session['username'])

@app.route('/manage_finance')
@login_required_decorator
def manage_finance():
    return render_template('manage_finance.html', username=session['username'])

@app.route('/write_report')
@login_required_decorator
def write_report():
    return render_template('write_report.html', username=session['username'])

@app.route('/maintenance')
@login_required_decorator
def maintenance():
    return render_template('maintenance.html', username=session['username'])

@app.route('/net_profit')
@login_required_decorator
def net_profit():
    return redirect(url_for('calculate_net_profit'))

# ... (các route khác)

if __name__ == '__main__':
    app.run(debug=True)
