import requests
import math
import json
from collections import defaultdict

LEVEL_LIST_URL = "https://api.slin.dev/grab/v1/list?max_format_version=20&type=curated_challenge"
BASE_STATS_URL = "https://api.slin.dev/grab/v1/statistics"

# ---------- MMR SYSTEM ----------

def level_mmr(victors):
    # smoother scaling
    return 5000 / math.sqrt(victors + 1)

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

# ---------- MAIN ----------

def main():
    print("Fetching levels...")

    try:
        levels_data = requests.get(LEVEL_LIST_URL).json()
    except:
        print("Failed to fetch level list")
        return

    player_scores = defaultdict(float)

    for level in levels_data:
        level_id = level.get("id")

        if not level_id:
            continue

        print(f"Processing level {level_id}")

        # Try to fetch leaderboard
        try:
            url = f"{BASE_STATS_URL}/{level_id}/1654257963"
            data = requests.get(url).json()
        except:
            continue

        scores = data.get("scores", [])

        if not scores:
            continue

        victors = len(scores)

        base_mmr = level_mmr(victors)

        for i, entry in enumerate(scores):
            player = entry.get("player")

            if not player:
                continue

            rank = i + 1
            mmr_gain = base_mmr * placement_multiplier(rank)

            player_scores[player] += mmr_gain

    # Build leaderboard
    leaderboard = []

    for player, mmr in player_scores.items():
        leaderboard.append({
            "player": player,
            "mmr": int(mmr),
            "rank": get_rank(mmr)
        })

    leaderboard.sort(key=lambda x: x["mmr"], reverse=True)

    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=2)

    print("Leaderboard updated successfully!")

if __name__ == "__main__":
    main()
