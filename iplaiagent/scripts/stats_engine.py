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

def get_fitness_impact(query: str, dfs: dict):
    """
    Evaluates performance vectors post-injury (Pillar 1).
    """
    if 'fitness' not in dfs or 'ipl' not in dfs or 'matches' not in dfs:
        return "Missing required datasets for fitness impact analysis."
        
    import re
    # Extract player name from query like "How did Virat Kohli perform after injury?"
    # We will just try to resolve names from the query against the player list.
    all_players = pd.concat([dfs['ipl']['striker'], dfs['ipl']['bowler']]).dropna().unique()
    
    player_found = None
    for p in all_players:
        if str(p).lower() in query.lower():
            player_found = p
            break
            
    if not player_found:
        return "Could not identify a player in your query for fitness analysis."
        
    fitness_df = dfs['fitness']
    player_fitness = fitness_df[fitness_df['player_name'] == player_found]
    
    if player_fitness.empty:
        return f"No injury records found for {player_found}."
        
    injury_record = player_fitness.iloc[0]
    injury_date = pd.to_datetime(injury_record['injury_date'])
    clearance_date = pd.to_datetime(injury_record['clearance_date'])
    
    # Merge matches to get dates in IPL data
    matches_df = dfs['matches'][['id', 'date']].copy()
    matches_df.rename(columns={'id': 'match_id'}, inplace=True)
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')
    
    ipl_df = dfs['ipl'].merge(matches_df, on='match_id', how='left')
    ipl_df.dropna(subset=['date'], inplace=True)
    
    # Slicing
    before_df = ipl_df[ipl_df['date'] < injury_date]
    after_df = ipl_df[ipl_df['date'] >= clearance_date]
    
    output = f"### 🏥 Player Fitness Impact: {player_found} `[Simulated Vector]`\n"
    output += f"- **Injury Type:** {injury_record['injury_type']}\n"
    output += f"- **Injury Date:** {injury_date.strftime('%Y-%m-%d')}\n"
    output += f"- **Clearance Date:** {clearance_date.strftime('%Y-%m-%d')}\n\n"
    
    # Batting Stats
    b_before = before_df[before_df['striker'] == player_found]
    b_after = after_df[after_df['striker'] == player_found]
    
    if not b_before.empty or not b_after.empty:
        output += "#### 🏏 Batting Impact\n"
        runs_b = b_before['runs_off_bat'].sum() if not b_before.empty else 0
        balls_b = len(b_before)
        sr_b = (runs_b / balls_b * 100) if balls_b > 0 else 0
        
        runs_a = b_after['runs_off_bat'].sum() if not b_after.empty else 0
        balls_a = len(b_after)
        sr_a = (runs_a / balls_a * 100) if balls_a > 0 else 0
        
        bat_data = {
            "Phase": ["Before Injury", "After Clearance"],
            "Runs": [runs_b, runs_a],
            "Balls": [balls_b, balls_a],
            "Strike Rate": [f"{sr_b:.1f}", f"{sr_a:.1f}"]
        }
        output += pd.DataFrame(bat_data).to_markdown(index=False) + "\n\n"
        
    # Bowling Stats
    bw_before = before_df[before_df['bowler'] == player_found]
    bw_after = after_df[after_df['bowler'] == player_found]
    
    if not bw_before.empty or not bw_after.empty:
        output += "#### 🎯 Bowling Impact\n"
        runs_b = bw_before['total_runs'].sum() if not bw_before.empty else 0
        balls_b = len(bw_before)
        wkt_b = bw_before['is_wicket'].sum() if not bw_before.empty else 0
        econ_b = (runs_b / (balls_b / 6)) if balls_b > 0 else 0
        
        runs_a = bw_after['total_runs'].sum() if not bw_after.empty else 0
        balls_a = len(bw_after)
        wkt_a = bw_after['is_wicket'].sum() if not bw_after.empty else 0
        econ_a = (runs_a / (balls_a / 6)) if balls_a > 0 else 0
        
        bowl_data = {
            "Phase": ["Before Injury", "After Clearance"],
            "Wickets": [wkt_b, wkt_a],
            "Economy": [f"{econ_b:.2f}", f"{econ_a:.2f}"]
        }
        output += pd.DataFrame(bowl_data).to_markdown(index=False) + "\n\n"
        
    return output
