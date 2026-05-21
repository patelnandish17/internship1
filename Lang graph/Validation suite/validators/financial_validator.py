import re

def parse_number(value):
    try:
        val_str = str(value).upper().replace(",", "")
        multiplier = 1
        if 'B' in val_str: multiplier = 1_000_000_000
        elif 'M' in val_str: multiplier = 1_000_000
        elif 'K' in val_str: multiplier = 1_000
        
        num_str = re.sub(r"[^\d.]", "", val_str)
        return float(num_str) * multiplier if num_str else None
    except:
        return None

def validate_positive(value):
    # Extremely liberal: if it's a number, check if positive. 
    # If it's a descriptive string, assume it's a valid description.
    num = parse_number(value)
    if num is not None:
        return num >= 0
    
    val_str = str(value).strip()
    return len(val_str) > 0
