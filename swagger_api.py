
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Swagger UI configuration
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # Ensure this file exists in the "static" folder
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "User API Documentation"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            database="Newdb",
            user="postgres",
            password="vaishu",
            host="localhost"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {str(e)}")
        return None

# ✅ Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify(error="Username and password are required"), 400

        conn = get_db_connection()
        if not conn:
            return jsonify(error="Database connection failed"), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        return (jsonify(message="Login successful"), 200) if user else (jsonify(error="Invalid credentials"), 401)

    except Exception as e:
        return jsonify(error=f"An error occurred: {str(e)}"), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ✅ Get Users endpoint with optional query parameter "user_id"
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify(error="Database connection failed"), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        user_id = request.args.get('user_id')  # Optional query parameter

        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify(error="Invalid user_id parameter"), 400

            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify(error="User not found"), 404
            result = user
        else:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()

        return jsonify(result), 200

    except Exception as e:
        return jsonify(error=f"An error occurred: {str(e)}"), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ✅ Add a new user
@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify(error="Username and password are required"), 400

        conn = get_db_connection()
        if not conn:
            return jsonify(error="Database connection failed"), 500

        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        return jsonify(message="User added successfully"), 201

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify(error="Username already exists"), 400

    except Exception as e:
        return jsonify(error=f"An error occurred: {str(e)}"), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ✅ Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify(error="Username and password are required"), 400

        conn = get_db_connection()
        if not conn:
            return jsonify(error="Database connection failed"), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify(error="User not found"), 404

        # Update user
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE id = %s", (username, password, user_id))
        conn.commit()

        return jsonify(message="User updated successfully"), 200

    except Exception as e:
        return jsonify(error=f"An error occurred: {str(e)}"), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ✅ Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify(error="Database connection failed"), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify(error="User not found"), 404

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify(message="User deleted successfully"), 200

    except Exception as e:
        return jsonify(error=f"An error occurred: {str(e)}"), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
