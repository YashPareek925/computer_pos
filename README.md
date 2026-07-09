# Computer Shop POS System

A web-based Point of Sale and Inventory Management System built for computer shops. Features real-time stock tracking, sales management, WhatsApp-based digital billing, and a modern dark/light theme UI.

---

## Screenshots

### Login Page
https://github.com/YashPareek925/computer_pos/blob/ad425f2e381f37a84e4d11f3a0b58be8ec32d4fb/login.png

### Sales Page
https://github.com/YashPareek925/computer_pos/blob/ad425f2e381f37a84e4d11f3a0b58be8ec32d4fb/Sales.png

### Dashboard Page
https://github.com/YashPareek925/computer_pos/blob/ad425f2e381f37a84e4d11f3a0b58be8ec32d4fb/Dashboard.png

---

## Features

### Core
- Role-based authentication (Admin & Cashier)
- Product inventory with low stock alerts
- Real-time stock auto-update via MySQL triggers
- Customer auto-save on first purchase
- WhatsApp digital billing (paperless)
- Supplier and purchase tracking
- Sales dashboard with weekly revenue chart
- Profit margin tracking per product
- Auto-generated bill numbers

### UI/UX
- Dark / Light theme toggle (saved in browser)
- Collapsible left sidebar navigation
- Color-coded stat cards (Blue, Green, Orange, Purple)
- Custom delete confirmation modals
- Live search on all tables
- Circuit board background on login page
- Custom error pages (404, 403, 500)
- Responsive layout

### Security
- Passwords hashed with bcrypt
- Parameterized queries (SQL injection protection)
- Session-based authentication
- Role-based route protection (frontend + backend)
- Admin accounts permanently protected
- Duplicate username validation
- Foreign key protection on delete
- config.py excluded from version control

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Tailwind CDN, JavaScript |
| Backend | Python 3, Flask |
| Database | MySQL |
| Billing | WhatsApp (wa.me) |
| Charts | Chart.js |
| Icons | Tabler Icons |
| Auth | Flask Session + bcrypt |
| Version Control | Git + GitHub |

---

## Project Structure

```
computer_pos/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── schema.sql
├── .gitignore
├── routes/
│   ├── auth.py
│   ├── products.py
│   ├── sales.py
│   ├── purchases.py
│   ├── customers.py
│   ├── suppliers.py
│   └── dashboard.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── products.html
│   ├── edit_product.html
│   ├── sales.html
│   ├── purchases.html
│   ├── customers.html
│   ├── edit_customer.html
│   ├── suppliers.html
│   ├── edit_supplier.html
│   ├── manage_users.html
│   ├── 404.html
│   ├── 403.html
│   └── 500.html
└── static/
    └── css/
        └── style.css
```

---

## Database Schema

| Table | Description |
|---|---|
| users | Login credentials and roles |
| product | Inventory with cost and sales price |
| customer | Customer details with WhatsApp number |
| supplier | Supplier information |
| purchase | Stock purchase records |
| sales | Sales transaction records |

### MySQL Triggers

| Trigger | Action |
|---|---|
| after_sale_insert | Automatically deducts stock when a sale is recorded |
| after_purchase_insert | Automatically adds stock when a purchase is recorded |

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/computer_pos.git
cd computer_pos
```

### 2. Install dependencies
```bash
pip install flask flask-mysqldb bcrypt fpdf2
```

### 3. Setup MySQL database
- Create database `computer_pos` in MySQL Workbench
- Run `schema.sql` to create all tables and triggers

### 4. Configure credentials
Create `config.py` in root folder:
```python
class Config:
    SECRET_KEY = 'your_secret_key_here'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'your_mysql_password'
    MYSQL_DB = 'computer_pos'
```

### 5. Create admin user
Run this in terminal once:
```python
import bcrypt
hashed = bcrypt.hashpw("your_password".encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```
Then in MySQL Workbench:
```sql
INSERT INTO users (username, password, role)
VALUES ('admin', 'PASTE_HASH_HERE', 'admin');
```

### 6. Run the application
```bash
python app.py
```

### 7. Open in browser
http://127.0.0.1:5000

---

## Role Access

| Feature | Admin | Cashier |
|---|---|---|
| Dashboard | ✓ | ✗ |
| Products | ✓ | ✗ |
| Sales | ✓ | ✓ |
| Purchases | ✓ | ✗ |
| Customers | ✓ | ✓ |
| Suppliers | ✓ | ✗ |
| Manage Users | ✓ | ✗ |

---

## WhatsApp Billing

After each sale, a pre-filled WhatsApp message is generated with:
- Invoice number
- Date
- Product name
- Quantity
- Price
- Total amount

The cashier clicks "Bill" and WhatsApp opens with the message ready to send to the customer's number.

---

## Future Scope

- Barcode scanner integration
- GST report generation
- Mobile application
- Multi-branch inventory sync
- Online payment gateway
- Email invoice support
- Sales analytics and forecasting

---

## Developer

**Yash Pareek**      
BCA Final Year      
Shri Jain College      
GitHub: https://github.com/YashPareek925

---

## License

This project is open source and available under the [MIT License](LICENSE).
