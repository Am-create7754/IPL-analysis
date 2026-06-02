import pandas as pd
import re

def compute_phase(df):
    """Adds 'phase' column based on the over number if it doesn't exist."""
    if 'phase' not in df.columns and 'over' in df.columns:
        df['phase'] = pd.cut(df['over'], bins=[-1, 5, 14, 20], labels=['Powerplay', 'Middle', 'Death'])
    return df

def merge_player_profiles(df_balls, df_profiles):
    """Merges bowler_type and bat_style from player_profiles."""
    if df_profiles is not None and not df_profiles.empty:
        # Merge bowler style
        if 'bowler_type' not in df_balls.columns:
            bowler_map = df_profiles.set_index('unique_name')['bowl_style'].to_dict()
            df_balls['bowler_type'] = df_balls['bowler'].map(bowler_map)
        
        # Merge bat style
        if 'bat_style' not in df_balls.columns:
            batter_map = df_profiles.set_index('unique_name')['bat_style'].to_dict()
            df_balls['bat_style'] = df_balls['striker'].map(batter_map)
    return df_balls

def parse_and_execute_situational_query(query: str, dfs: dict):
    """
    Parses a query for situational slicing.
    Example: 'Show stats for Death phase, Left-Arm Pace in Inning 2'
    Returns a Markdown table.
    """
    if 'ipl' not in dfs:
        return "Core IPL dataset not found for situational slicing."
        
    df = dfs['ipl'].copy()
    df = compute_phase(df)
    if 'profiles' in dfs:
        df = merge_player_profiles(df, dfs['profiles'])
    
    q_lower = query.lower()
    
    # Extracting filters
    phase = None
    if 'powerplay' in q_lower: phase = 'Powerplay'
    elif 'middle' in q_lower: phase = 'Middle'
    elif 'death' in q_lower: phase = 'Death'
    
    inning = None
    if 'inning 1' in q_lower or '1st inning' in q_lower: inning = 1
    elif 'inning 2' in q_lower or '2nd inning' in q_lower: inning = 2
    
    bowler_type = None
    # Very basic parsing for bowler type in query (could be improved)
    if 'pace' in q_lower or 'fast' in q_lower or 'medium' in q_lower or 'spin' in q_lower or 'orthodox' in q_lower or 'legbreak' in q_lower:
        # Check all unique bowler types to see if they are in the query
        if 'bowler_type' in df.columns:
            types = df['bowler_type'].dropna().unique()
            for bt in types:
                clean_bt = str(bt).strip()
                if clean_bt and clean_bt.lower() in q_lower:
                    bowler_type = bt
                    break
    
    # Build mask
    mask = pd.Series([True] * len(df))
    filters_applied = []
    
    if phase:
        mask = mask & (df['phase'] == phase)
        filters_applied.append(f"Phase = {phase}")
    
    if inning:
        mask = mask & (df['inning'] == inning)
        filters_applied.append(f"Inning = {inning}")
        
    if bowler_type:
        mask = mask & (df['bowler_type'] == bowler_type)
        filters_applied.append(f"Bowler Type = {bowler_type}")
        
    if not filters_applied:
        return None # Not a clear situational query, let the LLM handle it
        
    sliced_df = df[mask]
    
    if sliced_df.empty:
        return f"### Situational Analysis\n\nNo data found for filters: {', '.join(filters_applied)}."
        
    # Compute rollups
    # Top 5 Strikers in this situation
    top_strikers = sliced_df.groupby('striker').agg(
        runs=('runs_off_bat', 'sum'),
        balls=('ball', 'count')
    )
    top_strikers['strike_rate'] = (top_strikers['runs'] / top_strikers['balls']) * 100
    top_strikers = top_strikers[top_strikers['balls'] >= 10].sort_values(by='strike_rate', ascending=False).head(5)
    
    # Top 5 Bowlers in this situation
    top_bowlers = sliced_df.groupby('bowler').agg(
        runs_conceded=('total_runs', 'sum'),
        balls=('ball', 'count'),
        wickets=('is_wicket', 'sum')
    )
    # Exclude wide/noball from balls for economy, but for simplicity we'll just do a basic one
    top_bowlers['economy'] = (top_bowlers['runs_conceded'] / (top_bowlers['balls'] / 6)).round(2)
    top_bowlers = top_bowlers[top_bowlers['balls'] >= 12].sort_values(by='economy').head(5)
    
    # Format output
    output = f"### 📊 Situational Analysis\n**Filters Applied:** {', '.join(filters_applied)}\n\n"
    
    output += "#### 🔥 Top Strikers (Min 10 balls)\n"
    if not top_strikers.empty:
        output += top_strikers.reset_index().to_markdown(index=False, floatfmt=".1f") + "\n\n"
    else:
        output += "No batters met the threshold.\n\n"
        
    output += "#### 🎯 Top Bowlers (Min 12 balls)\n"
    if not top_bowlers.empty:
        output += top_bowlers.reset_index().to_markdown(index=False, floatfmt=".2f") + "\n\n"
    else:
        output += "No bowlers met the threshold.\n\n"
        
    return output
