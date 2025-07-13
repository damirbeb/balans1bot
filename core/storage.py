import json
import os

USERS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "users.json"))

def save_user(telegram_id, full_name, bin_number=None, phone_number=None):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            users = json.loads(content) if content else {}
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    users[str(telegram_id)] = {
        "name": full_name,
        "bin": bin_number,
        "phone": phone_number
    }

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def get_user_data(telegram_id):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return None
            users = json.loads(content)
            return users.get(str(telegram_id))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def user_is_authenticated(telegram_id):
    user = get_user_data(telegram_id)
    return user and (user.get("phone") or user.get("bin"))

def remove_user(telegram_id):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        if str(telegram_id) in users:
            del users[str(telegram_id)]
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            return True
    except FileNotFoundError:
        pass
    return False
