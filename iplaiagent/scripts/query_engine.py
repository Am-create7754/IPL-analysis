import os
import re
from stats_engine import get_player_matchup, get_best_death_overs_batsmen, get_top_batsmen, resolve_player_name
from match_context_engine import get_match_context
from dynamic_commentary_engine import generate_commentary
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Initialize the dynamic LLM agent globally so it is reused across queries
_agent = None

def get_agent(df):
    global _agent
    if _agent is None:
        # Check if API key is present
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0, google_api_key=os.environ.get("GEMINI_API_KEY"))
        _agent = create_pandas_dataframe_agent(
            llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True
        )
    return _agent

def handle_query(query: str, df):
    """
    Parses a natural language query. It routes commentary queries to the hardcoded engine,
    and sends everything else to the dynamic LLM Pandas Agent.
    """
    q_lower = query.lower()
    
    # 1. Check for specific dynamic commentary queries
    style = "standard"
    if "hype" in q_lower:
        style = "hype"
    elif "hinglish" in q_lower:
        style = "hinglish"
        
    if "explain match" in q_lower or "explain turning point of match" in q_lower:
        match_search = re.search(r"match\s+(\d+)", q_lower)
        if match_search:
            match_id = match_search.group(1)
            context = get_match_context(df, match_id)
            if context:
                return generate_commentary(context, style)
            else:
                return f"Could not find context for Match {match_id}."

    # 2. Dynamic Agent handles everything else!
    try:
        agent = get_agent(df)
        print("\n[Dynamic Agent is running... this may take a few seconds]")
        
        # Give the agent instructions to handle name variations
        enhanced_query = (
            "IMPORTANT RULES FOR DATASET:\n"
            "1. Player names use initials (e.g., 'RG Sharma', 'V Kohli'). NEVER use exact matching like `== 'Rohit Sharma'`.\n"
            "2. ALWAYS use partial matching like `str.contains('Sharma', case=False, na=False)` when filtering by a player's name.\n"
            "3. df1 contains match info (season, date). df2 and df3 contain ball-by-ball info (striker, bowler, batsman_runs, etc.). To get stats for a season, merge/filter across them using match_id.\n\n"
            f"User Question: {query}"
        )
        
        response = agent.invoke(enhanced_query)
        return response["output"]
    except Exception as e:
        return f"Dynamic Agent Error: {e}"
