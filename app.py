"""
AI-Powered Expense Tracker - Main Application
Flask backend with authentication, expense management, and AI categorization
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from functools import wraps
import os
from model import ExpenseCategorizer

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Initialize ML model
categorizer = ExpenseCategorizer()

# Database configuration
DATABASE = 'database.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Login required decorator
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user into database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')
        
        # Verify user credentials
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Login successful
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all expenses and statistics"""
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all expenses for the user
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE user_id = ? 
        ORDER BY date DESC
    ''', (user_id,))
    expenses = cursor.fetchall()
    
    # Calculate total spent
    cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    total_spent = result['total'] if result['total'] else 0.0
    
    # Calculate category-wise summary
    cursor.execute('''
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM expenses 
        WHERE user_id = ? 
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id,))
    category_summary = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         expenses=expenses,
                         total_spent=total_spent,
                         category_summary=category_summary,
                         username=session['username'])

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    """Add new expense page"""
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '')
        manual_category = request.form.get('category', '').strip()
        
        # Validation
        if not description:
            flash('Description is required.', 'danger')
            return render_template('add_expense.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('Please enter a valid positive amount.', 'danger')
            return render_template('add_expense.html')
        
        # Predict category using AI if not manually selected
        if manual_category:
            category = manual_category
        else:
            category = categorizer.predict(description)
        
        # Get current date
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert expense into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, description, amount, category, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], description, amount, category, date))
        conn.commit()
        conn.close()
        
        flash(f'Expense added successfully! Category: {category}', 'success')
        return redirect(url_for('dashboard'))
    
    # Get available categories for manual selection
    categories = categorizer.get_categories()
    return render_template('add_expense.html', categories=categories)

@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    """Delete an expense"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify the expense belongs to the current user
    cursor.execute('SELECT user_id FROM expenses WHERE id = ?', (expense_id,))
    expense = cursor.fetchone()
    
    if expense and expense['user_id'] == session['user_id']:
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        flash('Expense deleted successfully.', 'success')
    else:
        flash('Expense not found or unauthorized.', 'danger')
    
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists(DATABASE):
        init_db()
    
    # Train the ML model
    print("Training AI categorization model...")
    categorizer.train()
    print("Model training complete!")
    
    # Run the Flask app
    print("\n=== AI-Powered Expense Tracker ===")
    print("Server starting on http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)