import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error:
        return None


def sample_events():
    return [
        {
            "Event_ID": 1,
            "Title": "Community Meetup",
            "Theme": "Networking",
            "Date": "2026-05-12",
            "Venue": "Main Hall",
            "Organizer": "Hari",
        },
        {
            "Event_ID": 2,
            "Title": "Startup Workshop",
            "Theme": "Innovation",
            "Date": "2026-05-20",
            "Venue": "Room 204",
            "Organizer": "Harsini",
        },
        {
            "Event_ID": 3,
            "Title": "Art & Music Evening",
            "Theme": "Culture",
            "Date": "2026-06-01",
            "Venue": "Garden Lounge",
            "Organizer": "Vishwa",
        },
    ]


@app.route("/")
def home():
    conn = get_db_connection()
    if conn is None:
        events = sample_events()
        return render_template("home.html", events=events)

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT e.Event_ID, e.Title, e.Theme, e.Date, e.Venue, u.Name AS Organizer FROM Events e JOIN Users u ON e.Organizer_ID = u.User_ID"
    )
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("home.html", events=events)


@app.route("/preview")
def preview():
    return render_template("home.html", events=sample_events())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["Password"], password):
            session["user_id"] = user["User_ID"]
            session["user_name"] = user["Name"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))
        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("A user with that email already exists.", "error")
            cursor.close()
            conn.close()
            return render_template("register.html")

        cursor.execute(
            "INSERT INTO Users (Name, Email, Password) VALUES (%s, %s, %s)",
            (name, email, hashed_password),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/create-event", methods=["GET", "POST"])
def create_event():
    if "user_id" not in session:
        flash("Please log in to create an event.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        date = request.form.get("date")
        venue = request.form.get("venue")
        theme = request.form.get("theme")
        organizer_id = session["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Events (Organizer_ID, Title, Theme, Date, Venue) VALUES (%s, %s, %s, %s, %s)",
            (organizer_id, title, theme, date, venue),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Event created successfully.", "success")
        return redirect(url_for("home"))

    return render_template("create_event.html")


@app.route("/book/<int:event_id>")
def book_event(event_id):
    if "user_id" not in session:
        flash("Please log in to book an event.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Bookings WHERE User_ID = %s AND Event_ID = %s", (user_id, event_id)
    )
    existing_booking = cursor.fetchone()
    if existing_booking:
        flash("You have already booked this event.", "info")
    else:
        cursor.execute(
            "INSERT INTO Bookings (User_ID, Event_ID) VALUES (%s, %s)",
            (user_id, event_id),
        )
        conn.commit()
        flash("Booking confirmed.", "success")
    cursor.close()
    conn.close()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view your dashboard.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT b.Booking_ID, e.Title, e.Theme, e.Date, e.Venue, u.Name AS Organizer "
        "FROM Bookings b "
        "JOIN Events e ON b.Event_ID = e.Event_ID "
        "JOIN Users u ON e.Organizer_ID = u.User_ID "
        "WHERE b.User_ID = %s",
        (user_id,),
    )
    bookings = cursor.fetchall()

    cursor.execute(
        "SELECT Event_ID, Title, Theme, Date, Venue FROM Events WHERE Organizer_ID = %s",
        (user_id,),
    )
    hosted_events = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "dashboard.html",
        bookings=bookings,
        hosted_events=hosted_events,
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
