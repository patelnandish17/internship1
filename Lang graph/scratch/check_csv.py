import pandas as pd
try:
    df = pd.read_csv('Internship(Supabase data).csv', encoding='latin1')
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    print("Null count in overview_text:", df['overview_text'].isnull().sum())
    print("Sample overview:", df['overview_text'].head(2).tolist())
except Exception as e:
    print("Error:", e)
