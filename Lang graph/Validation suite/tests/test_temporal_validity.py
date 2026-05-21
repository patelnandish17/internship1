from validators.temporal_validator import validate_temporal

def test_temporal(data):
    for _, row in data.iterrows():
        if row["column_name"] == "Year of Incorporation":

            result = validate_temporal(row["Input Data"])

            if "PASS" in str(row["Expected Result"]).upper():
                assert result
            else:
                assert not result