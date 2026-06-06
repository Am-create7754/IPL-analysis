import streamlit as st
import os
import sys
import re
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure the scripts directory is in path so internal imports work
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(SCRIPTS_DIR)

# pyrefly: ignore [missing-import]
from main import load_data
# pyrefly: ignore [missing-import]
from query_engine import handle_query
# pyrefly: ignore [missing-import]
from stats_engine import resolve_player_name

# Page config
st.set_page_config(
    page_title="Sports Intelligence Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cyberpunk / Tactical Dark Theme
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Make top header transparent to keep sidebar toggle visible */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Glowing Titles */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
        text-shadow: 0px 0px 20px rgba(0, 210, 255, 0.4);
    }
    
    /* Tactical Cards / Containers */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background-color: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 3-Grid Specific Glowing Borders */
    .card-fitness {
        border-left: 4px solid #ef4444 !important; /* Red */
        box-shadow: -5px 0px 15px rgba(239, 68, 68, 0.15) !important;
    }
    
    .card-nets {
        border-left: 4px solid #38bdf8 !important; /* Ice Blue */
        box-shadow: -5px 0px 15px rgba(56, 189, 248, 0.15) !important;
    }
    
    .card-sim {
        border-left: 4px solid #10b981 !important; /* Emerald */
        box-shadow: -5px 0px 15px rgba(16, 185, 129, 0.15) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }
    
    /* Custom Pills */
    .pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-left: 10px;
    }
    .pill-rehab { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .pill-active { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .pill-cleared { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    
    /* Input Styling */
    .stTextInput input {
        background-color: #1e293b !important;
        border: 1px solid #3b82f6 !important;
        color: #fff !important;
        border-radius: 4px;
        font-family: monospace;
    }
    .stTextInput input:focus {
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 4px;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
        border: none;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border-radius: 4px;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------
# DATA LOADING
# -----------------
@st.cache_resource(show_spinner=False)
def init_data():
    return load_data()

with st.spinner("Initializing Command Center Protocols..."):
    df_dict = init_data()

# -----------------
# HISTORY UTILS
# -----------------
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_history.json')

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history_list):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history_list, f)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = load_history()
    
if 'active_query' not in st.session_state:
    st.session_state.active_query = None
if 'active_response' not in st.session_state:
    st.session_state.active_response = None

# -----------------
# SIDEBAR
# -----------------
with st.sidebar:
    st.markdown("### 🌍 ENVIRONMENTAL CONTROLS")
    selected_venue = st.selectbox(
        "Venue/Soil Type Filter", 
        ["All Venues", "Wankhede Red Soil", "Chepauk Black Soil", "Eden Gardens Clay"],
        key="selected_venue"
    )
    st.markdown("---")
    st.markdown("### 📋 ACTIVE ROSTER & INJURY WATCH")
    st.markdown("---")
    
    if 'fitness' in df_dict:
        # Display some key players and their status from the fitness dataset
        fitness_df = df_dict['fitness']
        for _, row in fitness_df.head(8).iterrows():
            status = row['current_fitness_status']
            if status == "In Rehab":
                pill = "<span class='pill pill-rehab'>IN REHAB</span>"
            elif pd.notna(row['clearance_date']):
                pill = "<span class='pill pill-cleared'>CLEARED</span>"
            else:
                pill = "<span class='pill pill-active'>ACTIVE</span>"
                
            st.markdown(f"<div style='margin-bottom: 0.8rem; font-size: 0.95rem;'>{row['player_name']} {pill}</div>", unsafe_allow_html=True)
    else:
        st.markdown("Roster data unavailable.")
        
    st.markdown("---")
    st.markdown("### 🗄️ MISSION ARCHIVES")
    
    # CSS for scrollable history container
    st.markdown("""
        <style>
        .history-container {
            max-height: 300px;
            overflow-y: auto;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="history-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for i, item in enumerate(reversed(st.session_state.chat_history)):
            q_text = item['query']
            # Truncate long queries
            short_q = q_text[:25] + "..." if len(q_text) > 25 else q_text
            
            if st.button(f"📄 {short_q}", key=f"hist_{i}", use_container_width=True):
                st.session_state.active_query = item['query']
                st.session_state.active_response = item['response']
                st.rerun()
    else:
        st.markdown("<p style='font-size: 0.8rem; color: #94a3b8;'>No active missions in archive.</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💾 DATA MANAGEMENT")
    if st.button("Export Session Log (CSV)", use_container_width=True):
        if st.session_state.chat_history:
            log_df = pd.DataFrame(st.session_state.chat_history)
            log_df.to_csv("session_log_export.csv", index=False)
            st.success("Session saved to 'session_log_export.csv'!")
        else:
            st.warning("No queries to save yet.")

# -----------------
# TOP SECTION
# -----------------
st.markdown("<h1 class='main-title'>⚡ SPORTS INTELLIGENCE COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-family: monospace;'>SYSTEM ONLINE // WAITING FOR TACTICAL INPUT...</p>", unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    query = st.text_input("QUERY TARGET", placeholder="Type player name: 'Bumrah' or matchup: 'simulate Bumrah vs Kohli'...", label_visibility="collapsed", key="query_input")
with col_btn:
    analyze_btn = st.button("Analyze Matrix")

# If they searched a new query, clear active and process
if analyze_btn and query:
    with st.spinner("Compiling Matrix Data..."):
        response_text = handle_query(query, df_dict)
        
    st.session_state.active_query = query
    st.session_state.active_response = response_text
    
    # Save to history if it's new
    st.session_state.chat_history.append({"query": query, "response": response_text})
    save_history(st.session_state.chat_history)
    st.rerun()

# -----------------
# PARSER UTILS
# -----------------
def parse_markdown_to_sections(md_text):
    """Parses the orchestrator markdown into logical sections."""
    sections = {
        "title": "",
        "fitness": "",
        "nets": "",
        "sim": "",
        "history": "",
        "raw": md_text
    }
    
    # Extract Title
    title_match = re.search(r'## 🏏 EXECUTIVE INTELLIGENCE REPORT: (.*?)\n', md_text)
    if title_match:
        sections['title'] = title_match.group(1).strip()
        
    # Split by ### 
    parts = md_text.split("### ")
    for part in parts:
        # The first line of 'part' is the title (e.g. "🚨 PLAYER STATUS..."), the rest is the content
        lines = part.split("\n", 1)
        if len(lines) < 2:
            continue
            
        header = lines[0]
        content = lines[1].strip()
        
        if "PLAYER STATUS & FITNESS IMPACT FLAG" in header:
            sections['fitness'] = content
        elif "NET SESSION FORM TRENDS" in header:
            sections['nets'] = content
        elif "MATCHUP SIMULATION PROFILE" in header:
            sections['sim'] = content
        elif "HISTORICAL BASELINE CONTEXT" in header:
            sections['history'] = content
            
    return sections

def render_plots(title, df_dict):
    if 'ipl' not in df_dict:
        st.info("IPL dataset required for advanced plots.")
        return

    df = df_dict['ipl']
    players_raw = [p.strip() for p in title.split(" VS ")]
    
    if len(players_raw) == 1:
        p1 = resolve_player_name(df, players_raw[0])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"##### 📉 Career Progression: {p1}")
            try:
                b_df = df[df['striker'] == p1]
                if not b_df.empty:
                    runs_per_match = b_df.groupby('match_id')['runs_off_bat'].sum().reset_index()
                    runs_per_match = runs_per_match.sort_values('match_id')
                    runs_per_match['cumulative_runs'] = runs_per_match['runs_off_bat'].cumsum()
                    
                    import matplotlib.pyplot as plt
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(6, 4))
                    fig.patch.set_facecolor('#0f172a')
                    ax.set_facecolor('#1e293b')
                    ax.plot(range(len(runs_per_match)), runs_per_match['cumulative_runs'], color='#38bdf8', linewidth=2)
                    ax.set_title("Cumulative Runs over Career", color='#e2e8f0', pad=10)
                    for spine in ax.spines.values(): spine.set_color('#334155')
                    st.pyplot(fig)
                else:
                    bw_df = df[df['bowler'] == p1]
                    if not bw_df.empty:
                        wkt_per_match = bw_df.groupby('match_id')['is_wicket'].sum().reset_index()
                        wkt_per_match = wkt_per_match.sort_values('match_id')
                        wkt_per_match['cum_wkts'] = wkt_per_match['is_wicket'].cumsum()
                        
                        import matplotlib.pyplot as plt
                        plt.style.use('dark_background')
                        fig, ax = plt.subplots(figsize=(6, 4))
                        fig.patch.set_facecolor('#0f172a')
                        ax.set_facecolor('#1e293b')
                        ax.plot(range(len(wkt_per_match)), wkt_per_match['cum_wkts'], color='#ef4444', linewidth=2)
                        ax.set_title("Cumulative Wickets over Career", color='#e2e8f0', pad=10)
                        for spine in ax.spines.values(): spine.set_color('#334155')
                        st.pyplot(fig)
                    else:
                        st.info("No match data for progression plot.")
            except Exception as e:
                st.error(f"Plot error: {e}")
                
        with c2:
            st.markdown(f"##### 🎯 Outcome Distribution: {p1}")
            try:
                b_df = df[df['striker'] == p1]
                if not b_df.empty:
                    dots = len(b_df[b_df['runs_off_bat'] == 0])
                    singles = len(b_df[b_df['runs_off_bat'].isin([1, 2, 3])])
                    boundaries = len(b_df[b_df['runs_off_bat'].isin([4, 6])])
                    
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(6, 4))
                    fig.patch.set_facecolor('#0f172a')
                    labels = ['Dots', 'Rotation (1-3)', 'Boundaries']
                    sizes = [dots, singles, boundaries]
                    colors = ['#475569', '#38bdf8', '#10b981']
                    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'color':"w"})
                    ax.axis('equal')
                    st.pyplot(fig)
                else:
                    st.info("Insufficient batting data for pie chart.")
            except Exception as e:
                st.error(f"Plot error: {e}")
                
    elif len(players_raw) >= 2:
        p1 = resolve_player_name(df, players_raw[0])
        p2 = resolve_player_name(df, players_raw[1])
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"##### ⚔️ Head-to-Head Outcomes: {p1} vs {p2}")
            try:
                matchup = df[(df['striker'] == p1) & (df['bowler'] == p2)]
                if not matchup.empty:
                    dots = len(matchup[matchup['runs_off_bat'] == 0])
                    singles = len(matchup[matchup['runs_off_bat'].isin([1, 2, 3])])
                    boundaries = len(matchup[matchup['runs_off_bat'].isin([4, 6])])
                    wkts = matchup['is_wicket'].sum()
                    
                    import matplotlib.pyplot as plt
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(6, 4))
                    fig.patch.set_facecolor('#0f172a')
                    ax.set_facecolor('#1e293b')
                    
                    cats = ['Dots', 'Rotation', 'Boundaries', 'Wickets']
                    vals = [dots, singles, boundaries, wkts]
                    ax.bar(cats, vals, color=['#94a3b8', '#38bdf8', '#10b981', '#ef4444'])
                    ax.set_title("H2H Event Frequencies", color='#e2e8f0', pad=10)
                    for spine in ax.spines.values(): spine.set_color('#334155')
                    st.pyplot(fig)
                else:
                    st.info("No direct matchups in history.")
            except Exception as e:
                st.error(f"Plot error: {e}")
                
        with c2:
            st.markdown(f"##### 🔥 Phase-wise Strike Rate Matchup")
            try:
                if 'over' not in df.columns:
                    df['over'] = df['ball'].astype(int)
                    
                matchup = df[(df['striker'] == p1) & (df['bowler'] == p2)].copy()
                if not matchup.empty:
                    matchup['phase'] = pd.cut(matchup['over'], bins=[-1, 6, 15, 20], labels=['Powerplay', 'Middle', 'Death'])
                    runs_phase = matchup.groupby('phase', observed=False)['runs_off_bat'].sum()
                    balls_phase = matchup.groupby('phase', observed=False).size()
                    
                    sr_phase = (runs_phase / balls_phase * 100).fillna(0)
                    
                    import matplotlib.pyplot as plt
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(6, 4))
                    fig.patch.set_facecolor('#0f172a')
                    ax.set_facecolor('#1e293b')
                    
                    ax.plot(sr_phase.index.astype(str), sr_phase.values, color='#f59e0b', marker='o', linewidth=2, markersize=8)
                    ax.set_title(f"SR vs {p2} by Phase", color='#e2e8f0', pad=10)
                    ax.set_ylim(0, max(200, sr_phase.max() + 20))
                    for spine in ax.spines.values(): spine.set_color('#334155')
                    st.pyplot(fig)
                else:
                    st.info("No phase data.")
            except Exception as e:
                st.error(f"Plot error: {e}")

# -----------------
# DASHBOARD LOGIC
# -----------------
if st.session_state.active_response:
    response_text = st.session_state.active_response
    query_str = st.session_state.active_query
    
    # Check if the response is the formatted orchestrator report
    if "EXECUTIVE INTELLIGENCE REPORT:" in response_text:
        parsed = parse_markdown_to_sections(response_text)
        
        st.markdown(f"<h3 style='color:#38bdf8; text-align:center; margin-top:2rem;'>TARGET LOCKED: {parsed['title']}</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #334155; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        
        # 3-CARD GRID
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown('<div class="card-fitness">', unsafe_allow_html=True)
            st.markdown("#### 🚨 MEDICAL / FITNESS")
            st.markdown(parsed['fitness'])
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="card-nets">', unsafe_allow_html=True)
            st.markdown("#### 📈 NET TRACKING")
            st.markdown(parsed['nets'])
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c3:
            st.markdown('<div class="card-sim">', unsafe_allow_html=True)
            st.markdown("#### 🎯 SIMULATION")
            st.markdown(parsed['sim'])
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # DEEP-DIVE EXPANDER
        with st.expander("🔍 Expand Deep-Dive Dossier / See More About This Matrix"):
            st.markdown("### 📊 Tactical Visualizations & Advanced Plots")
            st.markdown(parsed['history'])
            
            st.markdown("---")
            render_plots(parsed['title'], df_dict)
            
    else:
        # Standard fallback for non-orchestrator queries (e.g., standard pandas LLM response)
        st.markdown("<h3 style='color:#38bdf8;'>📡 DATABASE QUERY RESULT</h3>", unsafe_allow_html=True)
        st.markdown(response_text)

# -----------------
# BIOMECHANICAL TELEMETRY SUITE
# -----------------
st.markdown("---")

@st.cache_data
def load_bio_data():
    try:
        bio_df = pd.read_csv('data/player_biometrics_master.csv')
        telemetry_df = pd.read_csv('data/net_telemetry_balls.csv')
        return bio_df, telemetry_df
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()

bio_df, telemetry_df = load_bio_data()

bio_query = st.session_state.active_query if 'active_query' in st.session_state else None

if bio_query and not bio_df.empty:
    # Find all players mentioned in the query
    found_players = []
    for p in bio_df['player_name']:
        if p.lower() in bio_query.lower() and p not in found_players:
            found_players.append(p)
            
    if found_players:
        st.title("⚡ AntiGravity: Biomechanical Telemetry Suite")
        
        # --- HEAD-TO-HEAD COMPARISON (If multiple players) ---
        if len(found_players) >= 2:
            st.markdown(f"### ⚔️ HEAD-TO-HEAD BIOMETRIC COMPARISON: {found_players[0].upper()} VS {found_players[1].upper()}")
            
            p1_bio = bio_df[bio_df['player_name'] == found_players[0]].iloc[0]
            p2_bio = bio_df[bio_df['player_name'] == found_players[1]].iloc[0]
            
            # Metrics comparison
            comp_c1, comp_c2, comp_c3 = st.columns(3)
            with comp_c1:
                st.metric(label=f"Max Core Speed ({found_players[0]})", value=f"{p1_bio['max_recorded_core_speed_kmh']} km/h")
                st.metric(label=f"Max Core Speed ({found_players[1]})", value=f"{p2_bio['max_recorded_core_speed_kmh']} km/h")
            with comp_c2:
                st.metric(label=f"Release Height ({found_players[0]})", value=f"{p1_bio['bowling_release_point_height_m']} m")
                st.metric(label=f"Release Height ({found_players[1]})", value=f"{p2_bio['bowling_release_point_height_m']} m")
            with comp_c3:
                st.metric(label=f"Injury Index ({found_players[0]})", value=f"{p1_bio['shoulder_ankle_injury_threshold_index']}")
                st.metric(label=f"Injury Index ({found_players[1]})", value=f"{p2_bio['shoulder_ankle_injury_threshold_index']}")
            
            # Comparative Plot
            p1_telemetry = telemetry_df[telemetry_df['player_name'] == found_players[0]]
            p2_telemetry = telemetry_df[telemetry_df['player_name'] == found_players[1]]
            
            if not p1_telemetry.empty and not p2_telemetry.empty:
                st.markdown("**Release Velocity Distribution Comparison**")
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                plt.style.use('dark_background')
                fig_comp, ax_comp = plt.subplots(figsize=(10, 4))
                
                sns.kdeplot(data=p1_telemetry, x='release_speed', fill=True, color='#38bdf8', label=found_players[0], ax=ax_comp)
                sns.kdeplot(data=p2_telemetry, x='release_speed', fill=True, color='#ef4444', label=found_players[1], ax=ax_comp)
                
                ax_comp.set_xlabel("Release Speed (km/h)", color="#e2e8f0")
                ax_comp.set_ylabel("Density", color="#e2e8f0")
                fig_comp.patch.set_facecolor('#0f172a')
                ax_comp.set_facecolor('#1e293b')
                for spine in ax_comp.spines.values(): spine.set_color('#334155')
                ax_comp.tick_params(colors="#e2e8f0")
                ax_comp.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='white')
                
                st.pyplot(fig_comp)
                plt.close(fig_comp)
            
            st.markdown("---")
            
        # --- INDIVIDUAL PROFILES ---
        for player_name in found_players[:2]:  # Display up to 2 players individually
            player_bio = bio_df[bio_df['player_name'] == player_name]
            player_telemetry_full = telemetry_df[telemetry_df['player_name'] == player_name]
            
            # Apply venue filter
            if st.session_state.get('selected_venue', 'All Venues') != 'All Venues':
                player_telemetry = player_telemetry_full[player_telemetry_full['venue_soil_type'] == st.session_state.selected_venue]
            else:
                player_telemetry = player_telemetry_full
            
            if not player_bio.empty:
                player_info = player_bio.iloc[0]
                
                # --- HERO PROFILE COMPARTMENT ---
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(player_info['image_url'], caption=player_info['player_name'], width=200)
                    
                with col2:
                    st.markdown(f"### {player_info['player_name'].upper()} | INDIVIDUAL DOSSIER")
                    st.markdown(f"**Dominant Hand:** {player_info['dominant_hand']}")
                    st.markdown(f"**Height / Weight:** {player_info['height_cm']} cm / {player_info['weight_kg']} kg")
                    st.markdown(f"**Release Height:** {player_info['bowling_release_point_height_m']} m")
                    
                    st.metric(label="Max Core Speed", value=f"{player_info['max_recorded_core_speed_kmh']} km/h")
                    st.metric(label="Injury Threshold Index", value=f"{player_info['shoulder_ankle_injury_threshold_index']} / 100")
                    
                if not player_telemetry.empty:
                    st.markdown("#### 📊 TACTICAL VISUALIZATIONS")
                    
                    plt.style.use('dark_background')
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        st.markdown("**1. Release Velocity Progression**")
                        fig1, ax1 = plt.subplots(figsize=(6, 4))
                        sns.lineplot(data=player_telemetry, x=player_telemetry.index, y='release_speed', marker='o', color='#00d2d3', ax=ax1)
                        ax1.set_xlabel("Balls Bowled in Session")
                        ax1.set_ylabel("Speed (km/h)")
                        fig1.patch.set_facecolor('#0f172a')
                        ax1.set_facecolor('#1e293b')
                        for spine in ax1.spines.values(): spine.set_color('#334155')
                        st.pyplot(fig1)
                        plt.close(fig1)
                        
                    with col4:
                        st.markdown("**2. Length & Deviation Clustering**")
                        fig2, ax2 = plt.subplots(figsize=(6, 4))
                        sns.scatterplot(data=player_telemetry, x='deviation_degrees', y='pitch_distance_from_stumps_m', size='bounce_height_m', hue='release_speed', palette='flare', ax=ax2)
                        ax2.set_xlabel("Lateral Deviation (Degrees)")
                        ax2.set_ylabel("Pitch Distance from Stumps (m)")
                        fig2.patch.set_facecolor('#0f172a')
                        ax2.set_facecolor('#1e293b')
                        for spine in ax2.spines.values(): spine.set_color('#334155')
                        st.pyplot(fig2)
                        plt.close(fig2)
                        
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        st.markdown("**3. \"CLUTCH\" PRESSURE INDEX (CHOKE ANALYSIS)**")
                        if 'pressure_scenario' in player_telemetry_full.columns:
                            fig3, ax3 = plt.subplots(figsize=(6, 4))
                            pressure_agg = player_telemetry_full.groupby('pressure_scenario')[['release_speed', 'pitch_distance_from_stumps_m']].mean().reindex(['Low', 'High']).reset_index()
                            pressure_agg.set_index('pressure_scenario').plot(kind='bar', ax=ax3, secondary_y='pitch_distance_from_stumps_m', color=['#38bdf8', '#ef4444'], legend=False)
                            ax3.set_xlabel("Pressure Scenario", color="#e2e8f0")
                            ax3.set_ylabel("Speed (km/h)", color="#38bdf8")
                            ax3.right_ax.set_ylabel("Inaccuracy (m from stumps)", color="#ef4444")
                            fig3.patch.set_facecolor('#0f172a')
                            ax3.set_facecolor('#1e293b')
                            for spine in ax3.spines.values(): spine.set_color('#334155')
                            ax3.tick_params(colors="#e2e8f0")
                            ax3.right_ax.tick_params(colors="#e2e8f0")
                            st.pyplot(fig3)
                            plt.close(fig3)
                        else:
                            st.info("Pressure data unavailable.")
                            
                    with col6:
                        st.markdown("**4. VENUE-SPECIFIC MICRO-CLIMATE ENGINE**")
                        if 'venue_soil_type' in player_telemetry_full.columns:
                            fig4, ax4 = plt.subplots(figsize=(6, 4))
                            df_melted = player_telemetry_full.melt(id_vars='venue_soil_type', value_vars=['bounce_height_m', 'deviation_degrees'], var_name='Metric', value_name='Value')
                            sns.boxplot(data=df_melted, x='venue_soil_type', y='Value', hue='Metric', palette=['#10b981', '#f59e0b'], ax=ax4)
                            ax4.set_xlabel("")
                            ax4.set_ylabel("Variance", color="#e2e8f0")
                            ax4.tick_params(axis='x', rotation=15, labelsize=8, colors="#e2e8f0")
                            ax4.tick_params(axis='y', colors="#e2e8f0")
                            fig4.patch.set_facecolor('#0f172a')
                            ax4.set_facecolor('#1e293b')
                            for spine in ax4.spines.values(): spine.set_color('#334155')
                            ax4.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='white', fontsize=8)
                            st.pyplot(fig4)
                            plt.close(fig4)
                        else:
                            st.info("Venue data unavailable.")
                            
                    with st.expander(f"🔍 Access Deep-Dive Biomechanical Dossier for {player_name}"):
                        st.dataframe(player_telemetry[['session_date', 'release_speed', 'release_angle', 'deviation_degrees', 'pitch_distance_from_stumps_m']])
                        st.info("Mathematical State-Space model indicates performance variance is within normal physiological limits.")
                else:
                    st.warning(f"No net telemetry data available for {player_name}.")
                
                st.markdown("<br><hr style='border-color: #334155;'><br>", unsafe_allow_html=True)

