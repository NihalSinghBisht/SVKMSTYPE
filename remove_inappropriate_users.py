from supabase_client import delete_user_from_leaderboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_specific_users():
    users_to_remove = [
        "ria_left_nihal",
        "Teri maa ka ashiq"
    ]
    
    for username in users_to_remove:
        try:
            response = delete_user_from_leaderboard(username)
            if 'error' not in response:
                logger.info(f"Successfully removed user: {username}")
            else:
                logger.error(f"Error removing user {username}: {response['error']}")
        except Exception as e:
            logger.error(f"Exception removing user {username}: {str(e)}")

if __name__ == "__main__":
    remove_specific_users()