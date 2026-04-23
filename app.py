from flask import Flask, render_template, request, url_for, make_response, flash, redirect, Response, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, date as dt_date
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-secret-key'

db = SQLAlchemy(app)



class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String(200), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

CATEGORIES = ['Food', 'Transport', 'Rent', 'Utilities', 'Health', 'Other']

def parse_date_ornone(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError:
        return None

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        else:
            flash('Please enter username and password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if username and password and confirm:
            if password != confirm:
                flash('Passwords do not match.', 'error')
            elif User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
            else:
                user = User(username=username, password_hash=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
        else:
            flash('Please fill all fields.', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@login_required
@app.route('/')
def index():

    start_str = (request.args.get('start') or '').strip()
    end_str = (request.args.get('end') or '').strip()
    selected_category = (request.args.get('category') or '').strip()

    start_date = parse_date_ornone(start_str)
    end_date = parse_date_ornone(end_str)

    if start_date and end_date and end_date < start_date:
        flash("End date cannot be before start date", "error")
        start_date = end_date = None
        start_str = end_str = ''

    q=Expense.query
    if start_date:
        q = q.filter(Expense.date >= start_date)

    if end_date:
        q = q.filter(Expense.date <= end_date)

    if selected_category:
        q = q.filter(Expense.category == selected_category)

    expenses = q.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)

#piechart data
    cat_q = db.session.query(Expense.category, func.sum(Expense.amount))

    if start_date:
        cat_q = cat_q.filter(Expense.date >= start_date)

    if end_date:
        cat_q = cat_q.filter(Expense.date <= end_date)

    if selected_category:
        cat_q = cat_q.filter(Expense.category == selected_category)

    cat_row = cat_q.group_by(Expense.category).all()
    cat_labels = [c for c, _ in cat_row]
    cat_values = [round(float(s or 0),2) for _, s in cat_row]

    #daychart data

    day_q = db.session.query(Expense.date, func.sum(Expense.amount))

    if start_date:
        day_q = day_q.filter(Expense.date >= start_date)

    if end_date:
        day_q = day_q.filter(Expense.date <= end_date)

    if selected_category:
        day_q = day_q.filter(Expense.category == selected_category)

    day_row = day_q.group_by(Expense.date).order_by(Expense.date).all()
    day_labels = [d.isoformat() for d, _ in day_row]
    day_values = [round(float(s or 0),2) for _, s in day_row]


    return render_template(

        "index.html", 
        
        categories=CATEGORIES,
        today=date.today().isoformat(),
        expenses=expenses,
        total=total,
        start_str=start_str,
        end_str=end_str,
        selected_category=selected_category,
        cat_labels=cat_labels,
        cat_values=cat_values,
        day_labels=day_labels,
        day_values=day_values
        
        )





@login_required
@app.route('/add', methods=['POST'])
def add():

    description = (request.form.get('description') or '').strip()
    amount_str = (request.form.get('amount') or '').strip()
    category = (request.form.get('category') or '').strip()
    date_str = (request.form.get('date') or '').strip()

    if not description or not amount_str or not category:
        flash("Missing required fields", 'error')
        return redirect(url_for('index'))
    

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number", 'error')
        return redirect(url_for('index'))
    
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        d = date.today()


    e = Expense(description=description, amount=amount, category=category, date=d)
    db.session.add(e)
    db.session.commit()

    flash("Expense added", "success")
    return redirect(url_for('index'))



@login_required
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    e = Expense.query.get_or_404(expense_id)
    db.session.delete(e)
    db.session.commit()
    flash("Expense deleted", "success")
    return redirect(url_for('index'))



@login_required
@app.route('/edit/<int:expense_id>', methods=['GET'])
def edit(expense_id):
    e = Expense.query.get_or_404(expense_id)
    return render_template("edit.html", expense=e, categories=CATEGORIES, today=dt_date.today().isoformat())



@login_required
@app.route('/edit/<int:expense_id>', methods=['POST'])
def edit_post(expense_id):
    e = Expense.query.get_or_404(expense_id)

    description = (request.form.get('description') or '').strip()
    amount_str = (request.form.get('amount') or '').strip()
    category = (request.form.get('category') or '').strip()
    date_str = (request.form.get('date') or '').strip()

    if not description or not amount_str or not category:
        flash("Missing required fields", 'error')
        return redirect(url_for('edit', expense_id=expense_id))
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number", 'error')
        return redirect(url_for('edit', expense_id=expense_id))
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else dt_date.today()
    except ValueError:
        d = dt_date.today()

    e.description = description
    e.amount = amount
    e.category = category
    e.date = d

    db.session.commit()
    flash("Expense updated", "success")
    return redirect(url_for('index'))
    


@login_required
@app.route("/export.csv")
def export_csv():

    start_str = (request.args.get('start') or '').strip()
    end_str = (request.args.get('end') or '').strip()
    selected_category = (request.args.get('category') or '').strip()

    start_date = parse_date_ornone(start_str)
    end_date = parse_date_ornone(end_str)

    q=Expense.query
    if start_date:
        q = q.filter(Expense.date >= start_date)    
    if end_date:
        q = q.filter(Expense.date <= end_date)
    if selected_category:
        q = q.filter(Expense.category == selected_category)

    expenses = q.order_by(Expense.date, Expense.id).all()

    lines = ["date, category, description, amount"]

    for e in expenses:
        lines.append(f"{e.date.isoformat()}, {e.category}, {e.description}, {e.amount:.2f}")
    csv_data = "\n".join(lines)

    fname_start = start_str or "all"
    fname_end = end_str or "all"
    filename = f"expenses_{fname_start}_to_{fname_end}.csv"

    return Response(
        csv_data,
        headers={
            "Content-Type": "text/csv",
            "Content-disposition": f"attachment; filename={filename}"
            }
    )




    print("Form received:", dict(request.form))
    return make_response("Form received")

if __name__ == '__main__':
    app.run(debug=True, port=4848)
