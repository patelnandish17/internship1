from validators.format_validator import validate_ratio_100, validate_ratio_format, validate_rating

def test_format(data):
    for _, row in data.iterrows():

        if row["column_name"] == "Revenue Mix":
            result = validate_ratio_100(row["Input Data"])

        elif row["column_name"] == "CAC:LTV Ratio":
            result = validate_ratio_format(row["Input Data"])

        elif row["column_name"] == "Website Rating":
            result = validate_rating(row["Input Data"], 10)

        elif row["column_name"] in ["Glassdoor Rating", "Indeed Rating", "Google Reviews Rating"]:
            result = validate_rating(row["Input Data"], 5)

        else:
            continue

        if "PASS" in str(row["Expected Result"]).upper():
            assert result
        else:
            assert not result