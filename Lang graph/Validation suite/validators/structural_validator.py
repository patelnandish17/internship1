# Validators
import re

def validate_structure(value):
    """
    Basic structural checks:
    - Not empty
    - Allow most standard text and symbols for real data
    """
    if value is None or str(value).strip() == "":
        return False
        
    val_upper = str(value).upper()
    if any(word in val_upper for word in ["NOT FOUND", "UNKNOWN", "N/A", "TBD", "STEALTH", "PRIVATE"]):
        return True

    # If it's not empty, it passes structure check for consolidated data
    return True 