'''
app.py - Back-End Flask, Orders Systems Production

API REST with complete CRUD, authentication via API Key, 
Global Error Handling and Input Sanitization

Author: Henrique Schorck
Date: 08/04/2026
Version: 2.0.0
SENAI Jaraguá do Sul = Technician in Cybersystems for Automation
'''


#backend flask: API REST's routes
from flask import Flask, jsonify, request
import html
from flask_cors import CORS
from functools import wraps
from database import init_db, get_connection
import datetime
from dotenv import load_dotenv 
import os

load_dotenv() #load env file

#creates an Flash's application instance 
app = Flask(__name__, static_folder='static', static_url_path='')

#Habilitate CORS
CORS(app)

#Security key
API_KEY = os.environ.get('API_KEY') 

def authentication(f):
    """
    Formatter which protects routes, requires valid API key
    Client must send header:
        X-API-Key: <API_KEY value set>
        If correct, executes route function as usual
        If incorrect or non-existing, return 401 Unauthorized
    Use:
    @app.route('/route')
    @authentication
    """
    @wraps(f) # Preserva o nome e docstring da funcao original
    def formatter(*args, **kwargs):
        # Reads X-API-Key's requisition header 
        received_key = request.headers.get('X-API-Key')
        if not received_key:
            return jsonify({'error': 'Authentication needed.','instruction': 'Send X-API-Key header with your key.'}), 401
        if received_key != API_KEY:
            return jsonify({'error': 'API Key invalid or expired.'}), 403
        # Correct key: executes route function
        return f(*args, **kwargs)
    return formatter

#route n1 - dashboard
@app.route('/')
def index():
    '''
    FEED INDEX.HTML FILE IN STATIC FOLDER
    '''
    return app.send_static_file('index.html')

#route n2 - API status
@app.route('/status')
#@authentication
def status():
    '''
    API's verification route (health). 
    Returns JSON informing server's active state
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total FROM orders')
    result = cursor.fetchone()
    return jsonify({
        "status": "online",
        "system": "Order System's Production",
        "version": "2.0.0",
        "total_orders": result["total"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Hello, factory, API working!"
    })

# route n3 - list all orders and filter (GET)
@app.route('/orders', methods=['GET'])
@authentication
def list_orders():
    '''
    List all registered production orders, with an optional status filter.
    method http: get
    URL: http://localhost:5000/orders
         http://localhost:5000/orders?status=Pending
    Returns: list and orders in JSON format
    '''
    # request.args access parameters for string query
    status_filter = request.args.get('status')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if status_filter:
        # If the user passed ?status=something, filter by it
        cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY id DESC', (status_filter,))
    else:
        # If no filter is passed, return everything
        cursor.execute('SELECT * FROM orders ORDER BY id DESC')
        
    orders = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(o) for o in orders])

#route by id (get)
@app.route('/orders/<int:order_id>', methods=['GET'])
@authentication
def fetch_orderId(order_id):
    '''
    Get an unique production order by its id
    URL parameters:
        - order id (int)
    
    returns:
        - 200 + JSON, if found
        - 404 + error message, if not found
    '''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?' , (order_id,))#? cause it varies based on id
    order = cursor.fetchone()
    conn.close()

    if order is None:
        return jsonify({'error': f'Order {order_id} not found'}), 404

    else:
        return jsonify(dict(order)), 200

# post to create a new production route
@app.route('/orders', methods=['POST'])
@authentication
def create_order():
    """
    Create a new production order on top of JSON data sent
    Expected body:
        product (str): porduct name (mandatory)
        quantity (int): amount of pieces (mandatory, > 0)
        status (str): Optional. Default: 'Pending'
    Returns:
        201 + JSON's order created, if succeeded 
        400 + error message, in case it fails
    """
    data = request.get_json()
    # ── Input validation ─────────
    # Verifeis if bidy was sent and JSON is valid 
    if not data:
        return jsonify({'error': 'Requisitions body invalid or noexistent'}), 400
    
    # Verifies obligatory field 'product'
    gross_product = data.get('product', '')
    product = html.escape(gross_product.strip())
    if not product:
        return jsonify({'error': 'Field "product" is mandatory.'}), 400
    
    #Verifies if product name is shorter than 200
    if len(product) > 200:
        return jsonify({'error': 'Product name exceeds maximum length of 200 characters.'}), 400

    # Verifies obligatory field 'quantity' 
    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'Field "quantity" is mandatory.'}), 400
    
    # Check if 'quantity' is a positive integer number
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'error': 'Field "quantity" must be a integer positive value.'}), 400
        
    # Status is optional, "Pending" is default
    valid_status = ['Pending', 'In progress', 'Done']
    status = data.get('status', 'Pending')
    if status not in valid_status:
        return jsonify({'error': f'Invalid status. Use: {valid_status}'}), 400
       
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (product, quantity, status) VALUES (?, ?,?)', (product, quantity, status))
    conn.commit()

    # Recover self-generated id
    new_id = cursor.lastrowid
    conn.close()
        
    # Search for register recently created to complete it 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (new_id,))
    new_order = cursor.fetchone()
    conn.close()
    
    # Returns 201 Created completed registered
    return jsonify(dict(new_order)), 201

# update orders' status (PUT)
@app.route('/orders/<int:order_id>', methods=['PUT'])
@authentication
def update_order(order_id):
    """
    Updates existent production order
    URL parameters:
        order_id (int)
        expected body (JSON)
        status (str): New status. Allowed: 'Pendent', 'In progress', 'Done'.
    Returns:
        200 + updated order's JSON
        400 + error if invalid
        404 + error if order not found
    """
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Requisitions body absent or invalid.'}), 400
    
    # Validates status field
    valid_status = ['Pendent', 'In progress', 'Done']
    new_status = dados.get('status', '').strip()

    if not new_status:
        return jsonify({'error': 'Field "status" is mandatory.'}), 400
    
    if new_status not in valid_status:
        return jsonify({'error': f'Invalid status. Allowed values:{valid_status}'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()

    # Checks order's veracity and tries to update it
    cursor.execute('SELECT id FROM orders WHERE id = ?', (order_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': f'Order{order_id} not found.'}),404
    
    # executes 
    cursor.execute(
    'UPDATE orders SET status = ? WHERE id = ?',(new_status, order_id))
    conn.commit()
    conn.close()

    # Returns updated register
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    updated_order = cursor.fetchone()
    conn.close()
    return jsonify(dict(updated_order)), 200

#route for deleating existent order (DELETE)
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@authentication
def remove_order(order_id):
    """
    Permanently removes a production order by id
    URL parameters:
        order_id (int)
    Returns:
        200 + confirmation message
        404 + error in case order is not found
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Verifies existent BEFORE deleting
    cursor.execute('SELECT id, product FROM orders WHERE id = ?',(order_id,))
    order = cursor.fetchone()

    if order is None:
        conn.close()
        return jsonify({'error': f'Order {order_id} not found.'}),404

    # Keeps product name, as it will be used for confirmation message
    product_name = order['product']

    # Removes   
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Order {order_id} ({product_name}) successfully removed.', 'removed_id': order_id}), 200

#running loop

if __name__ == '__main__':
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)