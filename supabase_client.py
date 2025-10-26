# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # loads .env in dev

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Log Supabase configuration status
if SUPABASE_URL and SUPABASE_KEY:
    logger.info("Supabase configuration found")
    logger.info(f"Supabase URL: {SUPABASE_URL[:8]}...{SUPABASE_URL[-4:]}")  # Log partial URL for security
else:
    logger.error("Missing Supabase configuration!")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client created successfully")
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
        
        resp = supabase.table("scores").insert(
            {
                "username": username,
                "wpm": wpm,
                "accuracy": float(accuracy),
                "duration_seconds": int(duration_seconds)
            }
        ).execute()
        
        logger.info(f"Score inserted successfully: {resp}")
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
        resp = supabase.table("scores").select("*").order("wpm", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(resp.data) if hasattr(resp, 'data') else 0} leaderboard entries")
        return resp
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return {"error": str(e)}
