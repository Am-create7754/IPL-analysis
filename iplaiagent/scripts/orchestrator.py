import pandas as pd
import re
from stats_engine import resolve_player_name
from simulation_engine import get_matchup_probabilities

def extract_player_name(query, dfs):
    """
    Attempts to find player names in the query.
    Checks profiles, ipl, fitness, and nets datasets.
    """
    query_lower = query.lower()
    
    all_players = set()
    
    if 'profiles' in dfs:
        all_players.update(dfs['profiles']['name'].dropna().unique())
        all_players.update(dfs['profiles']['unique_name'].dropna().unique())
    
    if 'ipl' in dfs:
        all_players.update(dfs['ipl']['striker'].dropna().unique())
        all_players.update(dfs['ipl']['bowler'].dropna().unique())
        
    if 'fitness' in dfs:
        all_players.update(dfs['fitness']['player_name'].dropna().unique())
        
    if 'nets' in dfs:
        all_players.update(dfs['nets']['player_name'].dropna().unique())
        
    sorted_players = sorted([str(p) for p in all_players if str(p).strip()], key=len, reverse=True)
    
    found_players = []
    
    for p_str in sorted_players:
        if len(p_str) < 4: continue
        pattern = r'\b' + re.escape(p_str.lower()) + r'\b'
        if re.search(pattern, query_lower):
            found_players.append(p_str)
            query_lower = re.sub(pattern, "", query_lower)
            
    for p_str in sorted_players:
        if p_str in found_players: continue
        parts = p_str.split()
        if len(parts) > 1:
            last_name = parts[-1].lower()
            if len(last_name) >= 4:
                pattern = r'\b' + re.escape(last_name) + r'\b'
                if re.search(pattern, query_lower):
                    found_players.append(p_str)
                    query_lower = re.sub(pattern, "", query_lower)
                    
        if len(parts) > 1:
            first_name = parts[0].lower()
            if len(first_name) >= 5:
                pattern = r'\b' + re.escape(first_name) + r'\b'
                if re.search(pattern, query_lower):
                    found_players.append(p_str)
                    query_lower = re.sub(pattern, "", query_lower)
                        
    return found_players

def get_stats_baseline(player, dfs):
    if 'ipl' not in dfs: return None
    df = dfs['ipl']
    resolved = resolve_player_name(df, player)
    
    b_df = df[df['striker'] == resolved]
    runs = int(b_df['runs_off_bat'].sum()) if not b_df.empty else 0
    balls = len(b_df)
    sr = (runs / balls * 100) if balls > 0 else 0
    
    bw_df = df[df['bowler'] == resolved]
    wkt = int(bw_df['is_wicket'].sum()) if not bw_df.empty else 0
    bw_runs = int(bw_df['total_runs'].sum()) if not bw_df.empty else 0
    bw_balls = len(bw_df)
    econ = (bw_runs / (bw_balls / 6)) if bw_balls > 0 else 0
    
    if balls == 0 and bw_balls == 0:
        return None
        
    return {'runs': runs, 'sr': sr, 'wickets': wkt, 'econ': econ, 'resolved_name': resolved}

def get_fitness_status(player, dfs):
    if 'fitness' not in dfs: return None
    df = dfs['fitness']
    match = df[df['player_name'].str.contains(player, case=False, na=False)]
    if match.empty:
        parts = player.split()
        if len(parts) > 1:
            match = df[df['player_name'].str.contains(parts[-1], case=False, na=False)]
    if not match.empty:
        return match.iloc[0].to_dict()
    return None
    
def get_net_trends(player, dfs):
    if 'nets' not in dfs: return None
    df = dfs['nets']
    match = df[df['player_name'].str.contains(player, case=False, na=False)]
    if match.empty:
        parts = player.split()
        if len(parts) > 1:
            match = df[df['player_name'].str.contains(parts[-1], case=False, na=False)]
    if not match.empty:
        match = match.sort_values(by='date', ascending=False).head(5)
        return {
            'avg_speed': match['bowling_speed_tracked'].mean(),
            'avg_acc': match['line_length_accuracy_pct'].mean(),
            'balls_faced': int(match['balls_faced_played'].sum()),
            'recent_sessions': len(match)
        }
    return None

def generate_fitness_text(player, dfs):
    fitness = get_fitness_status(player, dfs)
    if not fitness:
        return "- No active injury flags found.\n"
    status = fitness.get('current_fitness_status', 'Unknown')
    out = f"- **Status:** {status}\n"
    out += f"- **Issue:** {fitness.get('injury_type', 'N/A')} ({fitness.get('recovery_days', 'N/A')} days)\n"
    if status == 'In Rehab':
        out += "- **Risk:** High physical risk. Not match-ready.\n"
    else:
        out += "- **Risk:** Cleared. Workload management required.\n"
    return out

def generate_nets_text(player, dfs):
    nets = get_net_trends(player, dfs)
    if not nets:
        return "- Low-Data Profile. No biometric net tracking available.\n"
    out = f"- **Volume:** {nets['balls_faced']} balls across {nets['recent_sessions']} sessions.\n"
    if pd.notna(nets['avg_speed']) and nets['avg_speed'] > 0:
        out += f"- **Pace:** Stabilized at ~{nets['avg_speed']:.1f} km/h.\n"
    if pd.notna(nets['avg_acc']):
        out += f"- **Control:** Line/Length accuracy at {nets['avg_acc']:.1f}%.\n"
    return out

def generate_history_text(player, dfs):
    stats = get_stats_baseline(player, dfs)
    if not stats:
        return "- No significant historical baseline stats found.\n"
    out = ""
    if stats['runs'] > 0:
        out += f"- **Batting:** {stats['runs']} runs @ {stats['sr']:.1f} SR.\n"
    if stats['wickets'] > 0:
        out += f"- **Bowling:** {stats['wickets']} wickets @ {stats['econ']:.2f} Econ.\n"
    return out

def run_orchestrator(query, dfs):
    players = extract_player_name(query, dfs)
    if not players:
        return None
        
    is_matchup = len(players) > 1
    
    if is_matchup:
        title = f"{players[0].upper()} VS {players[1].upper()}"
    else:
        title = f"{players[0].upper()}"
        
    output = f"## 🏏 EXECUTIVE INTELLIGENCE REPORT: {title}\n\n"
    
    # 1. FITNESS CHECK
    output += f"### 🚨 PLAYER STATUS & FITNESS IMPACT FLAG\n"
    for p in players[:2]:
        if is_matchup: output += f"**{p.upper()}**\n"
        output += generate_fitness_text(p, dfs)
    output += "\n"
        
    # 2. NET TRACKING
    output += f"### 📈 NET SESSION FORM TRENDS\n"
    for p in players[:2]:
        if is_matchup: output += f"**{p.upper()}**\n"
        output += generate_nets_text(p, dfs)
    output += "\n"
        
    # 3. PREDICTIVE SIMULATION
    output += f"### 🎯 MATCHUP SIMULATION PROFILE\n"
    if is_matchup and 'ipl' in dfs:
        probs, err = get_matchup_probabilities(dfs['ipl'], players[0], players[1])
        if probs:
            output += f"- **Tactical Matchup:** {players[0]} vs {players[1]}\n"
            output += f"- **Win Probability Matrix:** Dot Ball ({probs['Dot %']:.1f}%), Rotation ({probs['Run 1-3 %']:.1f}%), Boundary ({probs['Boundary %']:.1f}%), Wicket ({probs['Wicket %']:.1f}%)\n"
            output += f"- **Assessment:** Based on {probs['source'].lower()}, this vector highlights the core tactical advantage.\n\n"
        else:
            output += f"- Insufficient direct matchup data against {players[1]} for a high-confidence simulation.\n\n"
    else:
        output += "- **Profile Index:** Player shows dynamic performance probability against standard archetypes.\n"
        output += "- **Next Appearance:** High probability of executing primary role metrics based on current form.\n\n"
        
    # 4. HISTORICAL BASELINE CONTEXT
    output += f"### 📊 HISTORICAL BASELINE CONTEXT\n"
    for p in players[:2]:
        if is_matchup: output += f"**{p.upper()}**\n"
        output += generate_history_text(p, dfs)
    output += "\n"
        
    return output
