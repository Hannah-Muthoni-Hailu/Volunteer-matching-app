from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_session import Session
from bson.objectid import ObjectId
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = PyMongo(app).cx
app.config["SESSION_MONGODB_DB"] = "volunteer_system"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
Session(app)

@app.route('/')
def home():
    opportunities = mongo.db.opportunities.find()
    return render_template("index.html", opportunities=opportunities)

@app.route('/dashboard')
def dashboard():
    if "user_id" in session:
        return redirect(url_for("account"))
    return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            return redirect(url_for("home"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        rpassword = request.form.get("repeat_password")
        phone = request.form.get("phone-number")
        county = request.form.get("county")

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return "Email already registered"
        
        if password != rpassword:
            return "Passwords must match"
        
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        mongo.db.users.insert_one({
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "county": county
        })
        return redirect(url_for("login"))
    return render_template('register.html')

@app.route('/account', methods=["GET", "POST"])
def account():
    user_id = session["user_id"]
    try:
        user_id = ObjectId(user_id)
    except:
        return "Invalid user ID format", 400
    
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        rpassword = request.form.get("repeat_password")
        phone = request.form.get("phone-number")
        county = request.form.get("county")

        if password != rpassword:
            return "Passwords must match"

        update_data = {
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "phone": phone,
            "county": county
        }
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            update_data["password"] = hashed_password

        mongo.db.users.update_one({"_id": user_id}, {"$set": update_data})
        return redirect(url_for("account"))
    
    user = mongo.db.users.find_one({"_id": user_id})
    if not user:
        return "User not found", 404
    
    counties = ["Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay", "Isiolo","Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi", "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale","Laikipia", "Lamu", "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa", "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua", "Nyeri", "Samburu", "Siaya", "Taita-Taveta", "Tana River", "Tharaka-Nithi", "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"]
    return render_template("account.html", user=user, counties=counties)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)