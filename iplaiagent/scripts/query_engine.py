import os
import re
from stats_engine import get_player_matchup, get_best_death_overs_batsmen, get_top_batsmen, resolve_player_name
from match_context_engine import get_match_context
from dynamic_commentary_engine import generate_commentary
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from simulation_engine import handle_simulation_query
from situational_engine import parse_and_execute_situational_query
from stats_engine import get_fitness_impact
from orchestrator import run_orchestrator

# Initialize the dynamic LLM agent globally so it is reused across queries
_agent = None

def get_agent(dfs_list):
    global _agent
    if _agent is None:
        # Check if API key is present
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0, google_api_key=os.environ.get("GEMINI_API_KEY"))
        _agent = create_pandas_dataframe_agent(
            llm, 
            dfs_list, 
            verbose=True, 
            allow_dangerous_code=True
        )
    return _agent

def handle_query(query: str, dfs: dict):
    """
    Parses a natural language query. It routes commentary queries to the hardcoded engine,
    and sends everything else to the dynamic LLM Pandas Agent.
    """
    q_lower = query.lower()
    
    # 0. Intercept and run PROACTIVE ORCHESTRATOR FIRST (Player specific logic)
    orchestrator_res = run_orchestrator(query, dfs)
    if orchestrator_res:
        return orchestrator_res
    
    # 0. Intercept Simulation Queries (Pillar 3)
    if "!simulate" in q_lower:
        return handle_simulation_query(query, dfs)
        
    # 0. Intercept Fitness Impact Queries (Pillar 1)
    if "injury" in q_lower or "fitness" in q_lower or "clearance" in q_lower:
        return get_fitness_impact(query, dfs)
        
    # 0. Intercept Situational Queries (Pillar 2)
    situational_res = parse_and_execute_situational_query(query, dfs)
    if situational_res:
        return situational_res
    
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
            context = get_match_context(dfs['ipl'] if 'ipl' in dfs else list(dfs.values())[0], match_id)
            if context:
                return generate_commentary(context, style)
            else:
                return f"Could not find context for Match {match_id}."

    # 2. Dynamic Agent handles everything else!
    try:
        agent = get_agent(list(dfs.values()))
        print("\n[Dynamic Agent is running... this may take a few seconds]")
        
        # Give the agent instructions to handle name variations
        enhanced_query = (
            "IMPORTANT RULES FOR DATASET:\n"
            "1. Player names use initials (e.g., 'RG Sharma', 'V Kohli'). NEVER use exact matching like `== 'Rohit Sharma'`.\n"
            "2. ALWAYS use partial matching like `str.contains('Sharma', case=False, na=False)` when filtering by a player's name.\n"
            "3. df1 is typically matches.csv. The other dataframes might be ipl_all_matches.csv, player_profile, fitness, etc.\n"
            "4. **DEEP RESEARCH PROTOCOL**: If the data is NOT available in the provided CSVs, or if the user asks a deep analytical question, you MUST use your own internal knowledge base to answer it comprehensively. Act as an elite sports intelligence agent. Do not just fail; supplement with your own knowledge.\n\n"
            f"User Question: {query}"
        )
        
        response = agent.invoke(enhanced_query)
        return response["output"]
    except Exception as e:
        return f"Dynamic Agent Error: {e}"
