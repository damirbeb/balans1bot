import re

def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+77\d{9}", phone))

def is_valid_bin(bin_code: str) -> bool:
    return bool(re.fullmatch(r"\d{12}", bin_code))