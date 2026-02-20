from flask import Flask, render_template, request, redirect, session
import sqlite3
import time
import hashlib
from services.nlp_service import classify_issue

app = Flask(__name__)
app.secret_key = "secret123"

chat_history = []

# ---------- DATABASE ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue TEXT,
            category TEXT,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

def insert_default_admin():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ("admin", hash_password("admin123"))
        )

    conn.commit()
    conn.close()

# ---------- DASHBOARD ----------

def dashboard_stats():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    stats = {}
    c.execute("SELECT COUNT(*) FROM tickets")
    stats["total"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM tickets WHERE status='OPEN'")
    stats["open"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM tickets WHERE status='RESOLVED'")
    stats["resolved"] = c.fetchone()[0]

    for cat in ["Network", "Software", "Hardware", "Other"]:
        c.execute("SELECT COUNT(*) FROM tickets WHERE category=?", (cat,))
        stats[cat.lower()] = c.fetchone()[0]

    conn.close()
    return stats

# ---------- CHATBOT ----------

def generate_reply(msg):
    msg = msg.lower()

    if "wifi" in msg or "network" in msg:
        return "Please restart your router and check network cables."
    elif "software" in msg or "app" in msg:
        return "Try reinstalling or updating the software."
    elif "keyboard" in msg or "mouse" in msg or "hardware" in msg:
        return "Please check the hardware connections."
    else:
        return "I have escalated this issue to IT support."

# ---------- ROUTES ----------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_msg = request.form["message"]

        chat_history.append({
            "user": user_msg,
            "bot": "Analyzing your issue..."
        })

        time.sleep(0.5)
        chat_history[-1]["bot"] = generate_reply(user_msg)

    return render_template(
        "index.html",
        chat=chat_history,
        stats=dashboard_stats()
    )

@app.route("/resolve", methods=["POST"])
def resolve():
    chat_history.append({
        "user": "Status",
        "bot": "✅ Issue marked as RESOLVED."
    })
    return redirect("/")

@app.route("/escalate", methods=["POST"])
def escalate():
    last_msg = chat_history[-1]["user"]
    category = classify_issue(last_msg)

    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (issue, category, status) VALUES (?, ?, 'OPEN')",
        (last_msg, category)
    )
    conn.commit()
    conn.close()

    chat_history.append({
        "user": "Status",
        "bot": f"❌ Escalated to IT Admin (Category: {category})"
    })

    return redirect("/")

# ---------- ADMIN ----------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = sqlite3.connect("tickets.db")
        c = conn.cursor()
        c.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )
        admin = c.fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect("/admin/dashboard")

        return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tickets")
    tickets = c.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", tickets=tickets)

# ---------- MAIN ----------

if __name__ == "__main__":
    init_db()
    insert_default_admin()
    app.run(debug=True)