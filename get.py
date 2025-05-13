import requests

# Replace with your actual API key from football-data.org
API_KEY = "42941e9e63ae4f029b9a88377da23dec"

# Real Madrid's team ID on football-data.org
TEAM_ID = 86

# API endpoint
url = f"https://api.football-data.org/v4/teams/{TEAM_ID}/matches"

# Request headers
headers = {
    "X-Auth-Token": API_KEY
}

# Parameters: only finished matches, limit to last 10
params = {
    "status": "FINISHED",
    "limit": 10,
    "sort": "desc"  # Latest matches first
}

# Make request
response = requests.get(url, headers=headers, params=params)

# Handle response
if response.status_code == 200:
    data = response.json()
    matches = data.get("matches", [])
    if matches:
        print("Last 10 Real Madrid matches:")
        for match in matches:
            date = match['utcDate'][:10]
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            score_home = match['score']['fullTime']['home']
            score_away = match['score']['fullTime']['away']
            print(f"{date} - {home} {score_home} : {score_away} {away}")
    else:
        print("No finished matches found.")
else:
    print(f"API Error {response.status_code}: {response.text}")