from supabase_client import get_leaderboard, delete_user_from_leaderboard
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_riya_users():
    try:
        # Get all users from leaderboard
        response = get_leaderboard(limit=1000)  # Get a large number to ensure we get all users
        
        if 'error' in response:
            logger.error(f"Error fetching leaderboard: {response['error']}")
            return
            
        users = response.get('data', [])
        removed_count = 0
        
        for user in users:
            username = user.get('username', '').lower()
            # Check if username is a variant of RIYA
            if re.match(r'^r\s*i\s*y\s*a+\b', username):
                logger.info(f"Removing user: {username}")
                delete_response = delete_user_from_leaderboard(user['username'])
                if 'error' not in delete_response:
                    removed_count += 1
                else:
                    logger.error(f"Error removing user {username}: {delete_response['error']}")
        
        logger.info(f"Successfully removed {removed_count} users with RIYA variants")
        
    except Exception as e:
        logger.error(f"Error during removal process: {str(e)}")

if __name__ == "__main__":
    remove_riya_users()