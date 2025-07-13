import re

def is_valid_phone(phone: str) -> bool:
    phone = phone.strip().replace(" ", "")

    if phone.startswith("77") and not phone.startswith("+"):
        phone = "+" + phone

    return bool(re.fullmatch(r"\+77\d{9}", phone))

def is_valid_bin(bin_code: str) -> bool:
    return bool(re.fullmatch(r"\d{12}", bin_code))
