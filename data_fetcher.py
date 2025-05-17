import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta

from config import (
    API_KEY, BASE_URL, HEADERS, 
    MATCHES_TO_CONSIDER, MAX_H2H_MATCHES,
    FETCH_RECENT_MATCHES, FETCH_H2H_MATCHES,
    TEAM_IDS
)

# Create a cache directory if it doesn't exist
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_team_id(team_name):
    """
    Get team ID from the dictionary of common teams
    """
    team_name_lower = team_name.lower()
    
    # Try exact match
    if team_name_lower in TEAM_IDS:
        team_id = TEAM_IDS[team_name_lower]
        return team_id, team_name
    
    # Try partial match
    for key, id in TEAM_IDS.items():
        if team_name_lower in key or key in team_name_lower:
            return id, key
    
    print(f"Team not found: {team_name}")
    print("Available teams: " + ", ".join(sorted(TEAM_IDS.keys())))
    return None, None

def get_cached_data(cache_key, max_age_hours=24):
    """
    Get data from cache if available and fresh
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        # Check if cache is still valid
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_mod_time < timedelta(hours=max_age_hours):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading cache: {e}")
    
    return None

def save_to_cache(cache_key, data):
    """
    Save data to cache
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving to cache: {e}")

def get_recent_team_matches(team_id, team_name, limit=MATCHES_TO_CONSIDER):
    """
    Get the most recent matches for a specific team directly
    """
    # Check if we should skip fetching recent matches
    if not FETCH_RECENT_MATCHES:
        print(f"Skipping recent matches for {team_name} (FETCH_RECENT_MATCHES=False)")
        return []
    
    # Try to get from cache first
    cache_key = f"team_matches_{team_id}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        matches = cached_data
        print(f"Using cached data: Found {len(matches)} recent matches for {team_name}")
        return matches
    
    # Not in cache, fetch from API
    url = f"{BASE_URL}/teams/{team_id}/matches"
    
    params = {
        "status": "FINISHED",
        "limit": limit,
        "sort": "date",  # Get matches sorted by date
        "direction": "desc"  # Most recent first
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            print(f"Found {len(matches)} recent matches for {team_name}")
            
            # Save to cache
            save_to_cache(cache_key, matches)
            
            return matches
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_head_to_head_matches(team_a_id, team_a_name, team_b_id, team_b_name, limit=MAX_H2H_MATCHES):
    """
    Get head-to-head matches between two teams
    """
    # Check if we should skip fetching H2H matches
    if not FETCH_H2H_MATCHES:
        print(f"Skipping head-to-head matches (FETCH_H2H_MATCHES=False)")
        return []
    
    # Try to get from cache first
    cache_key = f"h2h_{min(team_a_id, team_b_id)}_{max(team_a_id, team_b_id)}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        h2h_matches = cached_data
        print(f"Using cached data: Found {len(h2h_matches)} head-to-head matches between {team_a_name} and {team_b_name}")
        return h2h_matches[:limit]
    
    # Not in cache, fetch directly using the dedicated API endpoint
    url = f"{BASE_URL}/teams/{team_a_id}/matches"
    
    params = {
        "status": "FINISHED",
        "limit": 100,
        "teams": team_b_id,  # Filter for matches against this team
        "sort": "date",
        "direction": "desc"
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            h2h_matches = data.get("matches", [])
            print(f"Found {len(h2h_matches)} head-to-head matches between {team_a_name} and {team_b_name}")
            
            # Save to cache
            save_to_cache(cache_key, h2h_matches)
            
            return h2h_matches[:limit]
        else:
            print(f"API Error {response.status_code} when fetching head-to-head matches: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred when fetching head-to-head matches: {e}")
        return []

def extract_match_features(matches, team_id):
    """
    Extract relevant features from match data for a specific team
    """
    features = []
    
    for match in matches:
        is_home = match['homeTeam']['id'] == team_id
        
        # Get team scores
        home_score = match['score']['fullTime']['home'] or 0
        away_score = match['score']['fullTime']['away'] or 0
        
        # Date
        match_date = datetime.strptime(match['utcDate'][:10], '%Y-%m-%d')
        
        # Goals scored and conceded
        goals_scored = home_score if is_home else away_score
        goals_conceded = away_score if is_home else home_score
        
        # Opponent
        opponent_id = match['awayTeam']['id'] if is_home else match['homeTeam']['id']
        opponent_name = match['awayTeam']['name'] if is_home else match['homeTeam']['name']
        
        # Result (win, draw, loss)
        if home_score > away_score:
            result = 'W' if is_home else 'L'
        elif home_score < away_score:
            result = 'L' if is_home else 'W'
        else:
            result = 'D'
        
        # Match info for reference
        match_info = f"{match_date.strftime('%Y-%m-%d')} - "
        match_info += f"{match['homeTeam']['name']} {home_score}-{away_score} {match['awayTeam']['name']}"
        
        features.append({
            'match_id': match['id'],
            'date': match_date,
            'is_home': is_home,
            'opponent_id': opponent_id,
            'opponent_name': opponent_name,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'total_goals': goals_scored + goals_conceded,
            'result': result,
            'match_info': match_info
        })
    
    return features

def get_team_stats(team_id, team_name):
    """
    Calculate team statistics from recent match data
    """
    # Get recent matches for this team
    team_matches = get_recent_team_matches(team_id, team_name)
    
    if not team_matches and FETCH_RECENT_MATCHES:
        print(f"No matches found for {team_name}")
        return None
    
    # If not fetching recent matches, create default stats
    if not FETCH_RECENT_MATCHES:
        return {
            'team_id': team_id,
            'team_name': team_name,
            'num_matches': 0,
            'avg_goals_scored': 0,
            'avg_goals_conceded': 0,
            'avg_total_goals': 0,
            'home_avg_goals_scored': 0,
            'home_avg_goals_conceded': 0,
            'away_avg_goals_scored': 0,
            'away_avg_goals_conceded': 0,
            'win_rate': 0,
            'recent_form': '',
            'match_history': []
        }
    
    # Extract features
    features = extract_match_features(team_matches, team_id)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(features)
    
    if df.empty:
        print(f"No features extracted for {team_name}")
        return None
    
    # Calculate aggregated stats
    stats = {
        'team_id': team_id,
        'team_name': team_name,
        'num_matches': len(df),
        'avg_goals_scored': df['goals_scored'].mean(),
        'avg_goals_conceded': df['goals_conceded'].mean(),
        'avg_total_goals': df['total_goals'].mean(),
        'home_avg_goals_scored': df[df['is_home']]['goals_scored'].mean() if not df[df['is_home']].empty else 0,
        'home_avg_goals_conceded': df[df['is_home']]['goals_conceded'].mean() if not df[df['is_home']].empty else 0,
        'away_avg_goals_scored': df[~df['is_home']]['goals_scored'].mean() if not df[~df['is_home']].empty else 0,
        'away_avg_goals_conceded': df[~df['is_home']]['goals_conceded'].mean() if not df[~df['is_home']].empty else 0,
        'win_rate': len(df[df['result'] == 'W']) / len(df) if len(df) > 0 else 0,
        'recent_form': ''.join(df.sort_values('date', ascending=False)['result'].head(5).tolist()),
        'match_results': df.to_dict('records')
    }
    
    # Add a list of match results for reference
    stats['match_history'] = df.sort_values('date', ascending=False)['match_info'].tolist()
    
    print(f"Calculated stats for {team_name} based on {len(df)} recent matches")
    if stats['recent_form']:
        print(f"Recent form: {stats['recent_form']}")
    
    return stats

def get_match_prediction_data(team_a, team_b):
    """
    Get all data needed for predicting match between team A and team B
    """
    # Get team IDs
    team_a_id, team_a_name = get_team_id(team_a)
    team_b_id, team_b_name = get_team_id(team_b)
    
    if not team_a_id or not team_b_id:
        return None
    
    # Get team stats from recent matches
    team_a_stats = get_team_stats(team_a_id, team_a_name)
    team_b_stats = get_team_stats(team_b_id, team_b_name)
    
    if (FETCH_RECENT_MATCHES and (not team_a_stats or not team_b_stats)):
        return None
    
    # If not fetching recent matches but stats are None, create default stats
    if not FETCH_RECENT_MATCHES:
        if not team_a_stats:
            team_a_stats = {
                'team_id': team_a_id,
                'team_name': team_a_name,
                'num_matches': 0,
                'match_history': []
            }
        if not team_b_stats:
            team_b_stats = {
                'team_id': team_b_id,
                'team_name': team_b_name,
                'num_matches': 0,
                'match_history': []
            }
    
    # Get head-to-head matches
    h2h_matches = get_head_to_head_matches(team_a_id, team_a_name, team_b_id, team_b_name)
    
    # If no H2H matches and we were supposed to fetch them, this is an issue
    if not h2h_matches and FETCH_H2H_MATCHES:
        print(f"No head-to-head matches found between {team_a_name} and {team_b_name}")
    
    if h2h_matches:
        # Calculate head-to-head stats for team A
        h2h_features = extract_match_features(h2h_matches, team_a_id)
        h2h_df = pd.DataFrame(h2h_features)
        
        if not h2h_df.empty:
            team_a_stats['h2h_avg_goals_scored'] = h2h_df['goals_scored'].mean()
            team_a_stats['h2h_avg_goals_conceded'] = h2h_df['goals_conceded'].mean()
            team_a_stats['h2h_win_rate'] = len(h2h_df[h2h_df['result'] == 'W']) / len(h2h_df)
            
            # Add a list of h2h match results for reference
            team_a_stats['h2h_history'] = h2h_df.sort_values('date', ascending=False)['match_info'].tolist()
        
        # For team B, the values are inverted
        team_b_stats['h2h_avg_goals_scored'] = team_a_stats.get('h2h_avg_goals_conceded', 0)
        team_b_stats['h2h_avg_goals_conceded'] = team_a_stats.get('h2h_avg_goals_scored', 0)
        team_b_stats['h2h_win_rate'] = 1 - team_a_stats.get('h2h_win_rate', 0)
        team_b_stats['h2h_history'] = team_a_stats.get('h2h_history', [])
    
    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'h2h_matches': h2h_matches
    }