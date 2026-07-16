from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from extensions import get_db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username= %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect(url_for('dashboard.index'))
            else:
                return redirect(url_for('sales.index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/manage-users')
def manage_users():
    if session.get('role') != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('dashboard.index'))

    from extensions import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id, username, role FROM users")
    all_users = cursor.fetchall()
    cursor.close()
    return render_template('manage_users.html', users=all_users)

@auth.route('/manage-users/add', methods=['POST'])
def add_user():
    if session.get('role') != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('dashboard.index'))

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    from extensions import mysql
    cursor = mysql.connection.cursor()

    # Pehle check karo username already exist karta hai ya nahi
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        flash(f'Username "{username}" already exists. Please choose a different username.', 'danger')
        return redirect(url_for('auth.manage_users'))

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, hashed.decode('utf-8'), role)
    )
    mysql.connection.commit()
    cursor.close()
    flash(f'User "{username}" added successfully.', 'success')
    return redirect(url_for('auth.manage_users'))

@auth.route('/manage-users/delete/<int:id>')
def delete_user(id):
    if session.get('role') != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('dashboard.index'))

    from extensions import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('User deleted.', 'success')
    return redirect(url_for('auth.manage_users'))

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))