from app import create_app
from app.extensions import db
from app.models import Task
import sqlite3
from datetime import datetime

def parse_date(date_value):
    if not date_value:
        return None
    return datetime.strptime(date_value, "%Y-%m-%d").date()
app = create_app()

SQLITE_DB = "instance/todo.db"

def migrate():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, status, due_date, priority, user_id FROM task")
    rows = cursor.fetchall()

    with app.app_context():

        # optional clean (only first time)
        db.session.query(Task).delete()
        db.session.commit()
        

        for row in rows:
            task = Task(
                id=row[0],
                title=row[1],
                status=row[2],
                due_date=parse_date(row[3]),
                priority=row[4],
                user_id=row[5]
            )
            db.session.add(task)

        db.session.commit()

    print("Migration completed!")

if __name__ == "__main__":
    migrate()