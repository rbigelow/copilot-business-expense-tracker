# Business Expense Tracker

A modern Flask web application for tracking business expenses with file uploads, categories, reports, and API export capabilities.

## Features

- **User Authentication**: Secure login, registration, and password reset functionality
- **Expense Management**: Create, read, update, and delete expenses
- **File Uploads**: Attach receipts and documents to expenses
- **Categories**: Organize expenses with custom categories
- **Reports**: View monthly and category-based expense reports
- **Data Export**: Export expenses to CSV format via web interface or JSON via API
- **Responsive UI**: Clean, modern interface built with Bootstrap 5
- **RESTful API**: Access and manage expenses programmatically

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rbigelow/copilot-business-expense-tracker.git
cd copilot-business-expense-tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env to set SECRET_KEY and other configuration options
```

5. Run the application:
```bash
# For development (with debug mode):
FLASK_DEBUG=true python run.py

# For production (without debug mode):
python run.py
```
```bash
python run.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Web Interface

1. **Register**: Create a new account at `/auth/register`
2. **Login**: Sign in at `/auth/login`
3. **Dashboard**: View expense summary and statistics
4. **Add Expense**: Click "Add Expense" to create a new expense entry
5. **Categories**: Manage expense categories
6. **Reports**: View detailed reports and export data
7. **Export**: Download expenses as CSV from the Reports page

### API Endpoints

All API endpoints require authentication. Include your session cookie or implement token-based authentication.

**Base URL**: `/api/v1`

#### Get All Expenses
```bash
GET /api/v1/expenses
Query Parameters:
  - page: Page number (default: 1)
  - per_page: Items per page (default: 20)
  - category_id: Filter by category
```

#### Get Single Expense
```bash
GET /api/v1/expenses/{id}
```

#### Create Expense
```bash
POST /api/v1/expenses
Content-Type: application/json

{
  "title": "Office Supplies",
  "amount": 49.99,
  "date": "2026-02-11",
  "description": "Purchased pens and paper",
  "category_id": 1
}
```

#### Update Expense
```bash
PUT /api/v1/expenses/{id}
Content-Type: application/json

{
  "title": "Updated Title",
  "amount": 59.99
}
```

#### Delete Expense
```bash
DELETE /api/v1/expenses/{id}
```

#### Get Categories
```bash
GET /api/v1/categories
```

#### Export Data (JSON)
```bash
GET /api/v1/export?format=json
```

### Example API Usage

Using curl:
```bash
# Login first to establish session
curl -c cookies.txt -X POST http://localhost:5000/auth/login \
  -d "username=youruser&password=yourpass"

# Get expenses
curl -b cookies.txt http://localhost:5000/api/v1/expenses

# Create expense
curl -b cookies.txt -X POST http://localhost:5000/api/v1/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch Meeting","amount":45.50,"date":"2026-02-11"}'

# Export as JSON
curl -b cookies.txt http://localhost:5000/api/v1/export
```

Using Python requests:
```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/auth/login', 
             data={'username': 'youruser', 'password': 'yourpass'})

# Get expenses
response = session.get('http://localhost:5000/api/v1/expenses')
expenses = response.json()

# Create expense
new_expense = {
    'title': 'Business Dinner',
    'amount': 125.00,
    'date': '2026-02-11',
    'category_id': 1
}
response = session.post('http://localhost:5000/api/v1/expenses', json=new_expense)
```

## Configuration

The application can be configured using environment variables:

- `SECRET_KEY`: Secret key for session management (default: 'dev-secret-key-change-in-production')
- `DATABASE_URL`: Database connection string (default: SQLite in project directory)

## Project Structure

```
copilot-business-expense-tracker/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main routes (dashboard, home)
│   │   ├── expenses.py      # Expense management routes
│   │   └── api.py           # API endpoints
│   └── templates/           # HTML templates
│       ├── base.html        # Base template
│       ├── index.html       # Home page
│       ├── dashboard.html   # Dashboard
│       ├── auth/            # Authentication templates
│       └── expenses/        # Expense templates
├── uploads/                 # Uploaded files storage
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## Technologies Used

- **Backend**: Flask 3.0
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **File Handling**: Werkzeug

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
