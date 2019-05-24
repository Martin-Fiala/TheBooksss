import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session

app = Flask(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def logged():
	if session.get("username") is None:
		return 0
	else:
		return 1

@app.route("/")
def index():
	if logged():
		return render_template("search.html")
	else:
		return render_template("login.html")
	
@app.route("/signup")
def signup():
	if logged():
		return redirect(url_for("index"))
	else:
		return render_template("signup.html")
	
@app.route("/login")
def login():
	if logged():
		return redirect(url_for("index"))
	else:
		return render_template("login.html")
	
@app.route("/signuphandler", methods=["POST"])
def signuphandler():
	username = request.form.get("username")
	password = request.form.get("password")
	repassword = request.form.get("re-password")
	email = request.form.get("email")
	
	user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
	if user.rowcount != 0:
		return render_template("signup.html")
	
	db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", {"username": username, "password": password, "email": email})
	db.commit()
	
	session["username"] = username
	return redirect(url_for("index"))

@app.route("/loginhandler", methods=["POST"])
def loginhandler():
	username = request.form.get("username")
	password = request.form.get("password")
	
	user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password})
	if user.rowcount != 0:
		session["username"] = username
	
	return redirect(url_for("index"))

@app.route("/logouthandler")
def logouthandler():
	session.pop("username")
	return redirect(url_for("index"))
	
@app.route("/searchhandler", methods=["POST"])
def searchhandler():
	search = "%"
	search += request.form.get("search")
	search += "%"
	search = search.lower()
	results = []
	results.extend(db.execute("SELECT * FROM BOOKS WHERE LOWER(title) LIKE :search", {"search":search}))
	results.extend(db.execute("SELECT * FROM BOOKS WHERE LOWER(author) LIKE :search", {"search":search}))
	results.extend(db.execute("SELECT * FROM BOOKS WHERE LOWER(isbn) LIKE :search", {"search":search}))
	return render_template("results.html", results=results)