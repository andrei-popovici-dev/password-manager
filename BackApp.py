import json
import os

# Path to your JSON file
DATA_FILE = 'data.json'

# Ensure the JSON file exists with the correct structure
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"accounts": []}, f, indent=4)

def load_data():
    """Load all data from JSON file."""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Save the data dictionary back to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_account(username, password):
    """
    Add a new account to the JSON file.
    Returns True if added, False if username already exists.
    """
    data = load_data()

    # Check if user already exists
    for acc in data["accounts"]:
        if acc["username"] == username:
            return False  # Username taken

    # Add new account
    data["accounts"].append({
        "username": username,
        "password": password,
        "credentials": []
    })

    save_data(data)
    return True

def get_account(username):
    """Return the account dictionary for a given username, or None."""
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            return acc
    return None

# Example usage:
if __name__ == "__main__":
    username = "user1"
    password = "mypassword"

    if add_account(username, password):
        print(f"Account '{username}' added successfully!")
    else:
        print(f"Username '{username}' already exists.")
