import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from schema import PARAMETER_KEYS

try:
    df = pd.read_csv('Internship(Supabase data).csv', encoding='latin1')
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    
    csv_cols = df.columns.tolist()
    
    print(f"CSV has {len(csv_cols)} columns.")
    print(f"Schema has {len(PARAMETER_KEYS)} parameters.")
    
    # Check overlaps
    exact_matches = set(csv_cols).intersection(set(PARAMETER_KEYS))
    print(f"Exact matches: {len(exact_matches)}")
    
    if len(exact_matches) < 10:
        print("First 10 CSV cols:", csv_cols[:10])
        print("First 10 Schema params:", PARAMETER_KEYS[:10])
except Exception as e:
    print("Error:", e)
