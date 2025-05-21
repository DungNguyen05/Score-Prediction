# API configuration
API_KEY = "42941e9e63ae4f029b9a88377da23dec"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_KEY
}

# Match prediction configuration
MATCHES_TO_CONSIDER = 20  # Number of recent matches to analyze
MAX_H2H_MATCHES = 10      # Maximum number of head-to-head matches to use

# Team configuration for prediction (using team IDs directly)
HOME_TEAM_ID = 66  
AWAY_TEAM_ID = 73   

# Match venue setting
IS_NEUTRAL_VENUE = True  # Set to True for matches at neutral venues

# Cache configuration
CACHE_MAX_AGE = 12  # hours