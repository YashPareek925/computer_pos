from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql
from datetime import date

purchases = Blueprint('purchases', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access only.', 'danger')
            return redirect(url_for('sales.index'))
        return f(*args, **kwargs)
    return decorated

# All Purchases
@purchases.route('/purchases')
@login_required
@admin_required
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.purchase_id, p.bill_no, p.date, 
               pr.product_name, s.name, 
               p.quantity, p.cost_price
        FROM purchase p
        JOIN product pr ON p.product_id = pr.product_id
        JOIN supplier s ON p.supplier_id = s.supplier_id
        ORDER BY p.date DESC
    """)
    all_purchases = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT product_id, product_name FROM product")
    all_products = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT supplier_id, name FROM supplier")
    all_suppliers = cursor.fetchall()
    cursor.close()

    return render_template('purchases.html',
                           purchases=all_purchases,
                           products=all_products,
                           suppliers=all_suppliers,
                           today=date.today())

# Add Purchase
@purchases.route('/purchases/add', methods=['POST'])
@login_required
@admin_required
def add():
    # Auto generate bill number
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM purchase")
    count = cursor.fetchone()[0]
    bill_no = f"{str(count + 1).zfill(4)}"

    purchase_date = request.form['date']
    product_id = request.form['product_id']
    supplier_id = request.form['supplier_id']
    quantity = request.form['quantity']
    cost_price = request.form['cost_price']

    cursor.execute(
        """INSERT INTO purchase
           (bill_no, date, product_id, supplier_id, quantity, cost_price)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (bill_no, purchase_date, product_id, supplier_id, quantity, cost_price)
    )
    mysql.connection.commit()
    cursor.close()
    flash(f'Purchase {bill_no} added successfully.', 'success')
    return redirect(url_for('purchases.index'))

# Delete Purchase
@purchases.route('/purchases/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    cursor = mysql.connection.cursor()

    # Pehle purchase ki details lo stock wapas karne ke liye
    cursor.execute("SELECT product_id, quantity FROM purchase WHERE purchase_id = %s", (id,))
    purchase = cursor.fetchone()

    # Stock wapas minus karo (purchase delete ki to stock bhi kam hogi)
    cursor.execute(
        "UPDATE product SET stock = stock - %s WHERE product_id = %s",
        (purchase[1], purchase[0])
    )

    # Ab purchase delete karo
    cursor.execute("DELETE FROM purchase WHERE purchase_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Purchase deleted and stock updated.', 'success')
    return redirect(url_for('purchases.index'))