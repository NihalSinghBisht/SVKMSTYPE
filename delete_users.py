from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
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

def delete_users():
    try:
        # Delete test results first
        for user in users_to_remove:
            # Delete from typing_results table
            data = supabase.table('typing_results').delete().eq('user_name', user).execute()
            print(f"Deleted typing results for: {user}")
            
            # Delete from users table
            data = supabase.table('users').delete().eq('name', user).execute()
            print(f"Deleted user: {user}")
            
        print("All specified users and their data have been removed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    delete_users()