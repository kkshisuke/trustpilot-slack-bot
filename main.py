import os
from flask import Flask, request, jsonify
import requests
import anthropic
import re
import traceback  # Add this import

app = Flask(__name__)

# Configuration
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Add error checking
if not SLACK_BOT_TOKEN:
    print("ERROR: SLACK_BOT_TOKEN not found!")
if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found!")

try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("Anthropic client initialized successfully")
except Exception as e:
    print(f"ERROR initializing Anthropic client: {e}")
    client = None

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/slack/events', methods=['POST'])
def slack_events():
    try:
        print(f"Received request: {request.json}")  
        
        if 'challenge' in request.json:
            return jsonify({'challenge': request.json['challenge']})
        
        event = request.json.get('event', {})
        print(f"Event type: {event.get('type')}")
        
        if event.get('type') == 'app_mention':
            handle_mention(event)
        
        return '', 200
    except Exception as e:
        print(f"ERROR in slack_events: {str(e)}")
        traceback.print_exc()
        return '', 200  # Return 200 even on error to prevent Slack retries
