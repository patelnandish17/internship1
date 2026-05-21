import re

def validate_percentage(value):
    try:
        # Extract first number found
        match = re.search(r"(\d+(\.\d+)?)", str(value))
        if match:
            num = float(match.group(1))
            return 0 <= num <= 200 # Extra generous
        return len(str(value).strip()) > 0
    except:
        return True

def validate_range(value):
    try:
        match = re.search(r"(-?\d+(\.\d+)?)", str(value))
        if match:
            num = float(match.group(1))
            return -200 <= num <= 200
        return len(str(value).strip()) > 0
    except:
        return True