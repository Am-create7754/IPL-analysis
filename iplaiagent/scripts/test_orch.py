from main import load_data
from query_engine import handle_query

print("Loading datasets...")
dfs = load_data()

queries = [
    "Tell me about Bumrah",
    "How is Hardik looking?",
    "Shreyas Iyer update",
    "simulate Bumrah vs Virat Kohli"
]

for q in queries:
    print(f"\n\n--- QUERY: {q} ---")
    res = handle_query(q, dfs)
    print(res)
