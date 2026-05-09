# IPL AI Agent – Smart Cricket Analyst + Commentary Engine

Welcome to the IPL AI Agent! This is a complete Python-based offline CLI tool that takes natural language queries, parses them into data queries against ball-by-ball IPL data, and returns stats, match contexts, and dynamic commentary.

## Features

- **Player vs Player Matchup**: Check how a batter performs against a specific bowler.
- **Player Performance**: Find the top-scoring matches for a specific player.
- **High Score Matches**: Find the match with the highest total runs.
- **Death Overs Analysis**: Identify the best batsmen in the death overs (overs 16+).
- **Match Story & Dynamic Commentary**: Get an AI-like generated summary of any match, including its turning point. Supports fun "hype" and "hinglish" modes!

## Project Structure

```
iplaiagent/
│
├── data/
│   └── processed/
│       └── ipl_all_matches.csv    <-- MUST BE PLACED HERE
│
├── scripts/
│   ├── stats_engine.py
│   ├── turning_point_engine.py
│   ├── match_context_engine.py
│   ├── dynamic_commentary_engine.py
│   ├── query_engine.py
│   └── main.py
│
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Install Dependencies**:
   Open a terminal in the `iplaiagent` directory and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Your Data**:
   Ensure you have the ball-by-ball IPL data file named `ipl_all_matches.csv`.
   Place this file inside the `data/processed/` folder.

3. **Run the Application**:
   Execute the main script from the `iplaiagent` directory:
   ```bash
   python scripts/main.py
   ```

## Example Queries

Once the app is running, you can interact with it using natural language. Try these examples:

- *"Virat Kohli vs Kagiso Rabada"*
- *"Which match had the highest runs?"*
- *"Who are the best death overs batsmen?"*
- *"Top matches of Rohit Sharma"*
- *"Explain match 335982"*
- *"Explain match 335982 in hype mode"*
- *"Explain match 335982 hinglish"*

Enjoy the AI Analyst!
