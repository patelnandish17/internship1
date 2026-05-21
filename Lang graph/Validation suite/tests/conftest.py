import pandas as pd
import pytest

@pytest.fixture(scope="session")
def rules():
    return pd.read_csv("rules/validation_mapping.csv")

@pytest.fixture(scope="session")
def data(rules):
    # This fixture loads the data and maps it to the format expected by the tests.
    import os
    testcases_file = "data/testcases_PES.xlsx"
    consolidated_file = "data/Consolidated_data.xlsx"

    if os.path.exists(testcases_file):
        xl = pd.ExcelFile(testcases_file)
        all_dfs = []
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(testcases_file, sheet_name=sheet_name)
            # Add sheet info for better error reporting
            df['sheet_name'] = sheet_name
            # Ensure required columns are present for the tests
            if 'company' not in df.columns:
                df['company'] = sheet_name
            if 'value' not in df.columns:
                df['value'] = df['Input Data'] if 'Input Data' in df.columns else None
            all_dfs.append(df)
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

    # Fallback to consolidated data if testcases is missing
    try:
        df_main = pd.read_excel(consolidated_file)
    except FileNotFoundError:
        return pd.DataFrame()
        
    mapping = {
        "Year of Incorporation": "incorporation_year",
        "Employee Size": "employee_size",
        "Annual Revenues": "annual_revenue",
        "Annual Profits": "annual_profit",
        "Market Share (%)": "market_share_percentage",
        "Total Capital Raised": "total_capital_raised",
        "Customer Acquisition Cost (CAC)": "customer_acquisition_cost",
        "Customer Lifetime Value (CLV)": "customer_lifetime_value",
        "CAC:LTV Ratio": "cac_ltv_ratio",
        "Churn Rate": "churn_rate",
        "Net Promoter Score (NPS)": "net_promoter_score",
        "Burn Rate": "burn_rate",
        "Runway": "runway_months",
        "Burn Multiplier": "burn_multiplier",
        "R&D Investment": "r_and_d_investment",
        "Total Addressable Market (TAM)": "tam",
        "Serviceable Addressable Market (SAM)": "sam",
        "Serviceable Obtainable Market (SOM)": "som",
        "Training/Development Spend": "training_spend",
        "Commute time from airport": "airport_commute_time",
        "Industry Benchmark Technology Adoption Rating": "tech_adoption_rating"
    }
    
    test_cases = []
    for _, row in df_main.iterrows():
        company_name = row.get('name', 'Unknown')
        for rule_col, data_col in mapping.items():
            if data_col in df_main.columns:
                val = row[data_col]
                test_cases.append({
                    "column_name": rule_col,
                    "Input Data": val,
                    "Expected Result": "PASS",
                    "value": val,
                    "company": company_name
                })
    
    return pd.DataFrame(test_cases)