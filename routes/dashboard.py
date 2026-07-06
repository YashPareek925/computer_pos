from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import mysql

dashboard = Blueprint('dashboard', __name__)

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

@dashboard.route('/dashboard')
@login_required
@admin_required
def index():
    cursor = mysql.connection.cursor()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM product")
    total_products = cursor.fetchone()[0]

    # Total Customers
    cursor.execute("SELECT COUNT(*) FROM customer")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM purchase")
    total_purchases = cursor.fetchone()[0]

    # Today's Sales Count
    cursor.execute("SELECT COUNT(*) FROM sales WHERE date = CURDATE()")
    today_sales = cursor.fetchone()[0]

    # Today's Revenue
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * sales_price), 0)
        FROM sales WHERE date = CURDATE()
    """)
    today_revenue = cursor.fetchone()[0]

    # Total Revenue Overall
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * sales_price), 0) FROM sales
    """)
    total_revenue = cursor.fetchone()[0]

    # Low Stock Products (stock < 5)
    cursor.execute("SELECT product_name, stock FROM product WHERE stock < 5")
    low_stock = cursor.fetchall()

    # Last 7 Days Sales (for chart)
    cursor.execute("""
        SELECT date, COALESCE(SUM(quantity * sales_price), 0) as revenue
        FROM sales
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY date
        ORDER BY date ASC
    """)
    weekly_sales = cursor.fetchall()

    # Recent 5 Sales
    cursor.execute("""
        SELECT s.invoice_no, s.date, p.product_name,
               c.name, s.quantity,
               (s.quantity * s.sales_price) as total
        FROM sales s
        JOIN product p ON s.product_id = p.product_id
        JOIN customer c ON s.customer_id = c.customer_id
        ORDER BY s.invoice_no DESC LIMIT 5
    """)
    recent_sales = cursor.fetchall()

    cursor.close()

    # Chart ke liye data prepare karo
    chart_labels = [str(row[0]) for row in weekly_sales]
    chart_data = [float(row[1]) for row in weekly_sales]

    return render_template('dashboard.html',
                           total_products=total_products,
                           total_customers=total_customers,
                           total_purchases=total_purchases,
                           today_sales=today_sales,
                           today_revenue=today_revenue,
                           total_revenue=total_revenue,
                           low_stock=low_stock,
                           recent_sales=recent_sales,
                           chart_labels=chart_labels,
                           chart_data=chart_data)