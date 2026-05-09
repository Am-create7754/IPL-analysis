import pandas as pd
from turning_point_engine import get_turning_point

def get_match_context(df, match_id):
    """
    Returns the context of a specific match.
    """
    # Assuming match_id might be numeric or string, handle accordingly
    # Convert match_id parameter to same type as df['match_id']
    match_df = df[df['match_id'].astype(str) == str(match_id)].copy()
    
    if match_df.empty:
        return None
        
    total_runs = match_df['runs_off_bat'].sum() + match_df.get('extras', 0).sum() if 'extras' in match_df.columns else match_df['runs_off_bat'].sum()
    
    # Calculate top batter
    batter_stats = match_df.groupby('striker').agg(runs=('runs_off_bat', 'sum')).reset_index()
    top_batter_row = batter_stats.loc[batter_stats['runs'].idxmax()]
    top_batter = top_batter_row['striker']
    top_runs = top_batter_row['runs']
    
    # Get turning point
    turning_over_info = get_turning_point(match_df)
    
    return {
        "match_id": match_id,
        "top_batter": top_batter,
        "top_runs": int(top_runs),
        "total_runs": int(total_runs),
        "turning_over": turning_over_info
    }
