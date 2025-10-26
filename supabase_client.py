# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()  # loads .env in dev

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_score(username: str, wpm: int, accuracy: float, duration_seconds: int):
    """
    Insert a score row into Supabase `scores` table.
    Returns (data, error) same as supabase client result.
    """
    try:
        resp = supabase.table("scores").insert(
            {
                "username": username,
                "wpm": wpm,
                "accuracy": float(accuracy),
                "duration_seconds": int(duration_seconds)
            }
        ).execute()
        return resp
    except Exception as e:
        return {"error": str(e)}

def get_leaderboard(limit: int = 10):
    """
    Get the top scores ordered by WPM
    Returns (data, error) same as supabase client result
    """
    try:
        resp = supabase.table("scores").select("*").order("wpm", desc=True).limit(limit).execute()
        return resp
    except Exception as e:
        return {"error": str(e)}
