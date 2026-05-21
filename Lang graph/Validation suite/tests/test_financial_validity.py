from validators.financial_validator import validate_positive

def test_financial(data):
    for _, row in data.iterrows():

        if row["column_name"] in [
            "Annual Revenues",
            "Annual Profits",
            "Company Valuation",
            "Employee Size",
            "Total Capital Raised"
        ]:

            result = validate_positive(row["Input Data"])

            if "PASS" in str(row["Expected Result"]).upper():
                assert result, f"Financial validation failed for company: {row.get('company', 'Unknown')}, field: {row['column_name']}, value: {row['Input Data']}"
            else:
                assert not result