from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql

customers = Blueprint('customers', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# All Customers
@customers.route('/customers')
@login_required
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customer")
    all_customers = cursor.fetchall()
    cursor.close()
    return render_template('customers.html', customers=all_customers)

# Add Customer
@customers.route('/customers/add', methods=['POST'])
@login_required
def add():
    name = request.form['name']
    address = request.form['address']
    city = request.form['city']
    email = request.form['email']
    contact_no = request.form['contact_no']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO customer (name, address, city, email, contact_no) VALUES (%s, %s, %s, %s, %s)",
        (name, address, city, email, contact_no)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Customer added successfully', 'success')
    return redirect(url_for('customers.index'))

# Edit Customer - Load
@customers.route('/customers/edit/<int:id>')
@login_required
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    return render_template('edit_customer.html', customer=customer)

# Edit Customer - Save
@customers.route('/customers/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    name = request.form['name']
    address = request.form['address']
    city = request.form['city']
    email = request.form['email']
    contact_no = request.form['contact_no']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE customer SET name=%s, address=%s, city=%s, email=%s, contact_no=%s WHERE customer_id=%s",
        (name, address, city, email, contact_no, id)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Customer updated successfully', 'success')
    return redirect(url_for('customers.index'))

# Delete Customer
@customers.route('/customers/delete/<int:id>')
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    
    # Pehle check karo customer ki koi sale hai ya nahi
    cursor.execute("SELECT COUNT(*) FROM sales WHERE customer_id = %s", (id,))
    sale_count = cursor.fetchone()[0]
    
    if sale_count > 0:
        cursor.close()
        flash(f'Cannot delete — this customer has {sale_count} sale(s) on record. Delete those sales first.', 'danger')
        return redirect(url_for('customers.index'))
    
    cursor.execute("DELETE FROM customer WHERE customer_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Customer deleted successfully.', 'success')
    return redirect(url_for('customers.index'))