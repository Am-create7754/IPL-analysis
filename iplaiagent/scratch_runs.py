import pandas as pd

matches = pd.read_csv(r"c:\Users\amber\OneDrive\Desktop\IPL analysis\iplaiagent\data\processed\matches.csv")
deliveries = pd.read_csv(r"c:\Users\amber\OneDrive\Desktop\IPL analysis\iplaiagent\data\processed\deliveries.csv")

# Filter matches for season 2020/21
m_2020 = matches[matches['season'] == '2020/21']
match_ids = m_2020['id'].tolist()

# Filter deliveries for those match ids
d_2020 = deliveries[deliveries['match_id'].isin(match_ids)]

total_runs = d_2020['total_runs'].sum()
print("Total runs for 2020/21:", total_runs)

super_overs = d_2020[d_2020['is_super_over'] == 1]['total_runs'].sum() if 'is_super_over' in d_2020.columns else 0
print("Super over runs:", super_overs)
print("Runs excluding super overs:", total_runs - super_overs)

