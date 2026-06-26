from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
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


@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))