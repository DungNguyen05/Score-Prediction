# API configuration
API_KEY = "42941e9e63ae4f029b9a88377da23dec"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_KEY
}

# Model configuration
HISTORY_MATCHES = 20  # Number of recent matches to consider for each team
SEASONS_TO_ANALYZE = 2  # Number of seasons to look back