from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import timedelta
from supabase_client import insert_score, get_leaderboard, delete_user_from_leaderboard
from better_profanity import profanity
from custom_profanity import CUSTOM_PROFANITY_WORDS
import os
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure profanity filter
profanity.load_censor_words()
profanity.add_censor_words(CUSTOM_PROFANITY_WORDS)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'svkm-typing-test-2025-secret-key')  # Use environment variable with fallback
app.permanent_session_lifetime = timedelta(days=7)

def contains_inappropriate_text(text):
    """
    Advanced check for inappropriate content including Hindi terms and variations
    """
    # Convert to lowercase for better matching
    text = text.lower()
    
    # Check using better-profanity library
    if profanity.contains_profanity(text):
        return True
        
    # Check for substrings (to catch partial matches like "ma ka")
    for word in CUSTOM_PROFANITY_WORDS:
        if word.lower() in text:
            return True
            
    # Check for common patterns with spaces or dots
    text_without_spaces = text.replace(" ", "").replace(".", "")
    for word in CUSTOM_PROFANITY_WORDS:
        if word.replace(" ", "").lower() in text_without_spaces:
            return True
            
    return False

def validate_username(username):
    # Check for inappropriate content
    if contains_inappropriate_text(username):
        return False, "Username contains inappropriate language"
    
    # Check for all name variants anywhere in the username
    blocked_patterns = [
        r'r\s*i\s*y\s*a+',
        r'r\s*h\s*e\s*a+',
        r'r\s*i\s*a+',
        r'r\s*e+\s*y\s*a+'
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, username.lower()):
            return False, "This username is not allowed"
    
    # Check minimum length
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    # Check maximum length
    if len(username) > 30:
        return False, "Username must be less than 30 characters"
    
    # Only allow letters, numbers, and underscores
    if not username.replace('_', '').isalnum():
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    sap_id = request.form.get('sap-id')
    name = request.form.get('name', '')  # Get name from signup form
    college = request.form.get('college', '')  # Get college from signup form

    if not email or not sap_id:
        error_msg = "Email and SAP ID are required."
        return render_template('login.html', error=error_msg)

    # Validate username
    username = name if name else email.split('@')[0]
    is_valid, error_message = validate_username(username)
    
    if not is_valid:
        return render_template('login.html', error=error_message)

    # Store user info in session
    session['user'] = {
        'email': email,
        'sap_id': sap_id,
        'username': username,
        'college': college  # Store college information
    }
    return redirect(url_for('main'))

@app.route('/main')
@app.route('/home')
def main():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/submit_result', methods=['POST'])
def submit_result():
    if 'user' not in session:
        logger.error('Submit result attempted without login')
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    logger.info(f"Received test results for user: {session['user']['username']}")
    logger.info(f"Test data received: {data}")
    
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    duration = data.get('duration_seconds', 60)  # Default to 60 seconds if not provided
    college = session['user'].get('college', 'Unknown')  # Fetch college from session

    if not all([wpm, accuracy, college]):
        logger.error(f"Missing required data - WPM: {wpm}, Accuracy: {accuracy}, College: {college}")
        return jsonify({'success': False, 'error': 'Missing required data'})

    try:
        # Insert score directly using the updated function
        response = insert_score(
            username=session['user']['username'],
            college=college,
            wpm=wpm,
            accuracy=accuracy,
            duration_seconds=duration
        )
        
        if 'error' in response:
            logger.error(f"Error from Supabase: {response['error']}")
            return jsonify({'success': False, 'error': response['error']})
            
        logger.info("Score submitted successfully")
        return jsonify({'success': True, 'redirect': '/leaderboard'})

    except Exception as e:
        logger.error(f"Exception during score submission: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        logger.warning("Leaderboard access attempted without login")
        return redirect(url_for('login'))
    
    selected_college = request.args.get('college', 'all')
    
    try:
        logger.info("Fetching leaderboard data")
        response = get_leaderboard(limit=50)
        
        if 'error' in response:
            logger.error(f"Error fetching leaderboard: {response['error']}")
            rankings = []
        else:
            raw_data = response.get('data', [])
            logger.info(f"Raw leaderboard data: {raw_data}")
            
            # Filter by college if needed
            if selected_college != 'all':
                rankings = [entry for entry in raw_data if entry.get('college', '').upper() == selected_college.upper()]
            else:
                rankings = raw_data
            
            # Format the data for display
            for rank in rankings:
                rank['name'] = rank['username']  # Use username as name
                
            logger.info(f"Formatted {len(rankings)} entries for display")
            
        return render_template('leaderboard.html', rankings=rankings, selected_college=selected_college)
    
    except Exception as e:
        logger.error(f"Exception in leaderboard route: {str(e)}")
        return render_template('leaderboard.html', rankings=[], selected_college=selected_college)

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/contact')
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')

@app.route('/get_user_info')
def get_user_info():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    return jsonify({
        'username': session['user']['username'],
        'email': session['user']['email'],
        'sapId': session['user']['sap_id']
    })

@app.route('/admin/clear-data', methods=['POST'])
def clear_data():
    try:
        from supabase_client import clear_leaderboard
        response = clear_leaderboard()
        
        if 'error' in response:
            logger.error(f"Error clearing data: {response['error']}")
            return jsonify({'success': False, 'error': str(response['error'])})
            
        logger.info("Successfully cleared all leaderboard data")
        return jsonify({'success': True, 'message': 'All leaderboard data has been cleared'})
        
    except Exception as e:
        logger.error(f"Exception during data clearing: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/remove-user', methods=['POST'])
def remove_inappropriate_user():
    try:
        username = request.form.get('username')
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'}), 400
            
        response = delete_user_from_leaderboard(username)
        
        if 'error' in response:
            logger.error(f"Error removing user {username}: {response['error']}")
            return jsonify({'success': False, 'error': str(response['error'])}), 500
            
        logger.info(f"Successfully removed inappropriate username: {username}")
        return jsonify({'success': True, 'message': f'User {username} has been removed from the leaderboard'})
        
    except Exception as e:
        logger.error(f"Exception during user removal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)