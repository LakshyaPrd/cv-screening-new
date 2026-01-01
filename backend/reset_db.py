"""
Database reset script to drop and recreate all tables with correct schema.
Run this to fix schema mismatches.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine
from app.models.batch import Batch
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult


def reset_database():
    """Drop all tables and recreate them with the current schema."""
    print("⚠️  WARNING: This will delete ALL data in the database!")
    print("📋 Tables to be dropped and recreated:")
    print("   - batches")
    print("   - candidates")
    print("   - job_descriptions")
    print("   - match_results")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Aborted. No changes made.")
        return
    
    print("\n🗑️  Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return
    
    print("\n🔨 Creating tables with new schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return
    
    print("\n✨ Database reset complete!")
    print("🎉 Schema is now up to date with the latest models")
    print("\nNew columns added to candidates table:")
    print("   ✓ date_of_birth")
    print("   ✓ nationality")
    print("   ✓ marital_status")
    print("   ✓ military_status")
    print("   ✓ current_country")
    print("   ✓ current_city")
    print("   ✓ linkedin_url")
    print("   ✓ portfolio_url")
    print("   ✓ behance_url")
    print("   ✓ current_position")
    print("   ✓ discipline")
    print("   ✓ sub_discipline")
    print("   ✓ And many more...")


if __name__ == "__main__":
    reset_database()
