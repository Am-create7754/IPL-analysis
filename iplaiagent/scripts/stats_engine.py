import pandas as pd

def resolve_player_name(df, name_query):
    name_query = name_query.strip().lower()
    if 'bowler' in df.columns:
        all_players = pd.concat([df['striker'], df['bowler']]).dropna().unique()
    else:
        all_players = df['striker'].dropna().unique()
    
    # 1. Exact match
    for p in all_players:
        if str(p).lower() == name_query:
            return str(p)
            
    # 2. Initials + Surname match (e.g., 'Virat Kohli' -> 'V Kohli')
    parts = name_query.split()
    if len(parts) > 1:
        first_initial = parts[0][0].lower()
        surname = parts[-1].lower()
        for p in all_players:
            p_str = str(p).lower()
            p_parts = p_str.split()
            if len(p_parts) > 1:
                if surname == p_parts[-1] and p_parts[0].startswith(first_initial):
                    return str(p)
                    
    # 3. Fallback: substring
    for p in all_players:
        if name_query in str(p).lower() or str(p).lower() in name_query:
            return str(p)
            
    return name_query


def get_top_batsmen(df, min_balls=50):
    """
    Returns top batsmen by total runs.
    Filters noise using min_balls.
    """
    stats = df.groupby('striker').agg(
        runs=('runs_off_bat', 'sum'),
        balls=('ball', 'count')
    ).reset_index()
    
    filtered_stats = stats[stats['balls'] >= min_balls]
    top_batsmen = filtered_stats.sort_values(by='runs', ascending=False)
    return top_batsmen

def get_strike_rates(df, min_balls=50):
    """
    Returns players sorted by strike rate.
    """
    stats = df.groupby('striker').agg(
        runs=('runs_off_bat', 'sum'),
        balls=('ball', 'count')
    ).reset_index()
    
    filtered_stats = stats[stats['balls'] >= min_balls].copy()
    filtered_stats['strike_rate'] = (filtered_stats['runs'] / filtered_stats['balls']) * 100
    top_sr = filtered_stats.sort_values(by='strike_rate', ascending=False)
    return top_sr

def get_best_death_overs_batsmen(df, min_balls=20):
    """
    Returns best death overs (overs >= 16) batsmen by strike rate.
    """
    if 'over' not in df.columns:
        df['over'] = df['ball'].astype(int)
        
    death_df = df[df['over'] >= 16]
    
    stats = death_df.groupby('striker').agg(
        runs=('runs_off_bat', 'sum'),
        balls=('ball', 'count')
    ).reset_index()
    
    filtered_stats = stats[stats['balls'] >= min_balls].copy()
    filtered_stats['strike_rate'] = (filtered_stats['runs'] / filtered_stats['balls']) * 100
    top_death_batsmen = filtered_stats.sort_values(by='strike_rate', ascending=False)
    return top_death_batsmen

def get_player_matchup(df, batter, bowler):
    """
    Returns matchup stats between a batter and bowler.
    """
    resolved_batter = resolve_player_name(df, batter)
    resolved_bowler = resolve_player_name(df, bowler)
    
    matchup_df = df[(df['striker'] == resolved_batter) & 
                    (df['bowler'] == resolved_bowler)]
                    
    if matchup_df.empty:
        return None
        
    runs = matchup_df['runs_off_bat'].sum()
    balls = len(matchup_df)
    
    # Check dismissals
    # Sometimes 'player_dismissed' might be NA/NaN when no one is dismissed
    dismissals = matchup_df['player_dismissed'].notna().sum()
    
    return {
        'batter': resolved_batter,
        'bowler': resolved_bowler,
        'runs': runs,
        'balls': balls,
        'dismissals': dismissals
    }
