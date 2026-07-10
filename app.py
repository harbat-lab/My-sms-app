import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import africastalking

load_dotenv()
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY = os.getenv("AT_API_KEY")
MY_254_NUMBER = os.getenv("MY_254_NUMBER")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
messages_db = []

@app.route("/")
def health():
    return jsonify({"status": "running"})

@app.route("/get-number", methods=["POST"])
def get_number():
    return jsonify({"phone_number": MY_254_NUMBER})

@app.route("/webhook/sms", methods=["POST"])
def at_webhook():
    msg = {
        "id": request.form.get("id", str(len(messages_db))),
        "from": request.form.get("from"),
        "to": request.form.get("to"),
        "body": request.form.get("text"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages_db.append(msg)
    socketio.emit('new_sms', msg, broadcast=True)
    return "OK", 200

@app.route("/messages", methods=["GET"])
def get_messages():
    to_number = request.args.get("to")
    user_msgs = [m for m in messages_db if m["to"] == to_number]
    return jsonify({"messages": user_msgs})

if __name__ == "__main__":
    socketio.run(app, port=5000)
