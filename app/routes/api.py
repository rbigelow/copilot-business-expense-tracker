from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Expense, Category
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api/v1')


@bp.route('/expenses', methods=['GET'])
@login_required
def get_expenses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    expenses = query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'expenses': [expense.to_dict() for expense in expenses.items],
        'total': expenses.total,
        'pages': expenses.pages,
        'current_page': expenses.page
    })


@bp.route('/expenses/<int:id>', methods=['GET'])
@login_required
def get_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify(expense.to_dict())


@bp.route('/expenses', methods=['POST'])
@login_required
def create_expense():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('amount'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        expense = Expense(
            title=data['title'],
            amount=float(data['amount']),
            date=datetime.fromisoformat(data.get('date', datetime.utcnow().isoformat())),
            description=data.get('description'),
            category_id=data.get('category_id'),
            user_id=current_user.id
        )
        
        from app import db
        db.session.add(expense)
        db.session.commit()
        
        return jsonify(expense.to_dict()), 201
    except (ValueError, KeyError) as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/expenses/<int:id>', methods=['PUT'])
@login_required
def update_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        if 'title' in data:
            expense.title = data['title']
        if 'amount' in data:
            expense.amount = float(data['amount'])
        if 'date' in data:
            expense.date = datetime.fromisoformat(data['date'])
        if 'description' in data:
            expense.description = data['description']
        if 'category_id' in data:
            expense.category_id = data['category_id']
        
        from app import db
        db.session.commit()
        
        return jsonify(expense.to_dict())
    except (ValueError, KeyError) as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/expenses/<int:id>', methods=['DELETE'])
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    from app import db
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({'message': 'Expense deleted successfully'}), 200


@bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'categories': [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'expense_count': c.expenses.count()
            } for c in categories
        ]
    })


@bp.route('/export', methods=['GET'])
@login_required
def export_expenses():
    format = request.args.get('format', 'json')
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    if format == 'json':
        return jsonify({
            'expenses': [expense.to_dict() for expense in expenses],
            'total_amount': sum(e.amount for e in expenses),
            'count': len(expenses)
        })
    
    return jsonify({'error': 'Invalid format'}), 400
