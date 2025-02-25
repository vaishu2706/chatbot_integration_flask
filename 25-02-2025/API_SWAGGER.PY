
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import psycopg2

# Initialize Flask app and Swagger API
app = Flask(__name__)
CORS(app)
api = Api(app, version='1.0', title='Chatbot API', description='API for Message CRUD Operations')

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="chatbot_db",
            user="postgres",
            password="vaishu",
            host="localhost",
            port="5432",
            options="-c search_path=public"
        )
        return conn
    except Exception as e:
        return str(e)

# Swagger Model for input data
message_model = api.model('Message', {
    'user_message': fields.String(required=True, description='User message'),
    'bot_response': fields.String(required=True, description='Bot response')
})

# Swagger Namespace
ns = api.namespace('messages', description='Message Operations')

# Health Check
@app.route('/')
def home():
    return jsonify({"message": "Chatbot API is running!"})

# 1. CREATE: Add a new message
@ns.route('/')
class MessageList(Resource):
    @ns.expect(message_model)
    def post(self):
        """Create a new message."""
        try:
            data = request.get_json()
            conn = get_db_connection()
            if isinstance(conn, str):
                return {"error": conn}, 500

            cur = conn.cursor()
            cur.execute("INSERT INTO messages (user_message, bot_response) VALUES (%s, %s)",
                        (data['user_message'], data['bot_response']))
            conn.commit()
            cur.close()
            conn.close()
            return {"message": "Message added successfully!"}, 201
        except Exception as e:
            return {"error": str(e)}, 500

    def get(self):
        """Get all messages."""
        try:
            conn = get_db_connection()
            if isinstance(conn, str):
                return {"error": conn}, 500

            cur = conn.cursor()
            cur.execute("SELECT * FROM messages")
            messages = cur.fetchall()
            cur.close()
            conn.close()

            return [{"id": m[0], "user_message": m[1], "bot_response": m[2]} for m in messages]
        except Exception as e:
            return {"error": str(e)}, 500

# 2. UPDATE: Update a message by ID
@ns.route('/<int:message_id>')
class Message(Resource):
    @ns.expect(message_model)
    def put(self, message_id):
        """Update an existing message by ID."""
        try:
            data = request.get_json()
            conn = get_db_connection()
            if isinstance(conn, str):
                return {"error": conn}, 500

            cur = conn.cursor()
            cur.execute("UPDATE messages SET user_message = %s, bot_response = %s WHERE id = %s",
                        (data['user_message'], data['bot_response'], message_id))
            conn.commit()
            cur.close()
            conn.close()
            return {"message": "Message updated successfully!"}
        except Exception as e:
            return {"error": str(e)}, 500

    def delete(self, message_id):
        """Delete a message by ID."""
        try:
            conn = get_db_connection()
            if isinstance(conn, str):
                return {"error": conn}, 500

            cur = conn.cursor()
            cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
            conn.commit()
            cur.close()
            conn.close()
            return {"message": "Message deleted successfully!"}
        except Exception as e:
            return {"error": str(e)}, 500

# 3. Check Table Existence
@app.route('/test_table')
def test_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages LIMIT 1;")
        cur.close()
        conn.close()
        return jsonify({"success": "Table 'messages' exists."})
    except Exception as e:
        return jsonify({"error": str(e)})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
