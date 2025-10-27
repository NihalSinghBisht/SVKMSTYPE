from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    "https://hnlvilglkeyhqawmfyny.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhubHZpbGdsa2V5aHFhd21meW55Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTA2NjQsImV4cCI6MjA3Njk4NjY2NH0.fOJPtv1tdZZRG_eIefpSfYjYTJqBqcfT_G-qn0DAYpI"
)

# Users to remove
users_to_remove = [
    "dalit panter 🐯",
    "tanvir ki ma ka client",
    "Vedant marry Aashi",
    "RIYA NIHAL SINGH",
    "Nihal",
    "Tanvir ka client"
]

def remove_users():
    try:
        # Delete from leaderboard table
        for user in users_to_remove:
            print(f"Removing data for user: {user}")
            
            # Delete from leaderboard table
            data = supabase.table('leaderboard').delete().eq('username', user).execute()
            print(f"- Deleted user entry and their scores")
            
        print("\nAll specified users and their data have been removed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    remove_users()