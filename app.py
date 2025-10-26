from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from datetime import timedelta
from supabase_client import insert_score, get_leaderboard

app = Flask(__name__)
# Use a stable secret key from environment variable or a fixed value for development
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-dev-secret-key-123')  
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    duration = data.get('duration_seconds', 60)  # Default to 60 seconds if not provided

    try:
        # Insert score directly using the simplified function
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

@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        print("No user in session, redirecting to login")  # Debug log
        return redirect(url_for('login'))
    
    try:
        print(f"Fetching leaderboard for user: {session['user']['username']}")  # Debug log
        response = get_leaderboard(limit=50)  # Get top 50 scores
        
        if isinstance(response, dict) and 'error' in response:
            print(f"Error fetching leaderboard: {response['error']}")  # Debug log
            rankings = []
        else:
            rankings = response.data if hasattr(response, 'data') else response
            print(f"Successfully fetched {len(rankings)} leaderboard entries")  # Debug log
            
        return render_template('leaderboard.html', rankings=rankings)
    
    except Exception as e:
        print(f"Exception in leaderboard route: {str(e)}")  # Debug log
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