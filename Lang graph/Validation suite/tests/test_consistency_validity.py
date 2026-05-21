from validators.consistency_validator import validate_percentage, validate_range

def test_consistency(data):
    for _, row in data.iterrows():

        if row["column_name"] in ["Employee Turnover", "Market Share (%)", "Churn Rate"]:
            result = validate_percentage(row["Input Data"])

        elif row["column_name"] == "Net Promoter Score (NPS)":
            result = validate_range(row["Input Data"])

        else:
            continue

        if "PASS" in str(row["Expected Result"]).upper():
            assert result
        else:
            assert not result