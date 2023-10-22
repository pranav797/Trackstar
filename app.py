import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpersfp import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")

def is_provided(field):
    if not request.form.get(field):
        return apology(f"must provide {field}", 403)


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        if not request.form.get("password"):
            return apology("must provide password", 403)

        else:
            try:
                primary_key=db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   username=request.form.get("username"),
                   password=generate_password_hash(request.form.get("password")))
                if primary_key is None:
                    return("Please provide registration details.", 403)
                session["user_id"] = primary_key
                redirect("/")
            except:
                return apology("Username already in use.", 403)

        return redirect("/")


    else:
        return render_template("register(fp).html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login(fp).html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/workout", methods=["GET","POST"])
@login_required
def workout():

#for filter function, use if commands

    filter_choice = request.form.get("filter_fp")

#filters for type
    if filter_choice == "upper-body":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE typew = 'upper-body';
        """)
    elif filter_choice == "core":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE typew = 'core';
        """)
    elif filter_choice == "lower-body":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE typew = 'lower-body';
        """)
    elif filter_choice == "hiit":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE typew = 'hiit';
        """)


#filters for difficulty
    elif filter_choice == "beginner":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE difficulty = 'beginner';
        """)
    elif filter_choice == "intermediate":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE difficulty = 'intermediate';
        """)
    elif filter_choice == "advanced":
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
            WHERE difficulty = 'advanced';
        """)


#standard filter
    else:
        workouts = db.execute("""
            SELECT name, typew, difficulty, time, description
            FROM workouts
        """)


    return render_template ("workout.html", workouts=workouts)

#use full screen modal


@app.route("/create", methods=["GET","POST"])
@login_required
def create():

    if request.method == "POST":

        errors = is_provided("name") or is_provided("typew") or is_provided("difficulty") or is_provided("length") or is_provided("workout")
        if errors:
             return errors

        name = request.form.get("name")
        typew = request.form.get("typew")
        difficulty = request.form.get("difficulty")
        length = request.form.get("length")
        workout = request.form.get("workout")

        db.execute("""
            INSERT INTO workouts (user_id, name, typew, difficulty, time, description)
            VALUES (:user_id, :name, :typew, :difficulty, :time, :workout)
            """,
            user_id = session["user_id"],
            name = name,
            typew = typew,
            difficulty = difficulty,
            time = length,
            workout = workout
        )

        flash("Workout created and posted!")

        return redirect ("/workout")

    else:
        return render_template("create.html")