# supabase_client.py
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()  # loads .env in dev

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_score(username: str, wpm: int, accuracy: float, duration_seconds: int):
    """
    Insert a score row into Supabase `leaderboard` table.
    Returns (data, error) same as supabase client result.
    """
    try:
        resp = supabase.table("leaderboard").insert(
            {
                "username": username,
                "wpm": wpm,
                "accuracy": float(accuracy),
                "duration_seconds": int(duration_seconds)
            }
        ).execute()
        logger.info(f"Score inserted successfully for user {username}")
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
        resp = supabase.table("leaderboard").select("*").order("wpm", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(resp.data)} leaderboard entries")
        return resp
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return {"error": str(e)}
