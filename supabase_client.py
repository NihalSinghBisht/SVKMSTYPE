# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # loads .env in dev

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Get or create a singleton instance of Supabase client
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Missing Supabase configuration!")
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in environment")
        
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client created/retrieved successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise

def insert_score(username: str, college: str, wpm: int, accuracy: float, duration_seconds: int):
    """
    Insert a score row into leaderboard table.
    Returns (data, error) same as supabase client result.
    """
    try:
        logger.info(f"Attempting to insert score for user: {username}")
        logger.info(f"Score details - College: {college}, WPM: {wpm}, Accuracy: {accuracy}, Duration: {duration_seconds}")
        
        supabase = get_supabase_client()
        
        # First delete any existing record for this username
        supabase.table("leaderboard").delete().eq("username", username).execute()
        
        # Then insert the new record
        resp = supabase.table("leaderboard").insert(
            {
                "username": username,
                "college": college,
                "wpm": wpm,
                "accuracy": float(accuracy),
                "duration_seconds": int(duration_seconds)
            }
        ).execute()
        
        logger.info(f"Score inserted successfully")
        return resp
    except Exception as e:
        logger.error(f"Error inserting score: {str(e)}")
        return {"error": str(e)}

def get_leaderboard(limit: int = 10):
    """
    Get the top scores ordered by WPM, showing only the best score per user
    Returns (data, error) same as supabase client result
    """
    try:
        logger.info(f"Fetching leaderboard (limit: {limit})")
        supabase = get_supabase_client()
        
        # First get all scores to calculate aggregates
        resp = supabase.table("leaderboard").select("*").execute()
        
        # Group by username and calculate metrics
        user_scores = {}
        for entry in resp.data:
            username = entry.get('username')
            if username not in user_scores:
                user_scores[username] = {
                    'username': username,
                    'college': entry.get('college', 'Unknown'),
                    'best_wpm': float(entry.get('wpm', 0)),
                    'avg_accuracy': float(entry.get('accuracy', 0)),
                    'tests_taken': 1
                }
            else:
                current = user_scores[username]
                current['best_wpm'] = max(current['best_wpm'], float(entry.get('wpm', 0)))
                current['avg_accuracy'] = (current['avg_accuracy'] * current['tests_taken'] + 
                                        float(entry.get('accuracy', 0))) / (current['tests_taken'] + 1)
                current['tests_taken'] += 1
        
        # Convert to list and sort by best WPM
        rankings = list(user_scores.values())
        rankings.sort(key=lambda x: x['best_wpm'], reverse=True)
        
        # Apply limit
        rankings = rankings[:limit]
        
        logger.info(f"Retrieved {len(rankings)} unique users for leaderboard")
        return {"data": rankings}
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return {"error": str(e)}

def clear_leaderboard():
    """
    Remove all records from the leaderboard table
    Returns (data, error) same as supabase client result
    """
    try:
        logger.info("Attempting to clear all leaderboard data")
        supabase = get_supabase_client()
        
        # Delete all records from the leaderboard table
        resp = supabase.table("leaderboard").delete().neq("id", 0).execute()
        
        logger.info("Successfully cleared leaderboard data")
        return resp
    except Exception as e:
        logger.error(f"Error clearing leaderboard: {str(e)}")
        return {"error": str(e)}

def delete_user_from_leaderboard(username: str):
    """
    Remove all entries for a specific user from the leaderboard
    Returns (data, error) same as supabase client result
    """
    try:
        logger.info(f"Attempting to delete user {username} from leaderboard")
        supabase = get_supabase_client()
        
        # Delete all records for this username
        resp = supabase.table("leaderboard").delete().eq("username", username).execute()
        
        logger.info(f"Successfully deleted user {username} from leaderboard")
        return resp
    except Exception as e:
        logger.error(f"Error deleting user from leaderboard: {str(e)}")
        return {"error": str(e)}
