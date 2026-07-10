import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import africastalking

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend to connect
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ================== UPDATE THESE 3 VALUES ==================
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")  # 1. Your Africa's Talking username
AT_API_KEY = os.getenv("AT_API_KEY", "xxx")        # 2. Your API key from dashboard
MY_254_NUMBER = "+254712345678"                    # 3. Your purchased +254 number
# ===========================================================

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

# Use a real DB in production. This is just for demo
messages_db = []

@app.route("/")
def health():
    return jsonify({"status": "running", "number": MY_254_NUMBER})

@app.route("/get-number", methods=["POST"])
def get_number():
    # In a real app you'd assign from a pool per user
    # For demo we just return your one number
    return jsonify({"phone_number": MY_254_NUMBER})

@app.route("/webhook/sms", methods=["POST"])
def at_webhook():
    # Africa's Talking sends this when SMS arrives
    from_number = request.form.get("from")
    to_number = request.form.get("to")
    text = request.form.get("text")
    message_id = request.form.get("id", str(len(messages_db)))
    
    msg = {
        "id": message_id,
        "from": from_number,
        "to": to_number,
        "body": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    messages_db.append(msg)
    print(f"New SMS: {msg}")
    
    # Push to all connected browsers instantly
    socketio.emit('new_sms', msg, broadcast=True)
    return "OK", 200

@app.route("/messages", methods=["GET"])
def get_messages():
    to_number = request.args.get("to")
    if to_number:
        user_msgs = [m for m in messages_db if m["to"] == to_number]
    else:
        user_msgs = messages_db
    return jsonify({"messages": user_msgs})

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)
