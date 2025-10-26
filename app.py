from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import timedelta
from supabase_client import insert_score, get_leaderboard
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'svkm-typing-test-2025-secret-key')  # Use environment variable with fallback
app.permanent_session_lifetime = timedelta(days=7)

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    sap_id = request.form.get('sap-id')

    if not email or not sap_id:
        error_msg = "Email and SAP ID are required."
        return render_template('login.html', error=error_msg)

    # Since we're not using a users table, we'll just store the login info in session
    session['user'] = {
        'email': email,
        'sap_id': sap_id,
        'username': email.split('@')[0]  # Use email prefix as username
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

    if not all([wpm, accuracy]):
        logger.error(f"Missing required data - WPM: {wpm}, Accuracy: {accuracy}")
        return jsonify({'success': False, 'error': 'Missing required data'})

    try:
        # Insert score directly using the simplified function
        response = insert_score(
            username=session['user']['username'],
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
    
    try:
        logger.info("Fetching leaderboard data")
        response = get_leaderboard(limit=50)
        
        if 'error' in response:
            logger.error(f"Error fetching leaderboard: {response['error']}")
            rankings = []
        else:
            raw_data = response.data if hasattr(response, 'data') else response
            logger.info(f"Raw leaderboard data: {raw_data}")
            
            # Format the data for the template
            rankings = []
            for entry in raw_data:
                formatted_entry = {
                    'name': entry.get('username', 'Anonymous'),  # Use username as name
                    'college': entry.get('college', 'Unknown'),  # Default to Unknown if not present
                    'best_wpm': float(entry.get('wpm', 0)),  # Convert to float
                    'avg_accuracy': float(entry.get('accuracy', 0)),  # Convert to float
                    'tests_taken': 1  # Default to 1 since we're showing individual scores
                }
                rankings.append(formatted_entry)
                
            logger.info(f"Formatted {len(rankings)} entries for display")
            
        return render_template('leaderboard.html', rankings=rankings)
    
    except Exception as e:
        logger.error(f"Exception in leaderboard route: {str(e)}")
        return render_template('leaderboard.html', rankings=[])

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

if __name__ == '__main__':
    app.run(debug=True)