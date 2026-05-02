from flask import Flask, render_template_string, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_FILE = 'products.json'
ADMIN_PASSWORD = '123456'

# Load products from file
def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Save products to file
def save_products(products):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

# HTML template (store front + admin panel)
TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فروشگاه لباس</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tahoma', 'Arial', sans-serif;
        }
        body {
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .product {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s;
        }
        .product:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .product img {
            max-width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
        }
        .product h3 {
            margin: 10px 0;
            color: #333;
        }
        .product .price {
            color: #e91e63;
            font-size: 1.2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .product .desc {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .btn {
            display: inline-block;
            background: #e91e63;
            color: white;
            padding: 8px 20px;
            text-decoration: none;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover {
            background: #c2185b;
        }
        .admin-link {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 10px 15px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 14px;
        }
        .admin-panel {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .admin-panel input, .admin-panel textarea {
            width: 100%;
            padding: 8px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .admin-panel textarea {
            height: 80px;
        }
        .product-item {
            background: white;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .delete-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .login-form {
            max-width: 300px;
            margin: 50px auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .login-form input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .message {
            background: #4caf50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if not session.logged_in %}
            <div class="login-form">
                <h2>ورود به پنل مدیریت</h2>
                <form method="post" action="{{ url_for('login') }}">
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <button type="submit" class="btn">ورود</button>
                </form>
                {% with messages = get_flashed_messages() %}
                    {% if messages %}
                        <div class="message">{{ messages[0] }}</div>
                    {% endif %}
                {% endwith %}
            </div>
        {% else %}
            <div class="admin-panel">
                <h2>پنل管理 - افزودن محصول جدید</h2>
                <form method="post" action="{{ url_for('add_product') }}">
                    <input type="text" name="name" placeholder="نام محصول" required>
                    <input type="text" name="price" placeholder="قیمت (تومان)" required>
                    <input type="text" name="image" placeholder="آدرس تصویر (URL)" required>
                    <textarea name="description" placeholder="توضیحات محصول"></textarea>
                    <button type="submit" class="btn">افزودن محصول</button>
                </form>
                
                <h2>محصولات موجود</h2>
                {% for product in products %}
                    <div class="product-item">
                        <div>
                            <strong>{{ product.name }}</strong> - {{ product.price }} تومان<br>
                            <small>{{ product.description[:50] }}</small>
                        </div>
                        <a href="{{ url_for('delete_product', index=loop.index0) }}" class="delete-btn" onclick="return confirm('حذف شود؟')">حذف</a>
                    </div>
                {% endfor %}
                <p><a href="{{ url_for('logout') }}" class="btn" style="background:#666;">خروج از پنل</a></p>
            </div>
        {% endif %}
        
        <h1>🛍️ فروشگاه لباس</h1>
        <div class="products">
            {% for product in products %}
                <div class="product">
                    <img src="{{ product.image }}" alt="{{ product.name }}" onerror="this.src='https://via.placeholder.com/200'">
                    <h3>{{ product.name }}</h3>
                    <div class="price">{{ product.price }} تومان</div>
                    <div class="desc">{{ product.description }}</div>
                    <button class="btn">خرید</button>
                </div>
            {% endfor %}
        </div>
    </div>
    <a href="{{ url_for('admin') }}" class="admin-link">🔐 پنل مدیریت</a>
</body>
</html>
'''

@app.route('/')
def index():
    products = load_products()
    return render_template_string(TEMPLATE, products=products, session=session)

@app.route('/admin')
def admin():
    products = load_products()
    return render_template_string(TEMPLATE, products=products, session=session)

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password == ADMIN_PASSWORD:
        session['logged_in'] = True
    else:
        from flask import flash
        flash('رمز عبور اشتباه است')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/add-product', methods=['POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    products = load_products()
    new_product = {
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'image': request.form.get('image'),
        'description': request.form.get('description', '')
    }
    products.append(new_product)
    save_products(products)
    return redirect(url_for('admin'))

@app.route('/delete-product/<int:index>')
def delete_product(index):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    products = load_products()
    if 0 <= index < len(products):
        products.pop(index)
        save_products(products)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        sample_products = [
            {"name": "تیشرکت مردانه", "price": "250,000", "image": "https://via.placeholder.com/200?text=T-Shirt", "description": "تیشرکت نخی با کیفیت عالی"},
            {"name": "شلوار جین", "price": "850,000", "image": "https://via.placeholder.com/200?text=Jeans", "description": "شلوار جین کلاسیک آبی"}
        ]
        save_products(sample_products)
    
    app.run(debug=True)
