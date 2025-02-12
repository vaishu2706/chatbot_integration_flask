
from flask import Flask,request,jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
app=Flask(__name__)
def get_db_connection():
    conn=psycopg2.connect(
        database="Newdb",
        user="postgres",
        password="vaishu",
        host="localhost"
    )
    return conn

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify(error="Username and password are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return jsonify(message="Login successful")
    else:
        return jsonify(error="Invalid credentials"), 401

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify(error="Username and password are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()  
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify(error="Username already exists"), 400
    finally:
        cursor.close()
        conn.close()
    
    return jsonify(message="User added successfully"), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify(error="Username and password are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = %s, password = %s WHERE id = %s", (username, password, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(message="User updated successfully")

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(message="User deleted successfully")

if __name__ == '__main__':
    app.run(debug=True)