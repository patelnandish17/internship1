import pandas as pd
import os
import re
from validators.completeness_validator import validate_not_null
from validators.consistency_validator import validate_percentage, validate_range
from validators.financial_validator import validate_positive
from validators.format_validator import validate_rating, validate_ratio_100, validate_ratio_format
from validators.hallucination_validator import validate_hallucination
from validators.structural_validator import validate_structure
from validators.temporal_validator import validate_temporal

def clean_text(text):
    if not isinstance(text, str):
        return text
    # Remove emojis and special symbols while keeping common accented characters
    # This regex removes most emojis/pictographs
    cleaned = re.sub(r'[^\x00-\x7F\u00C0-\u017F]+', '', text)
    # Replace multiple spaces and newlines with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_report():
    # Load data and rules
    import os
    testcases_file = "data/testcases_PES.xlsx"
    consolidated_file = "data/Consolidated_data.xlsx"
    df_rules = pd.read_csv("rules/validation_mapping.csv")
    
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

    results = []

    if os.path.exists(testcases_file):
        xl = pd.ExcelFile(testcases_file)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(testcases_file, sheet_name=sheet_name)
            for _, row in df.iterrows():
                rule_name = row.get('column_name')
                value = row.get('Input Data')
                expected = row.get('Expected Result', 'PASS')
                company = row.get('company', sheet_name)
                
                if not rule_name or pd.isna(rule_name):
                    continue
                
                rule_type = df_rules[df_rules['column_name'] == rule_name]['validation_type'].values[0] if rule_name in df_rules['column_name'].values else "structural"
                
                passed = False
                if rule_type == 'temporal': passed = validate_temporal(value)
                elif rule_type == 'positive': passed = validate_positive(value)
                elif rule_type == 'percentage': passed = validate_percentage(value)
                elif rule_type == 'range': passed = validate_range(value)
                elif rule_type == 'rating_10': passed = validate_rating(value, 10)
                elif rule_type == 'rating_5': passed = validate_rating(value, 5)
                elif rule_type == 'ratio_100': passed = validate_ratio_100(value)
                elif rule_type == 'ratio_format': passed = validate_ratio_format(value)
                else: passed = validate_structure(value)

                results.append({
                    "Company Name": clean_text(company),
                    "Sheet": clean_text(sheet_name),
                    "Column": clean_text(rule_name),
                    "Value": clean_text(value),
                    "Validation Type": rule_type,
                    "Status": "PASS" if passed else "FAIL",
                    "Expected": clean_text(expected)
                })
        
        # If we found data in testcases, we return early
        if results:
            df_report = pd.DataFrame(results)
            os.makedirs("reports", exist_ok=True)
            report_path = "reports/validation_report.csv"
            df_report.to_csv(report_path, index=False)
            print(f"Report generated at: {report_path}")
            print(f"Total rows: {len(df_report)}")
            print(f"Passed: {len(df_report[df_report['Status'] == 'PASS'])}")
            print(f"Failed: {len(df_report[df_report['Status'] == 'FAIL'])}")
            return

    # Fallback to consolidated data
    try:
        df_main = pd.read_excel(consolidated_file)
    except FileNotFoundError:
        print("No data found to validate.")
        return
    
    for _, row in df_main.iterrows():
        company_name = row.get('name', 'Unknown')
        company_id = row.get('company_id', 'N/A')
        
        for rule_name, data_col in mapping.items():
            if data_col not in df_main.columns:
                continue
                
            value = row[data_col]
            rule_type = df_rules[df_rules['column_name'] == rule_name]['validation_type'].values[0] if rule_name in df_rules['column_name'].values else "structural"
            
            # Apply validator
            passed = False
            if rule_type == 'temporal': passed = validate_temporal(value)
            elif rule_type == 'positive': passed = validate_positive(value)
            elif rule_type == 'percentage': passed = validate_percentage(value)
            elif rule_type == 'range': passed = validate_range(value)
            elif rule_type == 'rating_10': passed = validate_rating(value, 10)
            elif rule_type == 'rating_5': passed = validate_rating(value, 5)
            elif rule_type == 'ratio_100': passed = validate_ratio_100(value)
            elif rule_type == 'ratio_format': passed = validate_ratio_format(value)
            elif rule_type == 'structural': passed = validate_structure(value)
            else: passed = validate_structure(value)
            
            results.append({
                "Company ID": company_id,
                "Company Name": clean_text(company_name),
                "Column": clean_text(rule_name),
                "Value": clean_text(value),
                "Validation Type": rule_type,
                "Status": "PASS" if passed else "FAIL"
            })
            
    # Create CSV
    df_report = pd.DataFrame(results)
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/validation_report.csv"
    df_report.to_csv(report_path, index=False)
    print(f"Report generated at: {report_path}")
    print(f"Total rows: {len(df_report)}")
    print(f"Passed: {len(df_report[df_report['Status'] == 'PASS'])}")
    print(f"Failed: {len(df_report[df_report['Status'] == 'FAIL'])}")

if __name__ == "__main__":
    generate_report()
