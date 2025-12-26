# 💰 AI-Powered Expense Tracker

A complete full-stack web application for tracking expenses with AI-powered automatic categorization using Machine Learning.

## 🌟 Features

- **User Authentication**: Secure registration and login system with password hashing
- **AI Categorization**: Automatic expense categorization using scikit-learn (TF-IDF + Naive Bayes)
- **Expense Management**: Add, view, and delete expenses
- **Smart Dashboard**: Visual summary with total spent and category-wise breakdown
- **Offline ML Model**: No internet required - all AI processing happens locally
- **Clean UI**: Modern, responsive design that works on all devices
- **Session-based Security**: Protected routes with login requirements

## 🤖 AI Categories

The AI model automatically categorizes expenses into:
- 🍔 **Food**: Restaurants, groceries, coffee, meals
- ✈️ **Travel**: Uber, flights, hotels, gas, parking
- 📄 **Bills**: Electricity, rent, subscriptions, insurance
- 🛒 **Shopping**: Clothes, electronics, furniture, online orders
- 🎬 **Entertainment**: Movies, concerts, streaming services, games

## 🔧 Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3 (no JavaScript frameworks)
- **Database**: SQLite
- **ML**: scikit-learn (TF-IDF Vectorizer + Naive Bayes)
- **Authentication**: Werkzeug password hashing
- **Hosting**: Localhost

## 📁 Project Structure

```
expense_tracker/
│
├── app.py                    # Main Flask application
├── model.py                  # ML model training and prediction
├── database.db               # SQLite database (auto-created)
├── expense_model.pkl         # Trained ML model (auto-created)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── templates/
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # Main dashboard
│   └── add_expense.html     # Add expense form
│
└── static/
    └── style.css            # Main stylesheet
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Create Project Directory

```bash
mkdir expense_tracker
cd expense_tracker
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Directory Structure

```bash
# On Windows
mkdir templates static

# On macOS/Linux
mkdir -p templates static
```

### Step 5: Add All Files

Place all the files in their respective directories:
- `app.py` and `model.py` in the root directory
- All HTML files in the `templates/` directory
- `style.css` in the `static/` directory
- `requirements.txt` in the root directory

### Step 6: Run the Application

```bash
python app.py
```

The application will:
1. Initialize the SQLite database
2. Train the AI categorization model
3. Start the Flask server on `http://127.0.0.1:5000`

### Step 7: Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## 📖 Usage Guide

### 1. Register an Account

- Click "Register here" on the login page
- Choose a username (min 3 characters)
- Set a password (min 6 characters)
- Confirm your password

### 2. Login

- Enter your username and password
- Click "Login"

### 3. Add Expenses

- Click "+ Add Expense" button
- Enter a description (e.g., "Grocery shopping at Walmart")
- Enter the amount
- (Optional) Manually select a category, or let AI decide
- Click "Add Expense"

### 4. View Dashboard

- See all your expenses in a table
- View total amount spent
- Check category-wise summary
- Monitor your spending patterns

### 5. Delete Expenses

- Click "Delete" button next to any expense
- Confirm deletion

### 6. Logout

- Click "Logout" to end your session

## 🧠 How AI Categorization Works

The application uses a **TF-IDF (Term Frequency-Inverse Document Frequency) Vectorizer** combined with a **Multinomial Naive Bayes Classifier**:

1. **Training Phase** (on app startup):
   - The model trains on 100+ example expense descriptions
   - TF-IDF converts text into numerical features
   - Naive Bayes learns patterns for each category

2. **Prediction Phase** (when adding expenses):
   - Your description is converted to TF-IDF features
   - The classifier predicts the most likely category
   - The expense is automatically tagged

### Example Predictions

| Description | Predicted Category |
|-------------|-------------------|
| "lunch at chipotle" | Food 🍔 |
| "uber to airport" | Travel ✈️ |
| "netflix subscription" | Bills 📄 |
| "new laptop from amazon" | Shopping 🛒 |
| "movie tickets" | Entertainment 🎬 |

## 🔒 Security Features

- **Password Hashing**: Passwords are securely hashed using Werkzeug
- **Session Management**: Flask sessions protect user data
- **Login Required**: Protected routes redirect to login
- **User Isolation**: Each user only sees their own expenses
- **SQL Injection Protection**: Parameterized queries prevent SQL injection

## 🎨 Customization

### Change Categories

Edit the `categories` list in `model.py`:
```python
self.categories = ['Food', 'Travel', 'Bills', 'Shopping', 'Entertainment']
```

### Add Training Data

Extend the `get_training_data()` method in `model.py` with more examples.

### Modify Colors

Update CSS variables in `static/style.css`:
```css
:root {
    --primary-color: #4f46e5;
    --success-color: #10b981;
    /* etc. */
}
```

### Change Secret Key

**Important for production**: Update the secret key in `app.py`:
```python
app.secret_key = 'your-unique-secret-key-here'
```

## 📊 Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| username | TEXT | Unique username |
| password | TEXT | Hashed password |

### Expenses Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| user_id | INTEGER | Foreign key to users |
| description | TEXT | Expense description |
| amount | REAL | Expense amount |
| category | TEXT | AI-predicted category |
| date | TEXT | Timestamp |

## 🐛 Troubleshooting

### Port Already in Use

If port 5000 is busy, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module Not Found Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Database Locked Error

Close any other connections to `database.db` or delete it to start fresh.

### Model Training Fails

Delete `expense_model.pkl` and restart the app to retrain.

## 🚀 Deployment Notes

For production deployment:

1. **Disable Debug Mode**:
   ```python
   app.run(debug=False)
   ```

2. **Change Secret Key**: Use a strong, random secret key

3. **Use Production Server**: Deploy with Gunicorn or uWSGI instead of Flask's development server

4. **Add HTTPS**: Use a reverse proxy like Nginx with SSL

5. **Database**: Consider PostgreSQL for production instead of SQLite

## 📝 License

This project is open-source and available for educational purposes.