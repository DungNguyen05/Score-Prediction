import requests

url = "https://v3.football.api-sports.io/fixtures"

headers = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": "ae77e0ebaa6dcb82472e5f974aff1ce8"  # Replace with your real key
}

params = {
    "team": "529",       # FC Barcelona
    "season": "2023",    # Season year
    # "league": "140"    # Optional: La Liga (Spain), or leave out to get all competitions
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    for match in data['response']:
        date = match['fixture']['date'][:10]
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        score_home = match['goals']['home']
        score_away = match['goals']['away']
        print(f"{date} - {home} {score_home} : {score_away} {away}")
else:
    print("Error:", response.status_code)