import os
import csv
from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Expense, Category, Attachment
from app.forms import ExpenseForm, CategoryForm

bp = Blueprint('expenses', __name__, url_prefix='/expenses')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Expense.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Expense.date <= end)
        except ValueError:
            pass
    
    expenses = query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    return render_template('expenses/list.html', 
                         title='Expenses',
                         expenses=expenses,
                         categories=categories)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ExpenseForm()
    form.category_id.choices = [(0, 'No Category')] + [
        (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()
    ]
    
    if form.validate_on_submit():
        expense = Expense(
            title=form.title.data,
            amount=form.amount.data,
            date=form.date.data,
            description=form.description.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.flush()  # Get the expense ID
        
        # Handle file upload
        if form.files.data:
            file = form.files.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                attachment = Attachment(
                    filename=file.filename,
                    filepath=filepath,
                    expense_id=expense.id
                )
                db.session.add(attachment)
        
        db.session.commit()
        flash('Expense created successfully!', 'success')
        return redirect(url_for('expenses.list'))
    
    return render_template('expenses/form.html', 
                         title='Create Expense',
                         form=form,
                         action='Create')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)
    form.category_id.choices = [(0, 'No Category')] + [
        (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()
    ]
    
    if form.validate_on_submit():
        expense.title = form.title.data
        expense.amount = form.amount.data
        expense.date = form.date.data
        expense.description = form.description.data
        expense.category_id = form.category_id.data if form.category_id.data != 0 else None
        
        # Handle file upload
        if form.files.data:
            file = form.files.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                attachment = Attachment(
                    filename=file.filename,
                    filepath=filepath,
                    expense_id=expense.id
                )
                db.session.add(attachment)
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses.list'))
    
    return render_template('expenses/form.html', 
                         title='Edit Expense',
                         form=form,
                         action='Update',
                         expense=expense)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Delete associated files
    for attachment in expense.attachments:
        if os.path.exists(attachment.filepath):
            os.remove(attachment.filepath)
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses.list'))


@bp.route('/export')
@login_required
def export():
    format = request.args.get('format', 'csv')
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    if format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Title', 'Amount', 'Category', 'Description'])
        
        for expense in expenses:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                expense.title,
                expense.amount,
                expense.category.name if expense.category else 'N/A',
                expense.description or ''
            ])
        
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'expenses_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    
    return jsonify({'error': 'Invalid format'}), 400


@bp.route('/categories')
@login_required
def categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('expenses/categories.html', 
                         title='Categories',
                         categories=categories)


@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('expenses.categories'))
    
    return render_template('expenses/category_form.html', 
                         title='Create Category',
                         form=form,
                         action='Create')


@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('expenses.categories'))
    
    return render_template('expenses/category_form.html', 
                         title='Edit Category',
                         form=form,
                         action='Update',
                         category=category)


@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('expenses.categories'))


@bp.route('/report')
@login_required
def report():
    from sqlalchemy import func, extract
    from datetime import datetime
    
    # Get filter parameters
    current_year = datetime.utcnow().year
    year = request.args.get('year', current_year, type=int)
    category_id = request.args.get('category', type=int)
    
    query = Expense.query.filter_by(user_id=current_user.id)
    query = query.filter(extract('year', Expense.date) == year)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Monthly expenses
    monthly_expenses = db.session.query(
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year
    ).group_by('month').all()
    
    # Category breakdown
    category_expenses = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year
    ).group_by(Category.name).all()
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    total = query.with_entities(func.sum(Expense.amount)).scalar() or 0
    
    # Generate year range for the dropdown
    year_range = range(2020, current_year + 2)
    
    return render_template('expenses/report.html',
                         title='Expense Report',
                         year=year,
                         monthly_expenses=monthly_expenses,
                         category_expenses=category_expenses,
                         categories=categories,
                         total=total,
                         year_range=year_range)
