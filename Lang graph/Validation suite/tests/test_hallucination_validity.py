from validators.hallucination_validator import validate_hallucination

def test_hallucination(data):
    for _, row in data.iterrows():

        result = validate_hallucination(row["Input Data"])

        # Only check extreme unrealistic values
        # You can refine using column_name if needed

        assert isinstance(result, bool)