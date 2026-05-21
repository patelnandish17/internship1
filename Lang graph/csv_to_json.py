import os
import json
import pandas as pd
from schema import PARAMETER_KEYS

def convert_csv_to_json():
    try:
        # Load CSV
        df = pd.read_csv('Internship(Supabase data).csv', encoding='latin1')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        print(f"Loaded CSV with shape: {df.shape}")
        
        # We expect 164 columns: company_id + 163 params
        if df.shape[1] != len(PARAMETER_KEYS) + 1:
            print(f"Warning: CSV has {df.shape[1]} columns, but expected {len(PARAMETER_KEYS) + 1}.")
        
        # Exclude company_id (assume it's the first column)
        data_cols = df.columns[1:]
        
        count = 0
        for idx, row in df.iterrows():
            # Get company name for filename
            company_name = str(row['name']).strip()
            
            if not company_name or company_name == 'nan':
                continue
                
            golden_record = {}
            for col_idx, col_name in enumerate(data_cols):
                # Map column index to PARAMETER_KEYS index
                if col_idx < len(PARAMETER_KEYS):
                    param_key = PARAMETER_KEYS[col_idx]
                else:
                    param_key = col_name
                    
                val = row[col_name]
                
                # Handle NaN values
                if pd.isna(val):
                    val = "Not Found"
                
                golden_record[param_key] = val
                
            # Clean company name for safe filename
            safe_name = company_name.replace(' ', '_').replace('/', '_').replace('.', '').lower()
            filename = f"{safe_name}_golden_record.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(golden_record, f, indent=4)
                
            print(f"Generated {filename}")
            count += 1
            
        print(f"Successfully generated {count} JSON files.")
        
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == '__main__':
    convert_csv_to_json()
