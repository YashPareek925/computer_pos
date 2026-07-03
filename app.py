from flask import Flask, redirect, url_for
from config import Config
from extensions import mysql
from routes.customers import customers
from routes.suppliers import suppliers
from routes.purchases import purchases
from routes.sales import sales
from routes.dashboard import dashboard


app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)

from routes.auth import auth
from routes.products import products

app.register_blueprint(auth)  
app.register_blueprint(products)
app.register_blueprint(customers)
app.register_blueprint(suppliers)
app.register_blueprint(purchases)
app.register_blueprint(sales)
app.register_blueprint(dashboard)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)