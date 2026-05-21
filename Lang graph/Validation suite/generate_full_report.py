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

def generate_full_report():
    # Load data and rules
    df_main = pd.read_excel("data/Consolidated_data.xlsx")
    df_rules = pd.read_csv("rules/validation_mapping.csv")
    
    # Pre-defined mapping for complex names
    manual_mapping = {
        "Year of Incorporation": "incorporation_year",
        "Market Share (%)": "market_share_percentage",
        "Customer Acquisition Cost (CAC)": "customer_acquisition_cost",
        "Customer Lifetime Value (CLV)": "customer_lifetime_value",
        "CAC:LTV Ratio": "cac_ltv_ratio",
        "Net Promoter Score (NPS)": "net_promoter_score",
        "Runway": "runway_months",
        "R&D Investment": "r_and_d_investment",
        "Total Addressable Market (TAM)": "tam",
        "Serviceable Addressable Market (SAM)": "sam",
        "Serviceable Obtainable Market (SOM)": "som",
        "Training/Development Spend": "training_spend",
        "Commute time from airport": "airport_commute_time",
        "Industry Benchmark Technology Adoption Rating": "tech_adoption_rating"
    }
    
    # Helper to find column name in data based on rule name
    def find_data_col(rule_name):
        if rule_name in manual_mapping:
            return manual_mapping[rule_name]
        # Try snake_case conversion
        snake = re.sub(r'[\s/–-]+', '_', rule_name).lower().strip('_')
        if snake in df_main.columns:
            return snake
        return None

    results = []
    
    # List of all columns in the data to ensure we check EVERYTHING
    all_data_cols = [c for c in df_main.columns if c not in ['company_id', 'name', 'short_name']]
    
    for _, row in df_main.iterrows():
        company_name = row.get('name', 'Unknown')
        company_id = row.get('company_id', 'N/A')
        
        # Track which columns we've already checked with specific rules
        checked_cols = set()
        
        # 1. First, check columns that have specific rules
        for rule_idx, rule_row in df_rules.iterrows():
            rule_name = rule_row['column_name']
            rule_type = rule_row['validation_type']
            
            data_col = find_data_col(rule_name)
            if data_col and data_col in df_main.columns:
                value = row[data_col]
                checked_cols.add(data_col)
                
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
                    "Company ID": company_id,
                    "Company Name": company_name,
                    "Parameter": rule_name,
                    "Database Column": data_col,
                    "Value": value,
                    "Check Type": rule_type,
                    "Status": "PASS" if passed else "FAIL"
                })
        
        # 2. Then, check all remaining columns with a "Structural" check
        remaining_cols = [c for c in all_data_cols if c not in checked_cols]
        for data_col in remaining_cols:
            value = row[data_col]
            passed = validate_structure(value)
            
            results.append({
                "Company ID": company_id,
                "Company Name": company_name,
                "Parameter": data_col.replace('_', ' ').title(),
                "Database Column": data_col,
                "Value": value,
                "Check Type": "structural",
                "Status": "PASS" if passed else "FAIL"
            })
            
    # Create CSV
    df_report = pd.DataFrame(results)
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/full_163_param_report.csv"
    df_report.to_csv(report_path, index=False)
    
    print(f"Full Report generated at: {report_path}")
    print(f"Total parameters checked per company: {len(results) // len(df_main)}")
    print(f"Total checks performed: {len(results)}")
    print(f"Passed: {len(df_report[df_report['Status'] == 'PASS'])}")
    print(f"Failed: {len(df_report[df_report['Status'] == 'FAIL'])}")

if __name__ == "__main__":
    generate_full_report()
