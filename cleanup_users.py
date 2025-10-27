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
    "Nihal singh bisht",
    "Nihal Singh Bisht"
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
        
        # Get current leaderboard sorted by WPM to verify the update
        result = supabase.table('leaderboard').select('username, wpm, accuracy').order('wpm', desc=True).execute()
        
        if result.data:
            print("\nCurrent leaderboard order:")
            for entry in result.data:
                print(f"{entry['username']}: {entry['wpm']} WPM")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    remove_users()