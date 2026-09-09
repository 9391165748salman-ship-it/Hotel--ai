from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from config import Config
from database import get_db_connection, init_db
from services.ai_service import understand_request
from services.coordinator import coordinate
from services.notification import get_notifications
from services.proactive import get_proactive_message


app = Flask(__name__)
app.config.from_object(Config)


# -------------------------
# DATABASE
# -------------------------

with app.app_context():
    init_db()


# -------------------------
# LOGIN
# -------------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():

    role = request.form.get("role")

    if role == "staff":
        session["user_id"] = 2
        session["role"] = "staff"
    else:
        session["user_id"] = 1
        session["role"] = "guest"

    return redirect(
        url_for(
            "staff_dashboard"
            if role == "staff"
            else "guest_dashboard"
        )
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# -------------------------
# GUEST DASHBOARD
# -------------------------

@app.route("/guest")
def guest_dashboard():

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    proactive = get_proactive_message()

    notifications = get_notifications(user_id)

    return render_template(
        "guest_dashboard.html",
        user=user,
        proactive=proactive,
        notifications=notifications
    )


# -------------------------
# AI CHAT
# -------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "response": "Please tell me how I can help you."
        })

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    room = user["room"] if user else "205"

    # AI understanding
    analysis = understand_request(message)

    # Create request
    cursor = connection.execute(
        """
        INSERT INTO requests
        (user_id, room, message, department, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            room,
            message,
            analysis["department"],
            analysis["priority"],
            "Pending"
        )
    )

    request_id = cursor.lastrowid

    connection.commit()
    connection.close()

    # Coordination engine
    coordinated = coordinate(
        request_id,
        user_id,
        room,
        message,
        analysis
    )

    department = analysis["department"]

    response = (
        f"Got it! I've understood this as a "
        f"{analysis['intent']}."
        f"<br><br>"
        f"🤖 <b>{department} Agent</b> has received the task."
    )

    if analysis["priority"] == "High":
        response += (
            "<br><br>🔴 This request has been marked "
            "<b>High Priority</b>."
        )

    if coordinated:
        response += "<br><br><b>🔗 Coordination Engine activated:</b>"

        for task in coordinated:
            response += f"<br>• {task}"

    response += (
        "<br><br>✅ You don't need to contact "
        "different hotel departments separately."
    )

    return jsonify({
        "success": True,
        "response": response,
        "department": department,
        "priority": analysis["priority"],
        "intent": analysis["intent"]
    })


# -------------------------
# STAFF DASHBOARD
# -------------------------

@app.route("/staff")
def staff_dashboard():

    connection = get_db_connection()

    stats = {}

    stats["total"] = connection.execute(
        "SELECT COUNT(*) FROM requests"
    ).fetchone()[0]

    stats["pending"] = connection.execute(
        "SELECT COUNT(*) FROM requests WHERE status = 'Pending'"
    ).fetchone()[0]

    stats["progress"] = connection.execute(
        "SELECT COUNT(*) FROM requests WHERE status = 'In Progress'"
    ).fetchone()[0]

    stats["urgent"] = connection.execute(
        """
        SELECT COUNT(*)
        FROM requests
        WHERE priority IN ('High', 'Critical')
        """
    ).fetchone()[0]


 

    requests_list = connection.execute(
        """
        SELECT *
        FROM requests
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    tasks = connection.execute(
        """
        SELECT *
        FROM tasks
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    connection.close()

    return render_template(
        "staff_dashboard.html",
        stats=stats,
        requests=requests_list,
        tasks=tasks
    )


# -------------------------
# UPDATE REQUEST
# -------------------------

@app.route("/api/request/<int:request_id>/status", methods=["POST"])
def update_status(request_id):

    data = request.get_json()

    status = data.get("status")

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE requests
        SET status = ?
        WHERE id = ?
        """,
        (status, request_id)
    )

    connection.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE request_id = ?
        """,
        (status, request_id)
    )

    connection.commit()

    connection.close()

    return jsonify({
        "success": True
    })


# -------------------------
# REQUEST HISTORY
# -------------------------

@app.route("/requests")
def requests_page():

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    requests_list = connection.execute(
        """
        SELECT *
        FROM requests
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "requests.html",
        requests=requests_list
    )
# -------------------------
# GUEST SERVICE REQUEST
# -------------------------

@app.route("/api/service-request", methods=["POST"])
def service_request():

    data = request.get_json()

    service = data.get("service", "").strip()
    message = data.get("message", "").strip()

    if not service:
        return jsonify({
            "success": False,
            "message": "Please select a service."
        })

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    room = user["room"] if user else "205"

    # AI-style service routing
    service_routes = {

        "Room Cleaning": {
            "department": "Housekeeping",
            "priority": "Normal"
        },

        "Airport Pickup": {
            "department": "Transport",
            "priority": "High"
        },

        "Food Service": {
            "department": "Food Service",
            "priority": "Normal"
        },

        "Maintenance": {
            "department": "Maintenance",
            "priority": "High"
        },

        "Parking": {
            "department": "Parking",
            "priority": "Normal"
        },

        "Reception": {
            "department": "Reception",
            "priority": "Normal"
        }
    }

    route = service_routes.get(
        service,
        {
            "department": "Reception",
            "priority": "Normal"
        }
    )

    final_message = message if message else service

    cursor = connection.execute(
        """
        INSERT INTO requests
        (user_id, room, message, department, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            room,
            final_message,
            route["department"],
            route["priority"],
            "Pending"
        )
    )

    request_id = cursor.lastrowid

    # Create department task
    connection.execute(
        """
        INSERT INTO tasks
        (request_id, department, description, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            request_id,
            route["department"],
            final_message,
            "Pending"
        )
    )

    connection.commit()
    connection.close()

    return jsonify({

        "success": True,

        "request_id": request_id,

        "service": service,

        "department": route["department"],

        "priority": route["priority"],

        "status": "Pending",

        "message":
            f"Your request has been routed to "
            f"the {route['department']} Agent."
    })
# -------------------------
# SERVICES
# -------------------------

@app.route("/services")
def services():

    return render_template("services.html")


# -------------------------
# PROFILE
# -------------------------

@app.route("/profile")
def profile():

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "profile.html",
        user=user
    )
# -------------------------
# AI ARCHITECTURE
# -------------------------

@app.route("/architecture")
def architecture():

    return render_template("architecture.html")
# -------------------------
# FLIGHT DELAY DEMO
# -------------------------

@app.route("/flight-delay")
def flight_delay():

    return render_template("flight_delay.html")


@app.route("/api/flight-delay", methods=["POST"])
def process_flight_delay():

    data = request.get_json()

    flight = data.get("flight", "AI-542")
    delay = data.get("delay", "3 Hours")

    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    room = user["room"] if user else "205"

    message = (
        f"Flight {flight} has been delayed by {delay}. "
        f"Guest arrival time needs to be updated."
    )

    # Create main request
    cursor = connection.execute(
        """
        INSERT INTO requests
        (user_id, room, message, department, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            room,
            message,
            "Coordination Engine",
            "High",
            "In Progress"
        )
    )

    request_id = cursor.lastrowid

    # Create coordinated department tasks
    departments = [
        (
            "Reception",
            "Update guest expected arrival time"
        ),
        (
            "Transport",
            f"Reschedule airport pickup for Flight {flight}"
        ),
        (
            "Housekeeping",
            "Maintain room readiness for delayed arrival"
        )
    ]

    for department, description in departments:

        connection.execute(
            """
            INSERT INTO tasks
            (request_id, department, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                request_id,
                department,
                description,
                "Pending"
            )
        )

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "request_id": request_id,
        "flight": flight,
        "delay": delay,
        "tasks": [
            "Reception: Expected arrival updated",
            "Transport: Airport pickup rescheduled",
            "Housekeeping: Room readiness maintained"
        ]
    })
if __name__ == "__main__":
    app.run(debug=True)