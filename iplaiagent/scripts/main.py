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
    print("Loading all 3 IPL datasets... Please wait.")
    
    # Teeno files ke paths
    path_matches = os.path.join(BASE_DIR, 'data', 'processed', 'matches.csv')
    path_deliveries = os.path.join(BASE_DIR, 'data', 'processed', 'deliveries.csv')
    path_ipl = os.path.join(BASE_DIR, 'data', 'processed', 'ipl_all_matches.csv')

    dfs = []
    
    try:
        if os.path.exists(path_matches):
            matches_df = pd.read_csv(path_matches)
            # Standardize the season column by extracting the year from the date
            if 'date' in matches_df.columns:
                matches_df['season'] = pd.to_datetime(matches_df['date'], errors='coerce').dt.year.fillna(matches_df['season'])
                matches_df['season'] = matches_df['season'].astype(str).str.extract(r'^(\d{4})')[0]
            dfs.append(matches_df)
            print("✅ Loaded matches.csv (contains season/dates)")
            
        if os.path.exists(path_deliveries):
            dfs.append(pd.read_csv(path_deliveries))
            print("✅ Loaded deliveries.csv")
            
        if os.path.exists(path_ipl):
            dfs.append(pd.read_csv(path_ipl))
            print("✅ Loaded ipl_all_matches.csv")
            
        if not dfs:
            print("\nError: Koi dataset nahi mila 'data/processed/' folder me!")
            sys.exit(1)
            
        print("All data loaded successfully!\n")
        return dfs # Ab ye single DataFrame nahi, list of DataFrames dega
        
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
