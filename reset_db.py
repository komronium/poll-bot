"""Script to reset database with new structure"""
import os
from database import engine, Base

if os.path.exists("survey_bot.db"):
    os.remove("survey_bot.db")
    print("✅ Old database deleted")

# Create new database with updated structure
Base.metadata.create_all(bind=engine)
print("✅ New database created with updated structure")

