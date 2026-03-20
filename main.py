import requests
import math
from collections import defaultdict

LEVEL_LIST_URL = "https://api.slin.dev/grab/v1/list?max_format_version=20&type=curated_challenge"
BASE_STATS_URL = "https://api.slin.dev/grab/v1/statistics"

# ---------- MMR LOGIC ----------

def level_mmr(victors, age_days):
    age_factor = math.log(age_days + 1) * 500
    victor_factor = 8000 / (victors + 1)
    return age_factor + victor_factor

def placement_multiplier(rank):
    if rank == 1:
        return 1.5
    elif rank <= 5:
        return 1.2
    elif rank <= 10:
        return 1.0
    elif rank <= 25:
        return 0.8
    else:
        return 0.5

def get_rank(mmr):
    if mmr < 100:
        return "Unranked"
    elif mmr < 500:
        return "Bronze"
    elif mmr < 1000:
        return "Silver"
    elif mmr < 2000:
        return "Gold"
    elif mmr < 3000:
        return "Ruby"
    elif mmr < 5000:
        return "Diamond"
    elif mmr < 8000:
        return "Master"
    elif mmr < 12000:
        return "Grandmaster"
    else:
        return "Elite"

# ---------- MAIN LOGIC ----------

def main():
    print("Fetching level list...")
    levels_data = requests.get(LEVEL_LIST_URL).json()

    player_scores = defaultdict(float)

    for level in levels_data:
        level_id = level.get("id")

        if not level_id:
            continue

        print(f"Processing level {level_id}")

        # Get leaderboard
        try:
            url = f"{BASE_STATS_URL}/{level_id}/1654257963"
            data = requests.get(url).json()
        except:
            continue

        victors = len(data.get("scores", []))
        age_days = 365  # fallback if not provided

        base_mmr = level_mmr(victors, age_days)

        scores = data.get("scores", [])

        for i, entry in enumerate(scores):
            player = entry.get("player", "unknown")
            rank = i + 1

            mmr_gain = base_mmr * placement_multiplier(rank)
            player_scores[player] += mmr_gain

    # Convert to final leaderboard
    leaderboard = []

    for player, mmr in player_scores.items():
        leaderboard.append({
            "player": player,
            "mmr": int(mmr),
            "rank": get_rank(mmr)
        })

    leaderboard.sort(key=lambda x: x["mmr"], reverse=True)

    # Save file
    with open("leaderboard.json", "w") as f:
        import json
        json.dump(leaderboard, f, indent=2)

    print("Leaderboard updated!")

if __name__ == "__main__":
    main()