# app.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import date

app = Flask(__name__)
CORS(app)

# 配置SQLite数据库
DATABASE = 'order_system.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            unit_price REAL NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
		    name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
		    price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id)
    );
    ''')
    conn.commit()
    conn.close()

# 初始化数据库表格
create_table()

# 获取商品列表的API
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price, unit_price, image FROM products')
    products = cursor.fetchall()
    conn.close()

    products_with_image = []
    for product in products:
        product_dict = {
            'id': product[0],
            'name': product[1],
            'price': product[2],
            'unit_price': product[3],
            'image': product[4]
        }
        products_with_image.append(product_dict)

    return jsonify(products_with_image)

# 添加订单的API
@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    user_name = data['user']
    items = data['items']
    print("xxxxxxxxxxxxxxxxxxxxxxxxxx",items)
    # 将订单信息存储到数据库中
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # 注意这里根据具体数据结构进行调整插入逻辑
    for item in items:
        cursor.execute('''
            INSERT INTO orders (user_name, name, product_id, price, quantity, order_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_name,item['name'], item['id'], item['price'], item['quantity'], date.today().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()

    return jsonify({'message': '下单成功'})

# 获取今日订单
@app.route('/api/orders', methods=['GET'])
def get_orders():
    today = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.user_name, p.name, p.price
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.order_date = ?
    ''', (today,))
    today_orders = cursor.fetchall()
    conn.close()

    orders_by_user = {}
    total_price = 0

    for order in today_orders:
        user_name = order[0]
        product_name = order[1]
        product_price = order[2]

        if user_name not in orders_by_user:
            orders_by_user[user_name] = {'products': [], 'total_price': 0}

        orders_by_user[user_name]['products'].append({'name': product_name, 'price': product_price})
        orders_by_user[user_name]['total_price'] += product_price
        total_price += product_price

    result = {'orders_by_user': orders_by_user, 'total_price': total_price}
    return result


# 启动Flask应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

