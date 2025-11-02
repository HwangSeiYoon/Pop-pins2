"""
Database initialization script
Creates all tables based on models.py
"""

from db.database import *

from db import models

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
