import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Fix unicode output for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from query_engine import handle_query

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'ipl_all_matches.csv')

def load_data():
    print("Loading IPL datasets... Please wait.")
    
    path_matches = os.path.join(BASE_DIR, 'data', 'processed', 'matches.csv')
    path_deliveries = os.path.join(BASE_DIR, 'data', 'processed', 'deliveries.csv')
    path_ipl = os.path.join(BASE_DIR, 'data', 'processed', 'ipl_all_matches.csv')
    
    dfs = {}
    
    try:
        if os.path.exists(path_matches):
            matches_df = pd.read_csv(path_matches)
            if 'date' in matches_df.columns:
                matches_df['season'] = pd.to_datetime(matches_df['date'], errors='coerce').dt.year.fillna(matches_df['season'])
                matches_df['season'] = matches_df['season'].astype(str).str.extract(r'^(\d{4})')[0]
            dfs['matches'] = matches_df
            print("✅ Loaded matches.csv")
            
        if os.path.exists(path_deliveries):
            dfs['deliveries'] = pd.read_csv(path_deliveries)
            print("✅ Loaded deliveries.csv")
            
        if os.path.exists(path_ipl):
            ipl_df = pd.read_csv(path_ipl)
            dfs['ipl'] = ipl_df
            print("✅ Loaded ipl_all_matches.csv")
            
        path_profiles = os.path.join(BASE_DIR, 'data', 'processed', 'player_profile.csv')
        if os.path.exists(path_profiles):
            dfs['profiles'] = pd.read_csv(path_profiles)
            print("✅ Loaded player_profile.csv")

        if not dfs:
            print("\nError: No datasets found in 'data/processed/' folder!")
            sys.exit(1)
            
        # Pillar 1: Mock Fitness and Net Sessions Data if missing
        path_fitness = os.path.join(BASE_DIR, 'data', 'processed', 'player_fitness_medical.csv')
        path_nets = os.path.join(BASE_DIR, 'data', 'processed', 'net_sessions_performance.csv')
        
        if 'ipl' in dfs:
            all_players = pd.concat([dfs['ipl']['striker'], dfs['ipl']['bowler']]).dropna().unique()
            import numpy as np
            
            if os.path.exists(path_fitness):
                dfs['fitness'] = pd.read_csv(path_fitness)
                print("✅ Loaded player_fitness_medical.csv")
            else:
                print("🔧 Generating mock player_fitness_medical.csv...")
                # Mock fitness data
                np.random.seed(42)
                fitness_data = []
                for p in all_players:
                    if np.random.rand() > 0.8:  # 20% chance of injury record
                        injury_date = pd.to_datetime("2023-01-01") + pd.to_timedelta(np.random.randint(0, 365), unit='D')
                        recovery_days = np.random.randint(7, 90)
                        clearance_date = injury_date + pd.to_timedelta(recovery_days, unit='D')
                        fitness_data.append({
                            'player_name': p,
                            'injury_type': np.random.choice(['Hamstring', 'Shoulder', 'Knee', 'Ankle', 'Back']),
                            'injury_date': injury_date,
                            'recovery_days': recovery_days,
                            'clearance_date': clearance_date,
                            'current_fitness_status': 'Fit'
                        })
                dfs['fitness'] = pd.DataFrame(fitness_data)
                dfs['fitness'].to_csv(path_fitness, index=False)
                
            if os.path.exists(path_nets):
                dfs['nets'] = pd.read_csv(path_nets)
                print("✅ Loaded net_sessions_performance.csv")
            else:
                print("🔧 Generating mock net_sessions_performance.csv...")
                # Mock net sessions
                nets_data = []
                for p in all_players:
                    for _ in range(np.random.randint(1, 5)):
                        nets_data.append({
                            'session_id': f"S_{np.random.randint(1000, 9999)}",
                            'player_name': p,
                            'date': pd.to_datetime("2024-01-01") + pd.to_timedelta(np.random.randint(0, 100), unit='D'),
                            'balls_faced_played': np.random.randint(20, 100),
                            'wickets_lost_taken': np.random.randint(0, 5),
                            'bowling_speed_tracked': np.random.uniform(120.0, 150.0) if np.random.rand() > 0.5 else np.nan,
                            'line_length_accuracy_pct': np.random.uniform(60.0, 95.0)
                        })
                dfs['nets'] = pd.DataFrame(nets_data)
                dfs['nets'].to_csv(path_nets, index=False)

        print("All data loaded successfully!\n")
        return dfs 
        
    except Exception as e:
        print(f"Failed to load datasets: {e}")
        sys.exit(1)


def print_welcome():
    print("=" * 60)
    print("🏏 Welcome to the IPL AI Agent 🏏")
    print("=" * 60)
    print("I can answer your questions about IPL matches.")
    print("Try asking things like:")
    print(" - 'Virat Kohli vs Kagiso Rabada'")
    print(" - 'Which match had the highest runs?'")
    print(" - 'Who are the best death overs batsmen?'")
    print(" - 'Top matches of Rohit Sharma'")
    print(" - 'Explain match 335982' (add 'hype' or 'hinglish' for fun styles)")
    print(" - 'How many sixes were hit in 2016?' (Dynamic Agent!)")
    print(" - 'What is the average first innings score?' (Dynamic Agent!)")
    print("\nType 'exit' or 'quit' to leave.")
    print("=" * 60 + "\n")

def main():
    df = load_data()
    print_welcome()
    
    while True:
        try:
            query = input("\n🤔 Ask a question: ").strip()
            if query.lower() in ['exit', 'quit']:
                print("Goodbye! Thanks for using IPL AI Agent.")
                break
                
            if not query:
                continue
                
            # Process query
            print("\n🤖 Let me check that for you...")
            response = handle_query(query, df)
            print("-" * 40)
            print(f"👉 {response}")
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
