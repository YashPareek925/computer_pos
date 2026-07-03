from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql
from datetime import date

sales = Blueprint('sales', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# All Sales
@sales.route('/sales')
@login_required
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT s.invoice_no, s.date,
               p.product_name, c.name,
               s.quantity, s.sales_price,
               (s.quantity * s.sales_price) as total,
               c.contact_no
        FROM sales s
        JOIN product p ON s.product_id = p.product_id
        JOIN customer c ON s.customer_id = c.customer_id
        ORDER BY s.date DESC
    """)
    all_sales = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT product_id, product_name, stock, sales_price FROM product")
    all_products = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT customer_id, name, contact_no FROM customer")
    all_customers = cursor.fetchall()
    cursor.close()

    return render_template('sales.html',
                           sales=all_sales,
                           products=all_products,
                           customers=all_customers,
                           today=date.today())

# Add Sale
@sales.route('/sales/add', methods=['POST'])
@login_required
def add():
    # Date validation - past date check
    from datetime import datetime
    sale_date = request.form['date']
    if sale_date < str(date.today()):
        flash('Past date sales not allowed.', 'danger')
        return redirect(url_for('sales.index'))

    # Contact number validation
    contact_no = request.form['contact_no'].strip()
    if not contact_no.isdigit() or len(contact_no) != 10:
        flash('Invalid WhatsApp number. Enter 10 digits only.', 'danger')
        return redirect(url_for('sales.index'))
    
    sale_date = request.form['date']
    product_id = request.form['product_id']
    customer_name = request.form['customer_name'].strip()
    contact_no = request.form['contact_no'].strip()
    quantity = int(request.form['quantity'])
    sales_price = request.form['sales_price']

    # Stock check karo pehle
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT stock, product_name FROM product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()

    if product[0] < quantity:
        flash(f'Insufficient stock. Available: {product[0]} units only.', 'danger')
        cursor.close()
        return redirect(url_for('sales.index'))

    # Customer exist karta hai ya nahi check karo
    cursor.execute("SELECT customer_id FROM customer WHERE name = %s AND contact_no = %s",
                   (customer_name, contact_no))
    existing_customer = cursor.fetchone()

    if existing_customer:
        customer_id = existing_customer[0]
    else:
        # New customer save karo
        cursor.execute(
            "INSERT INTO customer (name, contact_no) VALUES (%s, %s)",
            (customer_name, contact_no)
        )
        mysql.connection.commit()
        customer_id = cursor.lastrowid

    # Sale insert karo
    cursor.execute(
        """INSERT INTO sales (date, product_id, customer_id, quantity, sales_price)
           VALUES (%s, %s, %s, %s, %s)""",
        (sale_date, product_id, customer_id, quantity, sales_price)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Sale recorded successfully.', 'success')
    return redirect(url_for('sales.index'))

# Delete Sale
@sales.route('/sales/delete/<int:id>')
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    # Pehle sale details lo stock wapas karne ke liye
    cursor.execute("SELECT product_id, quantity FROM sales WHERE invoice_no = %s", (id,))
    sale = cursor.fetchone()

    # Stock wapas add karo
    cursor.execute(
        "UPDATE product SET stock = stock + %s WHERE product_id = %s",
        (sale[1], sale[0])
    )

    # Sale delete karo
    cursor.execute("DELETE FROM sales WHERE invoice_no = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Sale deleted and stock reversed.', 'success')
    return redirect(url_for('sales.index'))

# Customer search for autocomplete
@sales.route('/sales/search-customer')
@login_required
def search_customer():
    from flask import jsonify
    query = request.args.get('q', '')
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT name, contact_no FROM customer WHERE name LIKE %s LIMIT 5",
        ('%' + query + '%',)
    )
    results = cursor.fetchall()
    cursor.close()
    customers = [{'name': r[0], 'contact_no': r[1]} for r in results]
    return jsonify(customers)