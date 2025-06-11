import pandas as pd

def dedupe(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    before = len(df)
    df_clean = df.drop_duplicates(subset=['email'])
    after = len(df_clean)
    df_clean.to_csv(output_csv, index=False)
    print(f"Dropped {before-after} duplicates; {after} unique leads remain.")

if __name__ == "__main__":
    dedupe("demo_data/raw_leads.csv", "demo_data/clean_leads.csv")
