# Online Event Planning and Booking System

A simple Flask-based web application for event organizers and attendees.

## Features
- Register and log in
- View all events
- Create new events
- Book events
- User dashboard showing booked events and hosted events

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create the MySQL database and tables:
   - Open MySQL and run `init_db.sql`
   - Update `config.py` with your MySQL credentials
3. Run the app:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000/`

## Notes
- The app uses a simple session-based login.
- Passwords are stored hashed using Werkzeug.
- This project is designed for learning basic CRUD and relational database usage.
