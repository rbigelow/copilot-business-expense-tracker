from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html', title='Home')


@bp.route('/dashboard')
@login_required
def dashboard():
    from app.models import Expense, Category
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Get statistics
    total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    expense_count = Expense.query.filter_by(user_id=current_user.id).count()
    category_count = Category.query.filter_by(user_id=current_user.id).count()
    
    # Get this month's expenses
    today = datetime.utcnow()
    first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= first_day
    ).scalar() or 0
    
    # Get expenses by category
    expenses_by_category = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == current_user.id
    ).group_by(Category.name).all()
    
    # Get recent expenses
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.date.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', 
                         title='Dashboard',
                         total_expenses=total_expenses,
                         expense_count=expense_count,
                         category_count=category_count,
                         this_month=this_month,
                         expenses_by_category=expenses_by_category,
                         recent_expenses=recent_expenses)
