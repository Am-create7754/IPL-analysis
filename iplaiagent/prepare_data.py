import pandas as pd

print("Preparing data by renaming columns in deliveries.csv to match the app's expectations...")
df = pd.read_csv('data/processed/deliveries.csv')

# Rename columns to match what the scripts expect
df = df.rename(columns={
    'batter': 'striker',
    'batsman_runs': 'runs_off_bat',
    'extra_runs': 'extras'
})

df.to_csv('data/processed/ipl_all_matches.csv', index=False)
print("Data preparation complete! File saved to data/processed/ipl_all_matches.csv.")
