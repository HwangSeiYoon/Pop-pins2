"""
Database initialization script
Creates all tables based on models.py
"""

from db.database import init_db

if __name__ == "__main__":
    init_db()
