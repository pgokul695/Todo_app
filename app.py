from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

# --- Google Calendar API Imports ---
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
# -----------------------------------

app = Flask(__name__)

# File to store tasks
DATA_FILE = 'notifications.json'

# --- Google Calendar Setup ---
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
CALENDAR_ID = 'primary' # Use 'primary' for your main calendar

def get_calendar_service():
    """Shows user credentials for local access, handles token refresh, and returns the service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expired, attempting refresh...")
            creds.refresh(Request())
        else:
            print("\n--- FIRST TIME SETUP ---")
            print("Please follow the instructions in your browser to authorize access to your calendar.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            
            # Using 'localhost' is the standard for desktop app flow
            # When running for the first time, this will start a browser window.
            creds = flow.run_local_server(port=0) 
            print("Authorization successful!")
            
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    return build('calendar', 'v3', credentials=creds)

# Initialize service globally (or lazily in the route)
# We initialize it here, it will trigger the authorization flow on first run.
try:
    calendar_service = get_calendar_service()
    print("Google Calendar Service loaded successfully.")
except FileNotFoundError:
    print(f"\nFATAL ERROR: Please ensure '{CREDENTIALS_FILE}' is in the root directory and contains your Google OAuth client secret.")
    calendar_service = None
except Exception as e:
    print(f"An error occurred during Calendar service initialization: {e}")
    calendar_service = None

# --- Standard Task API Functions (Keep these the same) ---

def load_notifications():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                content = f.read()
                return json.loads(content) if content else []
        except json.JSONDecodeError:
            print(f"Warning: {DATA_FILE} is corrupted.")
            return []
    return []

def save_notifications(notifications):
    with open(DATA_FILE, 'w') as f:
        json.dump(notifications, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    return jsonify(load_notifications())

@app.route('/api/notifications', methods=['POST'])
def add_notification():
    data = request.json
    notifications = load_notifications()
    new_id = datetime.now().timestamp()
    
    notification = {
        'id': new_id, 
        'text': data.get('text'),
        'priority': data.get('priority', 'normal'),
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    
    notifications.append(notification)
    save_notifications(notifications)
    return jsonify(notification), 201

@app.route('/api/notifications/<float:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    data = request.json
    notifications = load_notifications()
    
    for notification in notifications:
        if abs(notification['id'] - notification_id) < 1e-6:
            if 'completed' in data:
                notification['completed'] = data['completed']
            if 'text' in data:
                notification['text'] = data['text']
            if 'priority' in data:
                notification['priority'] = data['priority']
                
            save_notifications(notifications)
            return jsonify(notification)
    
    return jsonify({'error': 'Notification not found'}), 404

@app.route('/api/notifications/<float:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    notifications = load_notifications()
    notifications = [n for n in notifications if abs(n['id'] - notification_id) > 1e-6]
    save_notifications(notifications)
    return jsonify({'success': True})

# --- LIVE Google Calendar Event API Route (Using Service) ---

@app.route('/api/calendar_events', methods=['GET'])
def get_calendar_events():
    """Fetches real events from the user's primary Google Calendar."""
    if not calendar_service:
        return jsonify([])

    try:
        now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        # Get events for the next 24 hours
        time_max = (datetime.utcnow() + timedelta(hours=24)).isoformat() + 'Z' 
        
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=now,
            timeMax=time_max,
            maxResults=10, # Limit to 10 events
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format the event data for the frontend
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Simple handling for all-day events vs time-based events
            is_all_day = 'date' in event['start'] and 'dateTime' not in event['start']
            
            if is_all_day:
                # Format as an all-day event
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'location': event.get('location', 'All Day'),
                    'start_time': start,
                    'end_time': 'All Day',
                })
            else:
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'location': event.get('location', 'No Location'),
                    'start_time': start,
                    'end_time': end,
                })

        return jsonify(formatted_events)

    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    # Ensure you have moved index.html into a 'templates' folder for Flask
    # and placed your client_secret.json in the project root.
    app.run(debug=True, host='0.0.0.0', port=5000)
