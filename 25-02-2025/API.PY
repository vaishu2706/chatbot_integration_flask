from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import traceback

app = Flask(__name__)
CORS(app)

# PostgreSQL Connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="chatbot_db",
            user="postgres",
            password="vaishu",
            host="localhost",
            port="5432",
            options="-c search_path=public"  # Ensure correct schema
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return str(e)

# Test if 'messages' table exists
@app.route('/test_table', methods=['GET'])
def test_table():
    try:
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("SELECT to_regclass('public.messages');")
        result = cur.fetchone()[0]

        cur.close()
        conn.close()

        if result:
            return jsonify({"success": f"Table '{result}' exists."})
        else:
            return jsonify({"error": "Table 'messages' does not exist."}), 404

    except Exception as e:
        print(f"Error checking table existence: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# CREATE - Add a new message
@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        if not data or 'user_message' not in data or 'bot_response' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (user_message, bot_response) VALUES (%s, %s) RETURNING id;",
            (data['user_message'], data['bot_response'])
        )
        message_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Message added successfully!", "id": message_id}), 201

    except Exception as e:
        print(f"Error creating message: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# READ - Get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("SELECT * FROM messages;")
        messages = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([{"id": m[0], "user_message": m[1], "bot_response": m[2]} for m in messages])

    except Exception as e:
        print(f"Error retrieving messages: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# UPDATE - Update a message
@app.route('/messages/<int:message_id>', methods=['PUT'])
def update_message(message_id):
    try:
        data = request.get_json()
        if not data or 'user_message' not in data or 'bot_response' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute(
            "UPDATE messages SET user_message = %s, bot_response = %s WHERE id = %s;",
            (data['user_message'], data['bot_response'], message_id)
        )
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Message updated successfully!"})

    except Exception as e:
        print(f"Error updating message: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# DELETE - Delete a message
@app.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE id = %s;", (message_id,))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Message deleted successfully!"})

    except Exception as e:
        print(f"Error deleting message: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
