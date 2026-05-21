from validators.completeness_validator import validate_not_null

def test_completeness(data):
    for _, row in data.iterrows():

        result = validate_not_null(row["Input Data"])

        if "PASS" in str(row["Expected Result"]).upper():
            assert result
        else:
            assert not result