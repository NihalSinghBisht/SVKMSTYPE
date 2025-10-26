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

def insert_score(username: str, wpm: int, accuracy: float, duration_seconds: int):
    """
    Insert a score row into Supabase `scores` table.
    Returns (data, error) same as supabase client result.
    """
    try:
        logger.info(f"Attempting to insert score for user: {username}")
        logger.info(f"Score details - WPM: {wpm}, Accuracy: {accuracy}, Duration: {duration_seconds}")
        
        supabase = get_supabase_client()
        resp = supabase.table("scores").insert(
            {
                "username": username,
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
    Get the top scores ordered by WPM
    Returns (data, error) same as supabase client result
    """
    try:
        logger.info(f"Fetching leaderboard (limit: {limit})")
        supabase = get_supabase_client()
        resp = supabase.table("scores").select("*").order("wpm", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(resp.data) if hasattr(resp, 'data') else 0} leaderboard entries")
        return resp
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return {"error": str(e)}
