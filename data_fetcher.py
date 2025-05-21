import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta

from config import (
    API_KEY, BASE_URL, HEADERS, 
    MATCHES_TO_CONSIDER, MAX_H2H_MATCHES,
    CACHE_MAX_AGE
)

# Create a cache directory if it doesn't exist
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_team_name(team_id):
    """
    Get team name from API using team ID
    """
    # Try to get from cache first
    cache_key = f"team_name_{team_id}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return cached_data
    
    # Not in cache, fetch from API
    url = f"{BASE_URL}/teams/{team_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            team_name = data.get("name", f"Team ID: {team_id}")
            
            # Save to cache
            save_to_cache(cache_key, team_name)
            
            return team_name
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return f"Team ID: {team_id}"
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Team ID: {team_id}"

def get_cached_data(cache_key, max_age_hours=CACHE_MAX_AGE):
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

def get_recent_team_matches(team_id, limit=MATCHES_TO_CONSIDER):
    """
    Get the most recent matches for a specific team directly
    """
    # Get team name for logging purposes
    team_name = get_team_name(team_id)
    
    # Try to get from cache first
    cache_key = f"team_matches_{team_id}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        matches = cached_data
        print(f"Using cached data: Found {len(matches)} recent matches for {team_name}")
        return matches
    
    # Not in cache, fetch from API
    url = f"{BASE_URL}/teams/{team_id}/matches"
    
    # Get more matches than we need so we can filter by competitiveness later
    api_limit = min(limit * 2, 100)  # Double the limit but stay within API constraints
    
    params = {
        "status": "FINISHED",
        "limit": api_limit,
        "sort": "date",  # Get matches sorted by date
        "direction": "desc"  # Most recent first
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_matches = data.get("matches", [])
            print(f"Found {len(all_matches)} recent matches for {team_name}")
            
            # Filter out friendlies and less important competitions
            competitive_matches = filter_competitive_matches(all_matches)
            
            # Take only the needed number of matches
            matches = competitive_matches[:limit]
            
            # Save to cache
            save_to_cache(cache_key, matches)
            
            return matches
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def filter_competitive_matches(matches, max_age_days=365):
    """
    Filter matches to include only competitive games and recent ones
    """
    # Define which competitions are considered more competitive/important
    top_competition_ids = [
        2001,  # Champions League
        2002,  # Europa League
        2019,  # Premier League
        2014,  # La Liga
        2021,  # Serie A
        2015,  # Ligue 1
        2002,  # Bundesliga
        2000,  # World Cup
        2018,  # European Championship
    ]
    
    # Filter by date - only include matches within the last year
    now = datetime.now()
    date_threshold = now - timedelta(days=max_age_days)
    
    # Start with competitive matches from top leagues/competitions
    competitive_matches = []
    other_matches = []
    
    for match in matches:
        match_date = datetime.strptime(match['utcDate'][:10], '%Y-%m-%d')
        
        # Skip if match is too old
        if match_date < date_threshold:
            continue
            
        # Prioritize matches from top competitions
        competition_id = match.get('competition', {}).get('id')
        
        if competition_id in top_competition_ids:
            competitive_matches.append(match)
        else:
            # Skip friendlies completely
            competition_type = match.get('competition', {}).get('type')
            if competition_type != 'FRIENDLY':
                other_matches.append(match)
    
    # Combine the lists, prioritizing competitive matches
    return competitive_matches + other_matches

def get_head_to_head_matches(team_a_id, team_b_id, limit=MAX_H2H_MATCHES):
    """
    Get head-to-head matches between two teams
    """
    # Get team names for logging purposes
    team_a_name = get_team_name(team_a_id)
    team_b_name = get_team_name(team_b_id)
    
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
        is_away = match['awayTeam']['id'] == team_id
        is_neutral = match.get('venue', {}).get('neutral', False)
        
        # Skip if the team is not in this match
        if not (is_home or is_away):
            continue
            
        # Get team scores
        home_score = match['score']['fullTime']['home'] or 0
        away_score = match['score']['fullTime']['away'] or 0
        
        # Date
        match_date = datetime.strptime(match['utcDate'][:10], '%Y-%m-%d')
        
        # Calculate match recency (0 to 1, where 1 is most recent)
        days_ago = (datetime.now() - match_date).days
        recency_score = max(0, 1 - (days_ago / 365))  # Scale from 0 to 1 based on days ago (max 1 year)
        
        # Goals scored and conceded
        goals_scored = home_score if is_home else away_score
        goals_conceded = away_score if is_home else home_score
        
        # Opponent
        opponent_id = match['awayTeam']['id'] if is_home else match['homeTeam']['id']
        opponent_name = match['awayTeam']['name'] if is_home else match['homeTeam']['name']
        
        # Competition importance (higher value for more important competitions)
        competition_id = match.get('competition', {}).get('id', 0)
        competition_importance = get_competition_importance(competition_id)
        
        # Result (win, draw, loss)
        if home_score > away_score:
            result = 'W' if is_home else 'L'
        elif home_score < away_score:
            result = 'L' if is_home else 'W'
        else:
            result = 'D'
        
        # Match info for reference
        match_info = f"{match_date.strftime('%Y-%m-%d')} - "
        if is_neutral:
            match_info += f"{match['homeTeam']['name']} {home_score}-{away_score} {match['awayTeam']['name']} (Neutral)"
        else:
            match_info += f"{match['homeTeam']['name']} {home_score}-{away_score} {match['awayTeam']['name']}"
        
        # Add competition name if available
        competition_name = match.get('competition', {}).get('name', '')
        if competition_name:
            match_info += f" ({competition_name})"
        
        features.append({
            'match_id': match['id'],
            'date': match_date,
            'is_home': is_home,
            'is_away': is_away,
            'is_neutral': is_neutral,
            'opponent_id': opponent_id,
            'opponent_name': opponent_name,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'total_goals': goals_scored + goals_conceded,
            'result': result,
            'match_info': match_info,
            'recency_score': recency_score,
            'competition_importance': competition_importance
        })
    
    return features

def get_competition_importance(competition_id):
    """
    Assign an importance value to different competitions
    Higher value means more important competition
    """
    # Define importance levels for different competitions
    top_competitions = {
        2001: 1.0,  # Champions League
        2002: 0.9,  # Europa League
        2019: 0.8,  # Premier League
        2014: 0.8,  # La Liga
        2021: 0.8,  # Serie A
        2015: 0.75, # Ligue 1
        2002: 0.8,  # Bundesliga
        2000: 1.0,  # World Cup
        2018: 0.9,  # European Championship
    }
    
    # Return importance or default value for other competitions
    return top_competitions.get(competition_id, 0.6)

def get_team_stats(team_id):
    """
    Calculate team statistics from recent match data with improved focus on recency
    """
    # Get team name for logging
    team_name = get_team_name(team_id)
    
    # Get recent matches for this team
    team_matches = get_recent_team_matches(team_id)
    
    if not team_matches:
        print(f"No matches found for {team_name}")
        return None
    
    # Extract features
    features = extract_match_features(team_matches, team_id)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(features)
    
    if df.empty:
        print(f"No features extracted for {team_name}")
        return None
    
    # Apply recency weighting to the data
    df['weight'] = df['recency_score'] * df['competition_importance']
    total_weight = df['weight'].sum()
    
    # Calculate weighted statistics
    if total_weight > 0:
        weighted_goals_scored = (df['goals_scored'] * df['weight']).sum() / total_weight
        weighted_goals_conceded = (df['goals_conceded'] * df['weight']).sum() / total_weight
        
        # Home/away specific weighted stats
        home_df = df[df['is_home'] & ~df['is_neutral']]
        away_df = df[df['is_away'] & ~df['is_neutral']]
        neutral_df = df[df['is_neutral']]
        
        home_weight = home_df['weight'].sum() if not home_df.empty else 0
        away_weight = away_df['weight'].sum() if not away_df.empty else 0
        neutral_weight = neutral_df['weight'].sum() if not neutral_df.empty else 0
        
        home_weighted_goals_scored = (home_df['goals_scored'] * home_df['weight']).sum() / home_weight if home_weight > 0 else 0
        home_weighted_goals_conceded = (home_df['goals_conceded'] * home_df['weight']).sum() / home_weight if home_weight > 0 else 0
        away_weighted_goals_scored = (away_df['goals_scored'] * away_df['weight']).sum() / away_weight if away_weight > 0 else 0
        away_weighted_goals_conceded = (away_df['goals_conceded'] * away_df['weight']).sum() / away_weight if away_weight > 0 else 0
        neutral_weighted_goals_scored = (neutral_df['goals_scored'] * neutral_df['weight']).sum() / neutral_weight if neutral_weight > 0 else 0
        neutral_weighted_goals_conceded = (neutral_df['goals_conceded'] * neutral_df['weight']).sum() / neutral_weight if neutral_weight > 0 else 0
    else:
        # Fallback to simple average if no weights
        weighted_goals_scored = df['goals_scored'].mean()
        weighted_goals_conceded = df['goals_conceded'].mean()
        
        home_df = df[df['is_home'] & ~df['is_neutral']]
        away_df = df[df['is_away'] & ~df['is_neutral']]
        neutral_df = df[df['is_neutral']]
        
        home_weighted_goals_scored = home_df['goals_scored'].mean() if not home_df.empty else 0
        home_weighted_goals_conceded = home_df['goals_conceded'].mean() if not home_df.empty else 0
        away_weighted_goals_scored = away_df['goals_scored'].mean() if not away_df.empty else 0
        away_weighted_goals_conceded = away_df['goals_conceded'].mean() if not away_df.empty else 0
        neutral_weighted_goals_scored = neutral_df['goals_scored'].mean() if not neutral_df.empty else 0
        neutral_weighted_goals_conceded = neutral_df['goals_conceded'].mean() if not neutral_df.empty else 0
    
    # Calculate weighted win rate
    if total_weight > 0:
        win_df = df[df['result'] == 'W']
        weighted_win_rate = (win_df['weight'].sum() / total_weight) if not win_df.empty else 0
    else:
        weighted_win_rate = len(df[df['result'] == 'W']) / len(df) if len(df) > 0 else 0
    
    # Calculate neutral venue win rate separately
    if not neutral_df.empty and neutral_weight > 0:
        neutral_win_df = neutral_df[neutral_df['result'] == 'W']
        neutral_weighted_win_rate = (neutral_win_df['weight'].sum() / neutral_weight) if not neutral_win_df.empty else 0
    else:
        neutral_weighted_win_rate = 0
    
    # Calculate aggregated stats
    stats = {
        'team_id': team_id,
        'team_name': team_name,
        'num_matches': len(df),
        'num_home_matches': len(home_df),
        'num_away_matches': len(away_df),
        'num_neutral_matches': len(neutral_df),
        'avg_goals_scored': df['goals_scored'].mean(),  # Keep simple average for reference
        'avg_goals_conceded': df['goals_conceded'].mean(),
        'avg_total_goals': df['total_goals'].mean(),
        'weighted_goals_scored': weighted_goals_scored,  # New weighted metrics
        'weighted_goals_conceded': weighted_goals_conceded,
        'home_avg_goals_scored': home_weighted_goals_scored,
        'home_avg_goals_conceded': home_weighted_goals_conceded,
        'away_avg_goals_scored': away_weighted_goals_scored,
        'away_avg_goals_conceded': away_weighted_goals_conceded,
        'neutral_avg_goals_scored': neutral_weighted_goals_scored,
        'neutral_avg_goals_conceded': neutral_weighted_goals_conceded,
        'win_rate': weighted_win_rate,
        'neutral_win_rate': neutral_weighted_win_rate,
        'recent_form': ''.join(df.sort_values('date', ascending=False)['result'].head(5).tolist()),
        'match_results': df.to_dict('records')
    }
    
    # Add a list of match results for reference
    stats['match_history'] = df.sort_values('date', ascending=False)['match_info'].tolist()
    
    print(f"Calculated stats for {team_name} based on {len(df)} recent matches")
    if stats['recent_form']:
        print(f"Recent form: {stats['recent_form']}")
    
    return stats

def get_match_prediction_data(team_a_id, team_b_id):
    """
    Get all data needed for predicting match between team A and team B
    """
    # Get team names for logging
    team_a_name = get_team_name(team_a_id)
    team_b_name = get_team_name(team_b_id)
    
    # Get team stats from recent matches
    team_a_stats = get_team_stats(team_a_id)
    team_b_stats = get_team_stats(team_b_id)
    
    if not team_a_stats or not team_b_stats:
        return None
    
    # Get head-to-head matches
    h2h_matches = get_head_to_head_matches(team_a_id, team_b_id)
    
    if not h2h_matches:
        print(f"No head-to-head matches found between {team_a_name} and {team_b_name}")
    
    if h2h_matches:
        # Calculate head-to-head stats for team A
        h2h_features = extract_match_features(h2h_matches, team_a_id)
        h2h_df = pd.DataFrame(h2h_features)
        
        if not h2h_df.empty:
            # Apply recency weighting to H2H matches
            h2h_df['weight'] = h2h_df['recency_score'] * h2h_df['competition_importance']
            total_h2h_weight = h2h_df['weight'].sum()
            
            # Track neutral venue H2H matches
            neutral_h2h_df = h2h_df[h2h_df['is_neutral']]
            neutral_h2h_weight = neutral_h2h_df['weight'].sum() if not neutral_h2h_df.empty else 0
            
            if total_h2h_weight > 0:
                # Weighted H2H stats
                team_a_stats['h2h_avg_goals_scored'] = (h2h_df['goals_scored'] * h2h_df['weight']).sum() / total_h2h_weight
                team_a_stats['h2h_avg_goals_conceded'] = (h2h_df['goals_conceded'] * h2h_df['weight']).sum() / total_h2h_weight
                
                win_h2h_df = h2h_df[h2h_df['result'] == 'W']
                team_a_stats['h2h_win_rate'] = (win_h2h_df['weight'].sum() / total_h2h_weight) if not win_h2h_df.empty else 0
                
                # Add neutral venue specific H2H stats if available
                if neutral_h2h_weight > 0:
                    neutral_win_h2h_df = neutral_h2h_df[neutral_h2h_df['result'] == 'W']
                    team_a_stats['h2h_neutral_win_rate'] = (neutral_win_h2h_df['weight'].sum() / neutral_h2h_weight) if not neutral_win_h2h_df.empty else 0
                    team_a_stats['h2h_neutral_avg_goals_scored'] = (neutral_h2h_df['goals_scored'] * neutral_h2h_df['weight']).sum() / neutral_h2h_weight
                    team_a_stats['h2h_neutral_avg_goals_conceded'] = (neutral_h2h_df['goals_conceded'] * neutral_h2h_df['weight']).sum() / neutral_h2h_weight
            else:
                # Fallback to simple average if no weights
                team_a_stats['h2h_avg_goals_scored'] = h2h_df['goals_scored'].mean()
                team_a_stats['h2h_avg_goals_conceded'] = h2h_df['goals_conceded'].mean()
                team_a_stats['h2h_win_rate'] = len(h2h_df[h2h_df['result'] == 'W']) / len(h2h_df)
                
                # Add neutral venue specific H2H stats if available
                if not neutral_h2h_df.empty:
                    team_a_stats['h2h_neutral_win_rate'] = len(neutral_h2h_df[neutral_h2h_df['result'] == 'W']) / len(neutral_h2h_df)
                    team_a_stats['h2h_neutral_avg_goals_scored'] = neutral_h2h_df['goals_scored'].mean()
                    team_a_stats['h2h_neutral_avg_goals_conceded'] = neutral_h2h_df['goals_conceded'].mean()
            
            # Add a list of h2h match results for reference
            team_a_stats['h2h_history'] = h2h_df.sort_values('date', ascending=False)['match_info'].tolist()
            
            # Count neutral venue h2h matches
            team_a_stats['h2h_neutral_matches'] = len(neutral_h2h_df)
        
        # For team B, the values are inverted
        team_b_stats['h2h_avg_goals_scored'] = team_a_stats.get('h2h_avg_goals_conceded', 0)
        team_b_stats['h2h_avg_goals_conceded'] = team_a_stats.get('h2h_avg_goals_scored', 0)
        team_b_stats['h2h_win_rate'] = 1 - team_a_stats.get('h2h_win_rate', 0)
        team_b_stats['h2h_history'] = team_a_stats.get('h2h_history', [])
        
        # For neutral venue h2h stats (if available)
        if 'h2h_neutral_win_rate' in team_a_stats:
            team_b_stats['h2h_neutral_win_rate'] = 1 - team_a_stats.get('h2h_neutral_win_rate', 0)
            team_b_stats['h2h_neutral_avg_goals_scored'] = team_a_stats.get('h2h_neutral_avg_goals_conceded', 0)
            team_b_stats['h2h_neutral_avg_goals_conceded'] = team_a_stats.get('h2h_neutral_avg_goals_scored', 0)
            team_b_stats['h2h_neutral_matches'] = team_a_stats.get('h2h_neutral_matches', 0)
    
    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'h2h_matches': h2h_matches
    }