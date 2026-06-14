from flask import Flask
import mysql.connector

app = Flask(__name__)

conn=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Project@123",
    database="computer_pos"
)

@app.route('/')
def home():
    return "Database Connected Successfully!"

@app.route('/products')
def products():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    return str(result)

if __name__ == "__main__":
    app.run(debug=True)
