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
def fetch_orderId():
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
cursor.execute('SELECT * FROM orders WHERE id = ?') #? cause it varies based on id
order = cursor.fetchone()
conn.close()


#Starting point

if __name__ == '__main__':
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)