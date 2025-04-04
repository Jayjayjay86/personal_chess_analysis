# init_db.py
from app import analyzer

if __name__ == "__main__":
    print("Initializing database...")
    analyzer._init_db()
    print("Database initialized successfully!")