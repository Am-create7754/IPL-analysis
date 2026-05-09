import pandas as pd

def get_turning_point(match_df):
    """
    Analyzes a specific match to find the turning point over.
    Impact Score = runs in the over + (wickets in the over * 20)
    Returns a dictionary with the most impactful over details.
    """
    if 'over' not in match_df.columns:
        match_df['over'] = match_df['ball'].astype(int)
        
    # We want to group by innings as well, if available. For simplicity, just over if only 1 innings
    # assuming we just group by over across the match. To be precise, group by 'over' and maybe 'inning' if it exists.
    # We will assume 'inning' exists or we just group by ball's integer part
    group_cols = ['over']
    if 'inning' in match_df.columns:
        group_cols = ['inning', 'over']
        
    over_stats = match_df.groupby(group_cols).agg(
        runs=('runs_off_bat', 'sum'),
        # Count non-null player_dismissed as wickets
        wickets=('player_dismissed', lambda x: x.notna().sum())
    ).reset_index()
    
    over_stats['impact_score'] = over_stats['runs'] + (over_stats['wickets'] * 20)
    
    if over_stats.empty:
        return None
        
    # Get the row with the maximum impact score
    turning_over = over_stats.loc[over_stats['impact_score'].idxmax()]
    
    return turning_over.to_dict()
