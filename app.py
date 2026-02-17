from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application Information
__author__ = "Denis Mulatya Mutua"
__project__ = "Electrical Fault Diagnosis System"
__year__ = "2026"
__institution__ = "Moi University"
__degree__ = "BSc Electrical & Electronics Engineering"
__graduation_date__ = "December 18, 2025"
__email__ = "denismutua970@gmail.com"
__phone__ = "0700516898"
__version__ = "1.0"

app = Flask(__name__)
app.config['DATABASE'] = 'faults.db'
app.config['SECRET_KEY'] = 'electrical-fault-diagnosis-secret-key-2026'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@electricalfaultdiagnosis.com')

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Serializer for generating activation tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# User Model
class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    """Load user from database."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['email'], user['username'])
    return None
MODEL_PATH = 'fault_model.pkl'
SCALER_PATH = 'scaler.pkl'

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema."""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        is_activated INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Check if is_activated column exists, if not add it
    c.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in c.fetchall()]
    if 'is_activated' not in user_columns:
        c.execute('ALTER TABLE users ADD COLUMN is_activated INTEGER DEFAULT 0')
    
    # Diagnoses table
    c.execute('''CREATE TABLE IF NOT EXISTS diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_id TEXT NOT NULL,
        fault_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        sensor_readings TEXT,
        recommendation TEXT
    )''')
    
    # Check if user_id column exists, if not add it
    c.execute("PRAGMA table_info(diagnoses)")
    diag_columns = [col[1] for col in c.fetchall()]
    if 'user_id' not in diag_columns:
        c.execute('ALTER TABLE diagnoses ADD COLUMN user_id INTEGER')
    
    conn.commit()
    conn.close()

def init_model():
    """Load or create a simple ML model for fault diagnosis."""
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    else:
        # Generate synthetic training data for demo
        np.random.seed(42)
        n_samples = 500
        
        # Features: voltage, current, temperature, vibration, power_factor
        X = np.random.randn(n_samples, 5) * 10 + np.array([230, 50, 60, 5, 0.9])
        
        # Fault labels: 0=Normal, 1=Overheat, 2=Overload, 3=Short Circuit
        y = np.random.choice([0, 1, 2, 3], n_samples)
        
        # Train model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Save model and scaler
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
    
    return model, scaler

# Load model on startup
model, scaler = init_model()
init_db()

# Email Helper Functions
def send_activation_email(user_email, user_name, activation_url):
    """Send account activation email."""
    try:
        print(f"[EMAIL] Attempting to send activation email to {user_email}")
        subject = "Activate Your Electrical Fault Diagnosis Account"
        body = f"""
        Hello {user_name},

        Thank you for registering with Electrical Fault Diagnosis System!

        To activate your account, please click the link below:
        {activation_url}

        This link will expire in 24 hours.

        If you did not create this account, please ignore this email.

        Best regards,
        Electrical Fault Diagnosis Team
        """
        
        msg = Message(subject=subject, recipients=[user_email], body=body)
        mail.send(msg)
        print(f"[EMAIL] Activation email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send activation email to {user_email}: {str(e)}")
        print(f"[EMAIL CONFIG] Server: {app.config.get('MAIL_SERVER')}, Port: {app.config.get('MAIL_PORT')}")
        print(f"[EMAIL CONFIG] Username: {app.config.get('MAIL_USERNAME')}")
        return False

def send_diagnosis_report_email(user_email, user_name, diagnosis_data, report_html):
    """Send fault diagnosis report email."""
    try:
        print(f"[EMAIL] Attempting to send diagnosis report to {user_email}")
        subject = f"Fault Diagnosis Report - {diagnosis_data['fault_type']} Detected"
        body = f"""
        Hello {user_name},

        A fault diagnosis has been completed for device {diagnosis_data['device_id']}.

        Fault Type: {diagnosis_data['fault_type']}
        Confidence: {diagnosis_data['confidence']}%
        Timestamp: {diagnosis_data['timestamp']}

        Sensor Readings:
        - Voltage: {diagnosis_data['readings']['voltage']} V
        - Current: {diagnosis_data['readings']['current']} A
        - Temperature: {diagnosis_data['readings']['temperature']} °C
        - Vibration: {diagnosis_data['readings']['vibration']} mm/s
        - Power Factor: {diagnosis_data['readings']['power_factor']}

        Recommendation:
        {diagnosis_data['recommendation']}

        Please log in to your account to view the detailed report and mitigation steps.

        Best regards,
        Electrical Fault Diagnosis Team
        """
        
        msg = Message(subject=subject, recipients=[user_email], body=body, html=report_html)
        mail.send(msg)
        print(f"[EMAIL] Diagnosis report email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send diagnosis report to {user_email}: {str(e)}")
        return False

FAULT_TYPES = {
    0: "Normal Operation",
    1: "Overheat",
    2: "Overload",
    3: "Short Circuit"
}

RECOMMENDATIONS = {
    0: "System operating normally. Continue monitoring.",
    1: "Reduce load or improve cooling. Check ventilation.",
    2: "Reduce load immediately. Inspect circuit breaker.",
    3: "EMERGENCY: Shut down immediately. Check for faults."
}

# Authentication Routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            password_confirm = data.get('password_confirm', '')
            
            # Validation
            if not email or not username or not password:
                return jsonify({'status': 'error', 'message': 'All fields required'}), 400
            
            if password != password_confirm:
                return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
            
            if len(password) < 6:
                return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
            
            # Check if email exists
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            if c.fetchone():
                conn.close()
                return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
            
            # Create user (not activated yet)
            password_hash = generate_password_hash(password)
            c.execute('INSERT INTO users (email, username, password_hash, is_activated) VALUES (?, ?, ?, ?)',
                     (email, username, password_hash, 0))
            conn.commit()
            
            # Get the user ID
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_id = c.fetchone()['id']
            conn.close()
            
            # Generate activation token
            activation_token = serializer.dumps(user_id, salt='email-confirm-salt')
            activation_url = url_for('activate_account', token=activation_token, _external=True)
            
            # Send activation email
            email_sent = send_activation_email(email, username, activation_url)
            
            # Return response
            response_data = {
                'status': 'success', 
                'activation_url': activation_url
            }
            
            if email_sent:
                response_data['message'] = 'Account created! Please check your email to activate your account.'
            else:
                response_data['message'] = 'Account created! Click the link below to activate your account.'
                response_data['email_failed'] = True
            
            return jsonify(response_data), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'status': 'error', 'message': 'Email and password required'}), 400
            
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            user_row = c.fetchone()
            conn.close()
            
            if not user_row:
                return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401
            
            if not check_password_hash(user_row['password_hash'], password):
                return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401
            
            if not user_row['is_activated']:
                return jsonify({'status': 'error', 'message': 'Please activate your account using the link sent to your email'}), 403
            
            user = User(user_row['id'], user_row['email'], user_row['username'])
            login_user(user, remember=True)
            
            return jsonify({'status': 'success', 'message': 'Login successful', 'redirect': '/'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('login.html')

@app.route('/activate/<token>')
def activate_account(token):
    """Activate user account from email link."""
    try:
        user_id = serializer.loads(token, salt='email-confirm-salt', max_age=3600*24)  # 24 hour expiry
        
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE users SET is_activated = 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return render_template('activation_success.html')
    except Exception as e:
        return render_template('activation_failed.html', error=str(e))

@app.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip()
            
            if not email:
                return jsonify({'status': 'error', 'message': 'Email is required'}), 400
            
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT id, username FROM users WHERE email = ?', (email,))
            user_row = c.fetchone()
            conn.close()
            
            if not user_row:
                # Don't reveal if email exists or not (security best practice)
                return jsonify({'status': 'success', 'message': 'If an account exists with this email, a reset link has been sent'}), 200
            
            # Generate password reset token
            reset_token = serializer.dumps(user_row['id'], salt='password-reset-salt')
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            
            # Try to send reset email
            email_sent = False
            try:
                msg = Message(
                    subject='Reset Your Password - Electrical Fault Diagnosis System',
                    recipients=[email],
                    html=f'''
                    <html>
                        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                            <div style="max-width: 500px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h2 style="color: #333; text-align: center;">⚡ Password Reset Request</h2>
                                <p style="color: #666; line-height: 1.6;">Hello <strong>{user_row['username']}</strong>,</p>
                                <p style="color: #666; line-height: 1.6;">You requested to reset your password. Click the button below to create a new password:</p>
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                                </div>
                                <p style="color: #999; font-size: 12px;">Or copy and paste this link in your browser:</p>
                                <p style="color: #999; font-size: 12px; word-break: break-all;">{reset_url}</p>
                                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                                <p style="color: #999; font-size: 12px;">This link will expire in 24 hours. If you did not request a password reset, please ignore this email.</p>
                                <p style="color: #999; font-size: 12px;">Best regards,<br>Electrical Fault Diagnosis System</p>
                            </div>
                        </body>
                    </html>
                    '''
                )
                mail.send(msg)
                email_sent = True
                print(f"[EMAIL] Password reset link sent to {email}")
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send password reset to {email}: {str(e)}")
            
            # Return success response (no reset_url for security - email-only delivery)
            return jsonify({
                'status': 'success',
                'message': 'If an account exists with this email, check your inbox for a password reset link.'
            }), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset."""
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=3600*24)  # 24 hour expiry
    except Exception as e:
        return render_template('activation_failed.html', error='Invalid or expired reset link')
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            password = data.get('password', '')
            
            if not password:
                return jsonify({'status': 'error', 'message': 'Password is required'}), 400
            
            if len(password) < 6:
                return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
            
            # Update password
            password_hash = generate_password_hash(password)
            conn = get_db()
            c = conn.cursor()
            c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            conn.commit()
            conn.close()
            
            return jsonify({'status': 'success', 'message': 'Password reset successfully'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('reset_password.html')

@app.route('/')
def index():
    """Render home page."""
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/api/diagnose', methods=['POST'])
@login_required
def diagnose():
    """Diagnose electrical fault from sensor readings."""
    try:
        data = request.json
        device_id = data.get('device_id', 'Unknown')
        
        # Extract sensor readings
        voltage = float(data.get('voltage', 230))
        current = float(data.get('current', 50))
        temperature = float(data.get('temperature', 60))
        vibration = float(data.get('vibration', 5))
        power_factor = float(data.get('power_factor', 0.9))
        
        # Prepare features for prediction
        features = np.array([[voltage, current, temperature, vibration, power_factor]])
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        confidence = model.predict_proba(features_scaled)[0][prediction]
        
        fault_type = FAULT_TYPES[prediction]
        recommendation = RECOMMENDATIONS[prediction]
        
        # Store in database with user_id
        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO diagnoses 
                     (user_id, device_id, fault_type, confidence, sensor_readings, recommendation)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (current_user.id, device_id, fault_type, confidence, 
                   f"V:{voltage}, I:{current}, T:{temperature}, Vib:{vibration}, PF:{power_factor}",
                   recommendation))
        conn.commit()
        conn.close()
        
        # Prepare diagnosis data
        diagnosis_data = {
            'device_id': device_id,
            'fault_type': fault_type,
            'confidence': round(confidence * 100, 2),
            'recommendation': recommendation,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'readings': {
                'voltage': voltage,
                'current': current,
                'temperature': temperature,
                'vibration': vibration,
                'power_factor': power_factor
            }
        }
        
        # Generate HTML report for email
        report_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Electrical Fault Diagnosis Report</h2>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Device ID:</strong> {device_id}</p>
                    <p><strong>Diagnosis Time:</strong> {diagnosis_data['timestamp']}</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h3 style="margin-top: 0; color: #856404;">Fault Detected</h3>
                    <p style="font-size: 1.2em; color: #c33;"><strong>{fault_type}</strong></p>
                    <p><strong>Confidence Level:</strong> {diagnosis_data['confidence']}%</p>
                </div>
                
                <h3>Sensor Readings</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Voltage</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{voltage} V</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Current</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{current} A</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Temperature</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{temperature} °C</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Vibration</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{vibration} mm/s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Power Factor</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{power_factor}</td>
                    </tr>
                </table>
                
                <h3 style="margin-top: 30px;">Mitigation & Recommendations</h3>
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;">
                    <p>{recommendation}</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666;">
                    <p>For more details and to view all your diagnosis reports, please log in to your account at:</p>
                    <p>{url_for('index', _external=True)}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send diagnosis report email
        send_diagnosis_report_email(current_user.email, current_user.username, diagnosis_data, report_html)
        
        return jsonify({
            'status': 'success',
            'device_id': device_id,
            'fault_type': fault_type,
            'confidence': round(confidence * 100, 2),
            'recommendation': recommendation,
            'readings': {
                'voltage': voltage,
                'current': current,
                'temperature': temperature,
                'vibration': vibration,
                'power_factor': power_factor
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/history', methods=['GET'])
@login_required
def history():
    """Get diagnosis history for current user."""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM diagnoses WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20', (current_user.id,))
        rows = c.fetchall()
        conn.close()
        
        diagnoses = [dict(row) for row in rows]
        return jsonify({'status': 'success', 'diagnoses': diagnoses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
@login_required
def stats():
    """Get diagnostic statistics for current user."""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Total diagnoses for this user
        c.execute('SELECT COUNT(*) as total FROM diagnoses WHERE user_id = ?', (current_user.id,))
        total = c.fetchone()['total']
        
        # Breakdown by fault type
        c.execute('''SELECT fault_type, COUNT(*) as count 
                     FROM diagnoses WHERE user_id = ?
                     GROUP BY fault_type''', (current_user.id,))
        breakdown = {row['fault_type']: row['count'] for row in c.fetchall()}
        
        # Average confidence
        c.execute('SELECT AVG(confidence) as avg_conf FROM diagnoses WHERE user_id = ?', (current_user.id,))
        avg_conf = c.fetchone()['avg_conf'] or 0
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'total_diagnoses': total,
            'fault_breakdown': breakdown,
            'avg_confidence': round(avg_conf * 100, 2)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/result')
def result():
    """Render result page."""
    return render_template('result.html')

@app.route('/about')
def about():
    """About the developer and system."""
    return render_template('about.html', author=__author__, email=__email__, phone=__phone__, institution=__institution__)

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    """Get current user information."""
    return jsonify({
        'status': 'success',
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
