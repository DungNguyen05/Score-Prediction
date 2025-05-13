import requests

API_KEY = "YOUR_API_KEY"
TEAM_ID = 541  # Real Madrid ID in API-Football

url = "https://v3.football.api-sports.io/fixtures"
headers = {
    "x-rapidapi-key": "42941e9e63ae4f029b9a88377da23dec",
    "x-rapidapi-host": "v3.football.api-sports.io"
}

params = {
    "team": TEAM_ID,
    "last": 10
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    for match in data["response"]:
        fixture = match["fixture"]
        teams = match["teams"]
        goals = match["goals"]
        stats = match.get("statistics", [])

        date = fixture["date"][:10]
        home = teams["home"]["name"]
        away = teams["away"]["name"]
        score_home = goals["home"]
        score_away = goals["away"]

        print(f"\n{date} - {home} {score_home}:{score_away} {away}")

        # Fetch stats by fixture ID
        fixture_id = fixture["id"]
        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics"
        stats_params = {
            "fixture": fixture_id
        }
        stats_res = requests.get(stats_url, headers=headers, params=stats_params)
        if stats_res.status_code == 200:
            stats_data = stats_res.json()["response"]
            for team_stats in stats_data:
                team_name = team_stats["team"]["name"]
                corners = next((item["value"] for item in team_stats["statistics"] if item["type"] == "Corner Kicks"), "N/A")
                print(f"{team_name} corners: {corners}")
        else:
            print("Stats unavailable for this match.")
else:
    print("Failed to retrieve match data.")