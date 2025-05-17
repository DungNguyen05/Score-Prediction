# API configuration
API_KEY = "42941e9e63ae4f029b9a88377da23dec"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_KEY
}

# Match prediction configuration
MATCHES_TO_CONSIDER = 20  # Number of recent matches to analyze
MAX_H2H_MATCHES = 10      # Maximum number of head-to-head matches to use

# Data fetching optimization 
FETCH_RECENT_MATCHES = True  # Whether to fetch recent team matches (set to False to skip and use H2H only)
FETCH_H2H_MATCHES = True     # Whether to fetch head-to-head matches


# Team configuration for prediction
HOME_TEAM = "manchester city"  
AWAY_TEAM = "crystal palace"   

# Dictionary of common team IDs
TEAM_IDS = {
    "real madrid": 86,
    "barcelona": 81,
    "manchester united": 66,
    "liverpool": 64,
    "manchester city": 65,
    "bayern munich": 5,
    "paris saint-germain": 524,
    "juventus": 109,
    "arsenal": 57,
    "chelsea": 61,
    "atletico madrid": 78,
    "borussia dortmund": 4,
    "inter milan": 108,
    "ac milan": 98,
    "tottenham": 73,
    "napoli": 113,
    "benfica": 294,
    "ajax": 678,
    "sevilla": 559,
    "porto": 503,
    "crystal palace": 354

}