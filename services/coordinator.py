from database import get_db_connection


def coordinate(request_id, user_id, room, message, analysis):

    department = analysis["department"]
    priority = analysis["priority"]

    connection = get_db_connection()

    # Main operational task
    connection.execute(
        """
        INSERT INTO tasks
        (request_id, department, description, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            request_id,
            department,
            message,
            "Pending"
        )
    )

    # Special coordination logic
    coordinated = []

    text = message.lower()

    if "flight" in text or "delayed" in text:
        connection.execute(
            """
            INSERT INTO tasks
            (request_id, department, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                request_id,
                "Transport",
                "Review airport pickup due to flight delay",
                "Pending"
            )
        )

        connection.execute(
            """
            INSERT INTO tasks
            (request_id, department, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                request_id,
                "Reception",
                "Update expected guest arrival time",
                "Pending"
            )
        )

        coordinated = [
            "Transport Agent: Airport pickup adjustment",
            "Reception Agent: Arrival time update"
        ]

    connection.execute(
        """
        INSERT INTO notifications (user_id, message)
        VALUES (?, ?)
        """,
        (
            user_id,
            f"{department} team has been notified."
        )
    )

    connection.commit()
    connection.close()

    return coordinated