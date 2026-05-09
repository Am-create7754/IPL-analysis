import random

def generate_commentary(context, style="standard"):
    """
    Generates dynamic commentary based on match context.
    Styles available: 'standard', 'hype', 'hinglish'
    """
    if not context:
        return "I couldn't find the context for this match to generate commentary."
        
    top_batter = context.get('top_batter', 'Unknown')
    top_runs = context.get('top_runs', 0)
    total_runs = context.get('total_runs', 0)
    
    turning_over = context.get('turning_over')
    over_num = turning_over.get('over', 'Unknown') if turning_over else 'Unknown'
    impact_runs = turning_over.get('runs', 0) if turning_over else 0
    impact_wickets = turning_over.get('wickets', 0) if turning_over else 0

    templates = {
        "standard": [
            f"In this match, the total score reached {total_runs}. {top_batter} was the standout performer, scoring a brilliant {top_runs} runs. The turning point was undoubtedly over {over_num}, where we saw {impact_runs} runs and {impact_wickets} wickets.",
            f"A solid game of cricket! A total of {total_runs} runs were scored. The highlight was {top_batter} who smashed {top_runs}. The game changed on its head in over {over_num} with {impact_runs} runs and {impact_wickets} wickets falling.",
            f"Analyzing the match, {top_batter} anchored the innings with {top_runs} runs out of the {total_runs} total. The pivotal moment occurred in over {over_num}, swinging the momentum with {impact_wickets} wickets and {impact_runs} runs."
        ],
        "hype": [
            f"ABSOLUTE CINEMA! A massive {total_runs} on the board! {top_batter} went BERSERK with {top_runs} runs! But the REAL madness happened in over {over_num} - {impact_runs} runs and {impact_wickets} wickets! UNBELIEVABLE SCENES!",
            f"WHAT A MATCH! {top_batter} lit up the stadium with a fiery {top_runs}! The scoreboard ticked to {total_runs}. But wait until you hear about over {over_num}... {impact_wickets} wickets down and {impact_runs} runs! PURE MAYHEM!",
            f"FIREWORKS everywhere! {total_runs} runs total, with {top_batter} unleashing pure destruction for {top_runs} runs! The match flipped completely in over {over_num}—we witnessed {impact_runs} runs and {impact_wickets} insane wickets!"
        ],
        "hinglish": [
            f"Kya match tha bhai! Total {total_runs} runs bane. {top_batter} ne toh aag laga di, {top_runs} runs marke! Par asli turning point tha over {over_num}, jisme {impact_runs} runs aaye aur {impact_wickets} wickets gire. Bawaal ekdum!",
            f"Bhai sahab, total score {total_runs} tha aur {top_batter} ki batting dekh ke maza aa gaya—{top_runs} runs! Lekin game tab palta jab over {over_num} mein {impact_runs} runs gaye aur {impact_wickets} wickets nikle. Ekdum kadak moment tha!",
            f"Match ka score {total_runs} tak pahuncha. {top_batter} form mein tha aur {top_runs} thok diye! Asli twist tab aaya jab over {over_num} mein {impact_runs} runs aur {impact_wickets} wickets ki hera pheri hui. Gazab ka match!"
        ]
    }
    
    chosen_style = style.lower() if style.lower() in templates else "standard"
    return random.choice(templates[chosen_style])
