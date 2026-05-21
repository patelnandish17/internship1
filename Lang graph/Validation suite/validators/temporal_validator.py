import re
from datetime import datetime

def validate_temporal(value):
    try:
        # Find any 4-digit year in the string
        match = re.search(r"\b(19|20)\d{2}\b", str(value))
        if match:
            year = int(match.group(0))
            return year <= datetime.now().year + 1 # Allow one year in future for projections
        
        # If no year found, but it's a descriptive string, allow it
        val_str = str(value).strip()
        if len(val_str) > 0:
            return True
        return False
    except:
        return False