from database import get_db_connection


def get_notifications(user_id):

    connection = get_db_connection()

    notifications = connection.execute(
        """
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return notifications