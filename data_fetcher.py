import requests
import pandas as pd
from datetime import datetime

from config import API_KEY, BASE_URL, HEADERS, MATCHES_TO_CONSIDER, TEAM_IDS

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

def get_competition_matches(competition_id=2014):  # Default to La Liga
    """
    Get recent matches from a competition (free tier compatible)
    """
    url = f"{BASE_URL}/competitions/{competition_id}/matches"
    
    params = {
        "status": "FINISHED",
        "limit": 100  # Get a good number of matches
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            print(f"Found {len(matches)} matches from competition {competition_id}")
            return matches
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def filter_team_matches(all_matches, team_id, limit=MATCHES_TO_CONSIDER):
    """
    Filter matches for a specific team from a list of all matches
    """
    team_matches = []
    
    for match in all_matches:
        home_id = match['homeTeam']['id']
        away_id = match['awayTeam']['id']
        
        if home_id == team_id or away_id == team_id:
            team_matches.append(match)
    
    # Sort by date (most recent first) and limit
    team_matches.sort(key=lambda x: x['utcDate'], reverse=True)
    return team_matches[:limit]

def get_head_to_head(all_matches, team_a_id, team_b_id, limit=10):
    """
    Filter head-to-head matches between two teams from list of all matches
    """
    h2h_matches = []
    
    for match in all_matches:
        home_id = match['homeTeam']['id']
        away_id = match['awayTeam']['id']
        
        if (home_id == team_a_id and away_id == team_b_id) or \
           (home_id == team_b_id and away_id == team_a_id):
            h2h_matches.append(match)
    
    # Sort by date (most recent first) and limit
    h2h_matches.sort(key=lambda x: x['utcDate'], reverse=True)
    print(f"Found {len(h2h_matches)} head-to-head matches between the teams")
    return h2h_matches[:limit]

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
        
        features.append({
            'match_id': match['id'],
            'date': match_date,
            'is_home': is_home,
            'opponent_id': opponent_id,
            'opponent_name': opponent_name,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'total_goals': goals_scored + goals_conceded,
            'result': result
        })
    
    return features

def get_team_stats(all_matches, team_id, team_name):
    """
    Calculate team statistics from match data
    """
    # Filter matches for this team
    team_matches = filter_team_matches(all_matches, team_id)
    
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
    
    print(f"Calculated stats for {team_name} based on {len(df)} matches")
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
    
    # For La Liga (if both teams are Spanish)
    competitions = [2014]  # Start with La Liga
    
    # If teams might be from different leagues, add more competitions
    if team_a_id not in [86, 81, 78, 559] or team_b_id not in [86, 81, 78, 559]:
        competitions.extend([2021, 2019, 2002])  # Premier League, Serie A, Bundesliga
    
    # Add Champions League for coverage of international matches
    competitions.append(2001)
    
    # Get matches from competitions
    all_matches = []
    for comp_id in competitions:
        matches = get_competition_matches(comp_id)
        all_matches.extend(matches)
        
    # Remove duplicates
    match_ids = set()
    unique_matches = []
    for match in all_matches:
        if match['id'] not in match_ids:
            match_ids.add(match['id'])
            unique_matches.append(match)
    
    print(f"Collected {len(unique_matches)} unique matches from {len(competitions)} competitions")
    
    # Get team stats
    team_a_stats = get_team_stats(unique_matches, team_a_id, team_a_name)
    team_b_stats = get_team_stats(unique_matches, team_b_id, team_b_name)
    
    if not team_a_stats or not team_b_stats:
        return None
    
    # Get head-to-head
    h2h_matches = get_head_to_head(unique_matches, team_a_id, team_b_id)
    
    if h2h_matches:
        # Calculate head-to-head stats for team A
        h2h_features = extract_match_features(h2h_matches, team_a_id)
        h2h_df = pd.DataFrame(h2h_features)
        
        if not h2h_df.empty:
            team_a_stats['h2h_avg_goals_scored'] = h2h_df['goals_scored'].mean()
            team_a_stats['h2h_avg_goals_conceded'] = h2h_df['goals_conceded'].mean()
            team_a_stats['h2h_win_rate'] = len(h2h_df[h2h_df['result'] == 'W']) / len(h2h_df)
        
        # For team B, the values are inverted
        team_b_stats['h2h_avg_goals_scored'] = team_a_stats.get('h2h_avg_goals_conceded', 0)
        team_b_stats['h2h_avg_goals_conceded'] = team_a_stats.get('h2h_avg_goals_scored', 0)
        team_b_stats['h2h_win_rate'] = 1 - team_a_stats.get('h2h_win_rate', 0)
    
    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'h2h_matches': h2h_matches
    }