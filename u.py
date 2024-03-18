# update_db.py

from app import app, db
from models import Termen

def update_database_schema():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    update_database_schema()
