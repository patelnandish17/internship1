# Validators
def validate_not_null(value):
    return value is not None and str(value).strip() != ""