from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from datetime import timedelta
from supabase_client import insert_score, get_leaderboard
import logging

app = Flask(__name__)
# Use environment variable for secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-dev-secret-key-123')

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

@app.before_request
def make_session_permanent():
    session.permanent = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    session['user'] = {
        'email': email,
        'sap_id': sap_id,
        'username': email.split('@')[0]
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
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    duration = data.get('duration_seconds', 60)

    try:
        response = insert_score(
            username=session['user']['username'],
            wpm=wpm,
            accuracy=accuracy,
            duration_seconds=duration
        )
        
        if 'error' in response:
            return jsonify({'success': False, 'error': response['error']})
            
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_score', methods=['POST'])
def save_score():
    try:
        if 'user' not in session:
            logger.warning("Attempt to save score without user session")
            return jsonify({"error": "No user session"}), 401

        data = request.get_json()
        username = session['user']['username']
        wpm = int(data.get('wpm', 0))
        accuracy = float(data.get('accuracy', 0))
        duration = int(data.get('duration_seconds', 60))

        logger.info(f"Saving score for user {username}: WPM={wpm}, Accuracy={accuracy}")
        result = insert_score(username, wpm, accuracy, duration)
        
        if isinstance(result, dict) and 'error' in result:
            logger.error(f"Error saving score: {result['error']}")
            return jsonify({"error": result['error']}), 500
            
        return jsonify({"message": "Score saved successfully"})
    except Exception as e:
        logger.error(f"Exception in save_score: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/leaderboard')
def leaderboard():
    try:
        if 'user' not in session:
            logger.warning("Attempt to access leaderboard without user session")
            return redirect(url_for('login'))
        
        logger.info(f"Fetching leaderboard for user: {session['user']['username']}")
        response = get_leaderboard(limit=50)
        
        if isinstance(response, dict) and 'error' in response:
            logger.error(f"Error fetching leaderboard: {response['error']}")
            return render_template('leaderboard.html', rankings=[], error=response['error'])
        
        rankings = response.data if hasattr(response, 'data') else response
        logger.info(f"Successfully fetched {len(rankings)} leaderboard entries")
        return render_template('leaderboard.html', rankings=rankings)
    
    except Exception as e:
        logger.error(f"Exception in leaderboard route: {str(e)}")
        return render_template('leaderboard.html', rankings=[], error=str(e))

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