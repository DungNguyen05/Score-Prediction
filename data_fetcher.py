import requests
import pandas as pd
from datetime import datetime, timedelta
from config import API_KEY, BASE_URL, HEADERS, HISTORY_MATCHES, SEASONS_TO_ANALYZE

def get_team_id(team_name):
    """
    Get team ID by searching for the team name
    """
    search_url = f"{BASE_URL}/teams"
    
    try:
        response = requests.get(search_url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("teams", [])
            
            # Search for team by name (case-insensitive partial match)
            team_name_lower = team_name.lower()
            for team in teams:
                if team_name_lower in team['name'].lower():
                    return team['id'], team['name']
            
            print(f"Team not found: {team_name}")
            return None, None
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def get_team_matches(team_id, limit=HISTORY_MATCHES):
    """
    Get recent matches for a team
    """
    # Calculate date for filtering (e.g., matches in the last SEASONS_TO_ANALYZE seasons)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * SEASONS_TO_ANALYZE)
    
    # Format dates for API
    date_from = start_date.strftime("%Y-%m-%d")
    date_to = end_date.strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/teams/{team_id}/matches"
    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "status": "FINISHED",
        "limit": limit
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            return response.json()['matches']
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_head_to_head(team_a_id, team_b_id, limit=10):
    """
    Get head-to-head matches between two teams
    """
    url = f"{BASE_URL}/teams/{team_a_id}/matches"
    params = {
        "status": "FINISHED",
        "limit": 100  # Get more to find head-to-head matches
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            
            # Filter only matches between the two teams
            h2h_matches = []
            for match in matches:
                home_id = match['homeTeam']['id']
                away_id = match['awayTeam']['id']
                
                if (home_id == team_a_id and away_id == team_b_id) or \
                   (home_id == team_b_id and away_id == team_a_id):
                    h2h_matches.append(match)
            
            # Sort by date (most recent first) and limit
            h2h_matches.sort(key=lambda x: x['utcDate'], reverse=True)
            return h2h_matches[:limit]
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"An error occurred: {e}")
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
        
        # Competition info
        competition = match['competition']['name']
        
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
            'competition': competition,
            'is_home': is_home,
            'opponent_id': opponent_id,
            'opponent_name': opponent_name,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'total_goals': goals_scored + goals_conceded,
            'result': result
        })
    
    return features

def get_team_stats(team_name):
    """
    Get comprehensive stats for a team
    """
    team_id, full_team_name = get_team_id(team_name)
    
    if not team_id:
        return None
    
    matches = get_team_matches(team_id)
    if not matches:
        return None
    
    features = extract_match_features(matches, team_id)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(features)
    
    # Calculate aggregated stats
    stats = {
        'team_id': team_id,
        'team_name': full_team_name,
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
        'recent_matches': df.sort_values('date', ascending=False).to_dict('records')
    }
    
    return stats

def get_match_prediction_data(team_a, team_b):
    """
    Get all data needed for predicting match between team A and team B
    """
    # Get stats for both teams
    team_a_stats = get_team_stats(team_a)
    team_b_stats = get_team_stats(team_b)
    
    if not team_a_stats or not team_b_stats:
        return None
    
    # Get head-to-head matches
    h2h_matches = get_head_to_head(team_a_stats['team_id'], team_b_stats['team_id'])
    
    h2h_features = []
    if h2h_matches:
        # Calculate head-to-head stats for team A
        h2h_features = extract_match_features(h2h_matches, team_a_stats['team_id'])
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