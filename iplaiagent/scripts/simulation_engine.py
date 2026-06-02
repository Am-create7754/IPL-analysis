import pandas as pd
import re
from stats_engine import resolve_player_name
from situational_engine import compute_phase, merge_player_profiles

def get_matchup_probabilities(df, batter, bowler):
    """
    Computes joint probability distributions for a given batter vs bowler matchup.
    Categories: [Dot %, Run 1-3 %, Boundary %, Wicket %]
    """
    resolved_batter = resolve_player_name(df, batter)
    resolved_bowler = resolve_player_name(df, bowler)
    
    matchup_df = df[(df['striker'] == resolved_batter) & (df['bowler'] == resolved_bowler)]
    
    if matchup_df.empty:
        # Fallback to general stats if they haven't faced each other
        batter_df = df[df['striker'] == resolved_batter]
        bowler_df = df[df['bowler'] == resolved_bowler]
        if batter_df.empty or bowler_df.empty:
            return None, "Not enough historical data for this simulation."
            
        # Combine base probabilities (simple average of batter's historical and bowler's historical)
        b_total = len(batter_df)
        b_dots = len(batter_df[batter_df['runs_off_bat'] == 0]) / b_total
        b_runs = len(batter_df[batter_df['runs_off_bat'].isin([1,2,3])]) / b_total
        b_bounds = len(batter_df[batter_df['runs_off_bat'].isin([4,6])]) / b_total
        b_wkt = batter_df['is_wicket'].sum() / b_total
        
        bw_total = len(bowler_df)
        bw_dots = len(bowler_df[bowler_df['runs_off_bat'] == 0]) / bw_total
        bw_runs = len(bowler_df[bowler_df['runs_off_bat'].isin([1,2,3])]) / bw_total
        bw_bounds = len(bowler_df[bowler_df['runs_off_bat'].isin([4,6])]) / bw_total
        bw_wkt = bowler_df['is_wicket'].sum() / bw_total
        
        prob_dots = (b_dots + bw_dots) / 2
        prob_runs = (b_runs + bw_runs) / 2
        prob_bounds = (b_bounds + bw_bounds) / 2
        prob_wkt = (b_wkt + bw_wkt) / 2
        source = "Fallback: General Career Stats"
        
    else:
        total = len(matchup_df)
        prob_dots = len(matchup_df[matchup_df['runs_off_bat'] == 0]) / total
        prob_runs = len(matchup_df[matchup_df['runs_off_bat'].isin([1,2,3])]) / total
        prob_bounds = len(matchup_df[matchup_df['runs_off_bat'].isin([4,6])]) / total
        prob_wkt = matchup_df['is_wicket'].sum() / total
        source = "Direct Head-to-Head History"
        
    # Normalize
    total_prob = prob_dots + prob_runs + prob_bounds + prob_wkt
    if total_prob > 0:
        prob_dots /= total_prob
        prob_runs /= total_prob
        prob_bounds /= total_prob
        prob_wkt /= total_prob
        
    return {
        'Dot %': prob_dots * 100,
        'Run 1-3 %': prob_runs * 100,
        'Boundary %': prob_bounds * 100,
        'Wicket %': prob_wkt * 100,
        'batter': resolved_batter,
        'bowler': resolved_bowler,
        'source': source
    }, None

def handle_simulation_query(query: str, dfs: dict):
    """
    Intercepts '!simulate' queries.
    Format: !simulate Virat Kohli vs Jasprit Bumrah
    """
    if 'ipl' not in dfs:
        return "Core IPL dataset not found."
        
    df = dfs['ipl'].copy()
    df = compute_phase(df)
    if 'profiles' in dfs:
        df = merge_player_profiles(df, dfs['profiles'])
        
    # Regex to extract players
    match = re.search(r'!simulate\s+(.*?)\s+vs\s+(.*)', query, re.IGNORECASE)
    if not match:
        return "Invalid simulation format. Use: `!simulate [Batsman] vs [Bowler]`"
        
    batter_raw = match.group(1).strip()
    bowler_raw = match.group(2).strip()
    
    probs, err = get_matchup_probabilities(df, batter_raw, bowler_raw)
    if err:
        return f"### 🎲 Simulation Failed\n{err}"
        
    # Format output as Markdown
    output = f"### 🎲 Matchup Simulation Vector\n"
    output += f"**{probs['batter']}** ⚔️ **{probs['bowler']}**\n\n"
    
    output += f"*(Data Source: {probs['source']})*\n\n"
    
    # State-Space Matrix
    table_data = {
        "Next Ball Outcome": ["Dot Ball (0 runs)", "Rotation (1-3 runs)", "Boundary (4 or 6)", "Dismissal (Wicket)"],
        "Probability": [f"{probs['Dot %']:.1f}%", f"{probs['Run 1-3 %']:.1f}%", f"{probs['Boundary %']:.1f}%", f"{probs['Wicket %']:.1f}%"]
    }
    
    result_df = pd.DataFrame(table_data)
    output += result_df.to_markdown(index=False) + "\n\n"
    
    # Generate True Economy/Strike Rate info context
    # Let's calculate True Strike Rate for batter
    batter_df = df[df['striker'] == probs['batter']]
    if not batter_df.empty:
        # Simplified: True SR = Batter SR - Phase Average SR
        # For simplicity, just get overall SR for the batter here to augment output
        runs = batter_df['runs_off_bat'].sum()
        balls = len(batter_df)
        sr = (runs / balls) * 100 if balls > 0 else 0
        output += f"**{probs['batter']} Overall SR:** {sr:.1f}\n"
        
    return output
