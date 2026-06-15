from flask import Flask, redirect, request, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = b"f8e2f8af01ac1180e0d031541d863c867f0a005a6f64db292cbc4f5a08bc94c1"


# Setup Database

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lilypad700#",
)

cursor = connection.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS GradData")
cursor.execute("USE GradData")

# Create the users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_name VARCHAR(100),
        password VARCHAR(200)
    )
''')


# Setup routing

@app.route("/")
def index():
    return redirect("/login")

@app.route("/home")
def home():
    if session.get("username") is not None:
        return render_template("home.html", login=True)
    else:
        return render_template("home.html", login=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        sql = "SELECT password FROM users WHERE user_name = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchall()
        
        # Check that the user exists
        if len(result) == 0:
            return render_template("login.html", message=f"There is no user with name: {username}.")
        
        user_password = result[0][0]
        
        if check_password_hash(user_password, password):
            session["username"] = username
            
            return redirect("/home")
        else:
            return render_template("login.html", message="Invalid password")
    else:
        return render_template("login.html", message="")

@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if password != confirm_password:
            return render_template("register.html", message="Passwords do not match.")
        
        sql = "INSERT INTO users(user_name, password) VALUES (%s, %s)"
        cursor.execute(sql, (username, generate_password_hash(password)))
        
        connection.commit()
        
        return redirect("/login")
        
    else:
        return render_template("register.html", message="")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/home")

if __name__ == "__main__":
    app.run("localhost", 5000)
