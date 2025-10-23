"""
Setup Notion Database Schema for Brisbane Business Bridge AI
Run this script to create the proper database structure in Notion
"""

import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

if not NOTION_TOKEN or not NOTION_DATABASE_ID:
    print("ERROR: Missing NOTION_TOKEN or NOTION_DATABASE_ID in .env file")
    exit(1)

notion = Client(auth=NOTION_TOKEN)

print("=" * 60)
print("Brisbane Business Bridge AI - Notion Database Setup")
print("=" * 60)

# Define the required database schema
schema = {
    "Name": {
        "title": {}
    },
    "User": {
        "rich_text": {}
    },
    "User Company": {
        "rich_text": {}
    },
    "User Email": {
        "email": {}
    },
    "Delegate": {
        "rich_text": {}
    },
    "Delegate Company": {
        "rich_text": {}
    },
    "Delegate Email": {
        "email": {}
    },
    "Match Score": {
        "number": {
            "format": "percent"
        }
    },
    "Rank": {
        "number": {}
    },
    "Sector": {
        "select": {
            "options": [
                {"name": "Local Government", "color": "blue"},
                {"name": "Property Development", "color": "green"},
                {"name": "Professional Services", "color": "purple"},
                {"name": "Food & Agribusiness", "color": "orange"},
                {"name": "Tourism & Hospitality", "color": "pink"},
                {"name": "Manufacturing", "color": "red"},
                {"name": "Infrastructure & Transport", "color": "gray"},
                {"name": "Finance & Banking", "color": "yellow"},
                {"name": "Technology", "color": "default"},
                {"name": "Education", "color": "brown"},
                {"name": "Healthcare", "color": "default"},
                {"name": "Legal Services", "color": "default"},
                {"name": "Marketing & Communications", "color": "default"},
                {"name": "Architecture & Design", "color": "default"},
                {"name": "Engineering", "color": "default"},
                {"name": "Retail", "color": "default"},
                {"name": "Other", "color": "default"}
            ]
        }
    },
    "Event": {
        "select": {
            "options": [
                {"name": "Boldly Brisbane Forum 2025", "color": "blue"},
                {"name": "APCS 2025", "color": "green"},
                {"name": "Other", "color": "gray"}
            ]
        }
    },
    "Status": {
        "select": {
            "options": [
                {"name": "New Match", "color": "blue"},
                {"name": "Contacted", "color": "yellow"},
                {"name": "Meeting Scheduled", "color": "orange"},
                {"name": "Meeting Completed", "color": "green"},
                {"name": "Follow-up Required", "color": "pink"},
                {"name": "Closed", "color": "gray"}
            ]
        }
    },
    "Created": {
        "created_time": {}
    }
}

print("\nAttempting to update database schema...")
print(f"Database ID: {NOTION_DATABASE_ID}")

try:
    # Update the database schema
    response = notion.databases.update(
        database_id=NOTION_DATABASE_ID,
        properties=schema
    )

    print("\n[SUCCESS] Database schema has been configured.")
    print("\nThe following properties have been added:")
    print("- Name (Title)")
    print("- User (Text)")
    print("- User Company (Text)")
    print("- User Email (Email)")
    print("- Delegate (Text)")
    print("- Delegate Company (Text)")
    print("- Delegate Email (Email)")
    print("- Match Score (Number - Percentage)")
    print("- Rank (Number)")
    print("- Sector (Select with 17 options)")
    print("- Event (Select: Boldly Brisbane, APCS 2025)")
    print("- Status (Select: New Match, Contacted, etc.)")
    print("- Created (Timestamp)")

    print("\n" + "=" * 60)
    print("Your Notion database is ready to receive matches!")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Failed to update database schema")
    print(f"Error details: {e}")
    print("\nTroubleshooting:")
    print("1. Check that your NOTION_TOKEN has edit permissions")
    print("2. Verify the NOTION_DATABASE_ID is correct")
    print("3. Ensure the integration has been added to the database page")
    import traceback
    traceback.print_exc()
