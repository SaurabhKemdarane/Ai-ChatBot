import os
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import google.generativeai as genai

# Set the Google application credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/visual studio codes/projects/AI-chatBOT-SYSTEM/cred.json"

app = Flask(__name__)
app.secret_key = "AIzaSyCIuhB3RwDHTrManJe8obyvPrYqbHAxFjg"

# MongoDB connection
app.config["MONGO_URI"] = "mongodb+srv://gg:12345@chatbot.s4lnzhi.mongodb.net/chatbot?connectTimeoutMS=30000&socketTimeoutMS=30000"
mongo = PyMongo(app)

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config)

# Function to get user's chat history
def get_user_history(email):
    return list(mongo.db.chats.find({"email": email}))

# Function to insert chat history for a user
def insert_user_history(email, question, answer):
    mongo.db.chats.insert_one({
        "email": email,
        "timestamp": datetime.now(),
        "question": question,
        "answer": answer
    })

# Function to fetch login credentials from MongoDB
def get_login_credentials(email):
    user = mongo.db.login.find_one({"email": email})
    if user:
        return user.get("email"), user.get("password")
    else:
        return None, None

@app.route("/")
def login_redirect():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = mongo.db.login.find_one({"email": email, "password": password})
        if user:
            session["email"] = email  # Store user's email in session
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("pswd")
    
    if not mongo.db.login.find_one({"email": email}):
        mongo.db.login.insert_one({"email": email, "password": password})
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Email already exists."})

@app.route("/index")
def index():
    if "email" not in session:
        return redirect(url_for("login"))
    
    email = session["email"]
    user_history = get_user_history(email)
    return render_template("index.html", user_history=user_history)

# API route for chat generation and storing history
@app.route("/api", methods=["POST"])
def qa():
    data = {}
    if request.is_json:
        question = request.json.get("question")
        if question:
            email = session.get("email")

            # Check the 'history' collection first
            history_chat = mongo.db.history.find_one({"email": email, "question": question})

            if history_chat:
                # Response found in history, retrieve and return it
                data = {"question": question, "answer": history_chat.get("answer", "")}

                # Update or insert into the 'chats' collection as well
                try:
                    update_or_insert_chat(email, question, history_chat["answer"])
                except Exception as e:
                    app.logger.error(f"Error updating or inserting chat in 'chats' collection: {str(e)}")

            else:
                # Check the 'chats' collection if history not found
                chat_history = mongo.db.chats.find_one({"email": email, "question": question})

                if chat_history:
                    # Response found in chats history, retrieve and return it
                    data = {"question": question, "answer": chat_history.get("answer", "")}
                else:
                    # Response not found in history, call API and store in history and chats collections
                    convo = model.start_chat(history=[])
                    convo.send_message(question)
                    answer = convo.last.text

                    try:
                        # Insert the question and answer into the 'chats' collection with the user's email
                        insert_user_history(email, question, answer)

                        # Also insert into the 'history' collection
                        insert_history(email, question, answer)

                        data = {"question": question, "answer": answer}
                    except Exception as e:
                        app.logger.error(f"Error inserting chat to 'chats' collection: {str(e)}")
                        data = {"error": "Error inserting chat to 'chats' collection"}

    return jsonify(data)

# Function to insert chat history into the 'chats' collection with the user's email
def insert_user_history(email, question, answer):
    mongo.db.chats.insert_one({
        "email": email,
        "question": question,
        "answer": answer
    })

# Function to insert chat history into the 'history' collection with the user's email
def insert_history(email, question, answer):
    mongo.db.history.insert_one({
        "email": email,
        "question": question,
        "answer": answer
    })

# Function to update or insert chat history into the 'chats' collection with the user's email
def update_or_insert_chat(email, question, answer):
    mongo.db.chats.update_one(
        {"email": email, "question": question},
        {"$set": {"email": email, "question": question, "answer": answer}},
        upsert=True
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
