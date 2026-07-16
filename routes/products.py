from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import get_db

products = Blueprint('products', __name__)

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

@products.route('/products')
@login_required
@admin_required
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM product")
    all_products = cursor.fetchall()
    cursor.close()
    return render_template('products.html', products=all_products)

@products.route('/products/add', methods=['POST'])
@login_required
@admin_required
def add():
    name = request.form['product_name']
    stock = request.form['stock']
    cost_price = request.form['cost_price']
    sales_price = request.form['sales_price']
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO product (product_name, stock, cost_price, sales_price) VALUES (%s, %s, %s, %s)",
        (name, stock, cost_price, sales_price)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Product added successfully', 'success')
    return redirect(url_for('products.index'))

@products.route('/products/edit/<int:id>')
@login_required
@admin_required
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM product WHERE product_id = %s", (id,))
    product = cursor.fetchone()
    cursor.close()
    return render_template('edit_product.html', product=product)

@products.route('/products/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update(id):
    name = request.form['product_name']
    stock = request.form['stock']
    cost_price = request.form['cost_price']
    sales_price = request.form['sales_price']
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE product SET product_name=%s, stock=%s, cost_price=%s, sales_price=%s WHERE product_id=%s",
        (name, stock, cost_price, sales_price, id)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Product updated successfully', 'success')
    return redirect(url_for('products.index'))

@products.route('/products/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM product WHERE product_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('products.index'))

@products.route('/products/search')
@login_required
@admin_required
def search():
    query = request.args.get('q', '')
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM product WHERE product_name LIKE %s",
        ('%' + query + '%',)
    )
    results = cursor.fetchall()
    cursor.close()
    return render_template('products.html', products=results, search=query)