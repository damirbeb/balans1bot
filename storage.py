import json

USERS_FILE = "users.json"

def save_user(telegram_id, full_name, bin_number=None, phone_number=None):
    print("[DEBUG] save_user() вызван")

    try:
        with open(USERS_FILE, "r") as f:
            content = f.read().strip()
            users = json.loads(content) if content else {}
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    users[str(telegram_id)] = {
        "name": full_name,
        "bin": bin_number,
        "phone": phone_number
    }

    print("[DEBUG] Сохраняем в файл:", users)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)
        print("[DEBUG] Данные записаны.")

def get_user_data(telegram_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            return users.get(str(telegram_id))
    except FileNotFoundError:
        return None

def user_is_authenticated(telegram_id):
    user = get_user_data(telegram_id)
    return user and (user.get("phone") or user.get("bin"))

def remove_user(telegram_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        if str(telegram_id) in users:
            del users[str(telegram_id)]
            with open(USERS_FILE, "w") as f:
                json.dump(users, f, indent=4)
            return True
    except FileNotFoundError:
        pass
    return False