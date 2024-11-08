from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import bcrypt

app = Flask(__name__)
CORS(app)

# MySQL connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      # Change to your MySQL host if necessary
        user="root",           # MySQL user (default is 'root' for localhost)
        password="",           # MySQL password (leave blank if none)
        database="ma"          # The name of your database ('ma' in this case)
    )

# Root route
@app.get('/')
def home():
    return jsonify({"message": "Welcome to the API"})

# Route to get all products
@app.get('/products/')
def getProducts():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM product')
        data = cursor.fetchall()
        product_list = []
        for item in data:
            product_list.append(
                {
                    "id": item[0],
                    "title": item[2],
                    "price": item[4],
                    "description": item[6],
                    "category": item[3],
                    "image": item[5],
                    "rating": {
                        "rate": 3.9,  # Placeholder, you can replace with actual rating logic
                        "count": 120  # Placeholder for rating count
                    }
                }
            )
        return jsonify(product_list)
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Route to get a single product by its ID
@app.get('/products/<int:product_id>')
def getProduct(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM product WHERE id = %s', (product_id,))
        data = cursor.fetchone()
        if data:
            product = {
                "id": data[0],
                "title": data[2],
                "price": data[4],
                "description": data[6],
                "category": data[3],
                "image": data[5],
                "rating": {
                    "rate": 3.9,  # Placeholder
                    "count": 120  # Placeholder
                }
            }
            return jsonify(product)
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Create a new product (Create)
@app.post('/products')
def create_product():
    data = request.get_json()
    
    # Validation for required fields
    required_fields = ['title', 'category', 'price', 'image', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO product (title, category, price, image_url, description) VALUES (%s, %s, %s, %s, %s)',
            (data['title'], data['category'], data['price'], data['image'], data['description'])
        )
        conn.commit()
        
        # Get the last inserted id for the response
        product_id = cursor.lastrowid
        return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Delete a product (Delete)
@app.delete('/products/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM product WHERE id = %s', (id,))
        conn.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Update an existing product (Update)
@app.put('/products/<int:product_id>')
def update_product(product_id):
    data = request.get_json()
    
    # Validation for required fields
    required_fields = ['title', 'category', 'price', 'image', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            UPDATE product
            SET title = %s, category = %s, price = %s, image_url = %s, description = %s
            WHERE id = %s
            ''',
            (data['title'], data['category'], data['price'], data['image'], data['description'], product_id)
        )
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
        
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Route to get user details by their ID
@app.get('/users/<int:user_id>')
def getUser(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        data = cursor.fetchone()
        if data:
            user = {
                "id": data[0],
                "name": data[1],
                "email": data[2],
                # Do not return password for security reasons
                "imgURL": data[4],
            }
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.get('/users')
def getUsers():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users')
        data = cursor.fetchall()
        users_list = []
        for item in data:
            users_list.append({
                "id": item[0],
                "name": item[1],
                "email": item[2],
                # Do not return password for security reasons
                "imgURL": item[4],
            })
        return jsonify(users_list)
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# New login route
@app.post('/login')
def login():
    # Get the data from the request
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    # Query the database to check for a matching user
    query = "SELECT * FROM users WHERE name = %s"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (name,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):  # Assuming the password is in user[3]
            user_data = {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "imgURL": user[4],
            }
            return jsonify({"message": "Login successful", "user": user_data}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "Database error", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
