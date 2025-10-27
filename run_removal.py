import logging
from remove_inappropriate_users import remove_specific_users

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    remove_specific_users()