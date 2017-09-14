import uuid
import yaml
import datetime
from flask import Flask, flash, request, render_template, redirect, url_for
app = Flask(__name__)
app.secret_key = 'life is pointless'

with open('products.yml') as _f:
    PRODUCTS = yaml.load(_f)

with open('denominations.yml') as _f:
    DENOMINATIONS = yaml.load(_f)


ORDER_DB = 'orders.yml'


def record_order(product_id):
    order_id = str(uuid.uuid4()).split('-', 1)[0]
    orders = {
        order_id: {
            'product_id': product_id,
        }
    }
    with open(ORDER_DB, 'a') as f:
        f.write(yaml.dump(orders, default_flow_style=False))
    return order_id


@app.route('/', methods=['POST', 'GET'])
def index():
    context = {}
    if request.method == 'POST':
        product_number = int(request.form['product'])
        amount_paid = float(request.form['paid'])
        if product_number > 3:
            flash('Please choose a product', 'danger')
        elif amount_paid < PRODUCTS[product_number]['price']:
            flash('Please pay more money', 'danger')
        else:
            flash('Order Placed Successfully', 'success')
            order_info = {
                "amount_paid": amount_paid,
                "amount_bought": PRODUCTS[product_number]['price'],
                "buyer": request.form['buyer'],
                "created": datetime.datetime.now().strftime('%Y-%m-%d')
            }
            order_id = record_order(order_info)
            return redirect(url_for('confirmation', order_id=order_id))
    return render_template(
        'index.jinja',
        products=PRODUCTS,
        title='Order Form',
        **context)


@app.route('/confirmation/<order_id>')
def confirmation(order_id):
    with open(ORDER_DB) as f:
        orders = yaml.load(f) or {}

    order = orders.get(order_id)
    if order is None:
        return redirect(url_for('index'))
    amount_paid = order['product_id']['amount_paid']
    item_price = order['product_id']['amount_bought']
    change_due = round(amount_paid - item_price, 2)
    change_left = change_due * 100
    denominations = []
    for item in DENOMINATIONS:
        numberOfDenominations = int(change_left/item['value'])
        denominations.append({'name': item['name'], 'count': numberOfDenominations})
        change_left -= item['value'] * numberOfDenominations
    return render_template(
        'confirmation.jinja',
        order_id=order_id,
        title='Order Confirmation',
        amount_paid=amount_paid,
        item_price=item_price,
        change_due=change_due,
        denominations=denominations)


@app.route('/orders')
def orders():
    with open(ORDER_DB) as f:
        orders_list = yaml.load(f)
    order_info = []
    for order_id, order in orders_list.items():
        order_info.append({'order_id': order_id,
                           'created': order['product_id']['created'],
                           'buyer': order['product_id']['buyer'],
                           'amount_bought': order['product_id']['amount_bought']})
    return render_template(
        'orders.jinja',
        orders=order_info,
        title='Order List')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
