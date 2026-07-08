from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql

suppliers = Blueprint('suppliers', __name__)

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

# All Suppliers
@suppliers.route('/suppliers')
@login_required
@admin_required
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM supplier")
    all_suppliers = cursor.fetchall()
    cursor.close()
    return render_template('suppliers.html', suppliers=all_suppliers)

# Add Supplier
@suppliers.route('/suppliers/add', methods=['POST'])
@login_required
@admin_required
def add():
    name = request.form['name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    address = request.form['address']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO supplier (name, contact_no, email, address) VALUES (%s, %s, %s, %s)",
        (name, contact_no, email, address)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Supplier added successfully', 'success')
    return redirect(url_for('suppliers.index'))

# Edit Supplier - Load
@suppliers.route('/suppliers/edit/<int:id>')
@login_required
@admin_required
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM supplier WHERE supplier_id = %s", (id,))
    supplier = cursor.fetchone()
    cursor.close()
    return render_template('edit_supplier.html', supplier=supplier)

# Edit Supplier - Save
@suppliers.route('/suppliers/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update(id):
    name = request.form['name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    address = request.form['address']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE supplier SET name=%s, contact_no=%s, email=%s, address=%s WHERE supplier_id=%s",
        (name, contact_no, email, address, id)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Supplier updated successfully', 'success')
    return redirect(url_for('suppliers.index'))

# Delete Supplier
@suppliers.route('/suppliers/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    cursor = mysql.connection.cursor()

    # Check karo supplier ki koi purchase hai ya nahi
    cursor.execute("SELECT COUNT(*) FROM purchase WHERE supplier_id = %s", (id,))
    purchase_count = cursor.fetchone()[0]

    if purchase_count > 0:
        cursor.close()
        flash(f'Cannot delete — this supplier has {purchase_count} purchase(s) on record. Delete those purchases first.', 'danger')
        return redirect(url_for('suppliers.index'))

    cursor.execute("DELETE FROM supplier WHERE supplier_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Supplier deleted successfully.', 'success')
    return redirect(url_for('suppliers.index'))