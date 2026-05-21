# Validators
import re

def parse_number(value):
    try:
        value = str(value).replace(",", "")
        value = re.sub(r"[^\d.]", "", value)
        return float(value)
    except:
        return None


def validate_hallucination(value):
    """
    Detect unrealistic / extreme values
    """

    num = parse_number(value)

    if num is None:
        return True  # ignore non-numeric cases

    # Example thresholds (you can adjust)
    if num > 1_000_000_000_000:  # very high
        return False

    if num < 0:
        return False

    return True