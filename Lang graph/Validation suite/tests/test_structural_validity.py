from validators.structural_validator import validate_structure

def test_structural(data):
    for _, row in data.iterrows():

        result = validate_structure(row["Input Data"])

        # Structural validation is usually always expected PASS
        assert result