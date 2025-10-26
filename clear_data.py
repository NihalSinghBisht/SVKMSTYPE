from supabase_client import clear_leaderboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        response = clear_leaderboard()
        if 'error' in response:
            logger.error(f"Failed to clear data: {response['error']}")
        else:
            logger.info("Successfully cleared all leaderboard data")
    except Exception as e:
        logger.error(f"Error: {str(e)}")