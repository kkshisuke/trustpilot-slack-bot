def handle_mention(event):
    print(f"=== HANDLE MENTION CALLED ===")
    print(f"Full event: {event}")
    
    channel = event['channel']
    text = event.get('text', '')
    ts = event.get('ts')
    
    print(f"Channel: {channel}")
    print(f"Text: {text}")
    print(f"Bot ID: {bot_id}")
    
    # Extraire le texte après la mention du bot
    bot_id = '<@U092216TFKQ>'  # Your bot ID is correct!
    if bot_id in text:
        print("Bot ID found in text!")
        # Enlever la mention du bot pour garder que l'avis
        review_text = text.replace(bot_id, '').strip()
        print(f"Review text: {review_text}")
        
        if review_text:
            # Générer la réponse
            try:
                print("Calling Claude API...")
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
                
                print("Claude response received!")
                response_text = message.content[0].text
                print(f"Response: {response_text}")
                
                # Poster la réponse
                post_message(channel, response_text, ts)
                
            except Exception as e:
                print(f"ERROR calling Claude: {str(e)}")
                import traceback
                traceback.print_exc()
                post_message(channel, f"Erreur: {str(e)}", ts)
