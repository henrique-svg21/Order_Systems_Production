#backend flask: API REST's routes
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_connection

#creates an Flash's application instance 
app = Flask(__name__, static_folder='static', static_url_path='')

#Habilitate CORS
CORS(app)

#route n1 - dashboard
@app.route('/')
def index():
    '''
    FEED INDEX.HTML FILE IN STATIC FOLDER
    '''
    return app.send_static_file('index.html')

#route n2 - API status
@app.route('/status')
def status():
    '''
    API's verification route (health). 
    Returns JSON informing server's active state
    '''
    return jsonify({
        "status": "online",
        "system": "Order System's Production",
        "version": "1.0.0",
        "message": "Hello, factory, API working!"
    })

#route n3 - list all orders (get)
@app.route('/orders', methods=['GET'])
def list_orders():
    '''
    list all registered production orders
    method http: get
    URL: https://localhost:5000/orders
    Returns: list and orders in JSON format
    '''
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(o) for o in orders])

#route by id (get)
@app.route('/orders/<int:order_id>', methods=['GET'])
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
    product = data.get('product', '').strip()
    if not product:
        return jsonify({'error': 'Field "product" is mandatory.'}), 400
    
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


#running loop

if __name__ == '__main__':
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    