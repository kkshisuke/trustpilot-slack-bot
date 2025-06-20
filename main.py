import os
from flask import Flask, request, jsonify
import requests
import anthropic
import re

app = Flask(__name__)

# Configuration
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/slack/events', methods=['POST'])
def slack_events():
    if 'challenge' in request.json:
        return jsonify({'challenge': request.json['challenge']})

    event = request.json.get('event', {})
    if event.get('type') == 'app_mention':
        handle_mention(event)

    return '', 200

def handle_mention(event):
    channel = event['channel']
    text = event.get('text', '')
    ts = event.get('ts')

    # Extraire le texte après la mention du bot
    bot_id = '<@U092216TFKQ>'  # Remplace par l'ID de ton bot
    if bot_id in text:
        # Enlever la mention du bot pour garder que l'avis
        review_text = text.replace(bot_id, '').strip()

        if review_text:
            # Générer la réponse
            try:
                message = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    temperature=0.7,
                    system="""Tu es Dominique de ZEDE Paris. 
                        Réponds aux avis Trustpilot de manière personnalisée:
                        - Le nom du client est sur la première ligne
                        - Mentionne les détails spécifiques du produit
                        - 3-4 lignes maximum
                        - Signe 'Dominique - ZEDE Paris'
                        IMPORTANT: Utilise EXACTEMENT le nom et les détails fournis dans l'avis.""",
                    messages=[
                        {"role": "user", "content": f"Réponds à cet avis:\n\n{review_text}"}
                    ]
                )

                response_text = message.content[0].text

                # Extraire la référence si elle existe
                ref_match = re.search(r'#ZEDE\d+', review_text)
                if ref_match:
                    response_text = f"**Commande {ref_match.group(0)}**\n\n{response_text}"

                # Poster la réponse
                post_message(channel, response_text, ts)

            except Exception as e:
                post_message(channel, f"Erreur: {str(e)}", ts)
        else:
            post_message(channel, 
                "**Mode d'emploi:**\n" +
                "Copiez l'avis Trustpilot et collez-le après ma mention.\n\n" +
                "**Exemple:**\n" +
                "@ReviewBot Andries\n" +
                "Je suis très heureuse de mon nouveau sac gris...\n" +
                "#ZEDE39020", 
                ts)

def post_message(channel, text, thread_ts=None):
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    data = {
        'channel': channel,
        'text': text
    }
    if thread_ts:
        data['thread_ts'] = thread_ts

    requests.post(
        'https://slack.com/api/chat.postMessage',
        headers=headers,
        json=data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)