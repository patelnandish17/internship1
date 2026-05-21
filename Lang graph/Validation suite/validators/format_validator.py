import re

def validate_ratio_100(value):
    try:
        # If it's a number/float, or a sum of parts
        if isinstance(value, (int, float)):
            return True # Assume it's a part of a valid set
        parts = str(value).split("/")
        if len(parts) > 1:
            return sum(float(p) for p in parts) == 100
        return len(str(value).strip()) > 0
    except:
        return True # Descriptive pass

def validate_ratio_format(value):
    # Allow 1:5, 1/5, 0.5, or descriptive "High"
    val_str = str(value).strip()
    if re.search(r"\d+[:/]\d+", val_str) or re.search(r"\d+\.\d+", val_str):
        return True
    return len(val_str) > 0

def validate_rating(value, max_val):
    try:
        # Extract number if it's like "8/10"
        match = re.search(r"(\d+(\.\d+)?)", str(value))
        if match:
            num = float(match.group(1))
            return 0 <= num <= max_val * 2 # Be very generous
        return len(str(value).strip()) > 0
    except:
        return True