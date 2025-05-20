import numpy as np
from scipy.stats import poisson
import pandas as pd

def predict_goals(team_a_stats, team_b_stats, is_team_a_home=True):
    """
    Predict the expected goals for both teams using an enhanced Poisson model
    that prioritizes weighted recent performance and head-to-head history
    """
    # Use weighted goals statistics if available, otherwise fall back to regular averages
    if is_team_a_home:
        # For Team A (home team)
        team_a_exp_goals = team_a_stats['home_avg_goals_scored'] * (team_b_stats['away_avg_goals_conceded'] / team_b_stats['weighted_goals_conceded'])
        # For Team B (away team)
        team_b_exp_goals = team_b_stats['away_avg_goals_scored'] * (team_a_stats['home_avg_goals_conceded'] / team_a_stats['weighted_goals_conceded'])
    else:
        # For Team A (away team)
        team_a_exp_goals = team_a_stats['away_avg_goals_scored'] * (team_b_stats['home_avg_goals_conceded'] / team_b_stats['weighted_goals_conceded'])
        # For Team B (home team)
        team_b_exp_goals = team_b_stats['home_avg_goals_scored'] * (team_a_stats['away_avg_goals_conceded'] / team_a_stats['weighted_goals_conceded'])
    
    # Add head-to-head adjustment with increased weight (from 30% to 40%)
    if 'h2h_avg_goals_scored' in team_a_stats and 'h2h_avg_goals_scored' in team_b_stats:
        team_a_exp_goals = (team_a_exp_goals * 0.6) + (team_a_stats['h2h_avg_goals_scored'] * 0.4)
        team_b_exp_goals = (team_b_exp_goals * 0.6) + (team_b_stats['h2h_avg_goals_scored'] * 0.4)
    
    # Enhanced form adjustment using exponential weighting of recent results
    # Calculate form score with more weight to most recent matches
    team_a_form = team_a_stats['recent_form']
    team_b_form = team_b_stats['recent_form']
    
    # Weight recent matches more heavily (newest first)
    weights = [0.4, 0.25, 0.15, 0.1, 0.1]  # Sum = 1.0
    
    team_a_form_score = 0
    team_b_form_score = 0
    
    # Calculate weighted form scores
    for i, result in enumerate(team_a_form[:5]):
        if i < len(weights):
            team_a_form_score += weights[i] * (1.0 if result == 'W' else 0.5 if result == 'D' else 0.0)
    
    for i, result in enumerate(team_b_form[:5]):
        if i < len(weights):
            team_b_form_score += weights[i] * (1.0 if result == 'W' else 0.5 if result == 'D' else 0.0)
    
    # Apply form adjustment (increased from 0.2 to 0.3)
    form_adjustment = (team_a_form_score - team_b_form_score) * 0.3
    team_a_exp_goals += form_adjustment
    team_b_exp_goals -= form_adjustment
    
    # Add home field advantage
    if is_team_a_home:
        team_a_exp_goals *= 1.1  # 10% boost for home team
    else:
        team_b_exp_goals *= 1.1  # 10% boost for home team
    
    # Ensure positive values
    team_a_exp_goals = max(0.2, team_a_exp_goals)
    team_b_exp_goals = max(0.2, team_b_exp_goals)
    
    return team_a_exp_goals, team_b_exp_goals

def calculate_total_goals_probabilities(team_a_exp_goals, team_b_exp_goals, max_goals=10):
    """
    Calculate probability distribution for total goals in a match
    Extended to include more possible goals (up to 10 by default)
    """
    probabilities = {}
    
    # Calculate probabilities for each score combination
    total_probability = 0
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            home_prob = poisson.pmf(home_goals, team_a_exp_goals)
            away_prob = poisson.pmf(away_goals, team_b_exp_goals)
            
            total = home_goals + away_goals
            score_prob = home_prob * away_prob
            
            if total in probabilities:
                probabilities[total] += score_prob
            else:
                probabilities[total] = score_prob
            
            total_probability += score_prob
    
    # Add remaining probability to max_goals if needed
    if total_probability < 1:
        remaining = 1 - total_probability
        if max_goals * 2 in probabilities:
            probabilities[max_goals * 2] += remaining
        else:
            probabilities[max_goals * 2] = remaining
    
    # Convert to dataframe for easier display
    prob_df = pd.DataFrame({
        'total_goals': list(probabilities.keys()),
        'probability': list(probabilities.values())
    }).sort_values('total_goals')
    
    # Convert to percentages
    prob_df['probability'] = prob_df['probability'] * 100
    
    return prob_df

def calculate_score_probabilities(team_a_exp_goals, team_b_exp_goals, max_goals=5):
    """
    Calculate probability distribution for specific scores
    """
    probabilities = []
    
    # Calculate probabilities for each score combination
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            home_prob = poisson.pmf(home_goals, team_a_exp_goals)
            away_prob = poisson.pmf(away_goals, team_b_exp_goals)
            
            score_prob = home_prob * away_prob
            
            probabilities.append({
                'home_goals': home_goals,
                'away_goals': away_goals,
                'score': f"{home_goals}-{away_goals}",
                'probability': score_prob * 100  # Convert to percentage
            })
    
    # Convert to dataframe and sort by probability (descending)
    prob_df = pd.DataFrame(probabilities).sort_values('probability', ascending=False)
    
    # Return top 10 most likely scores
    return prob_df.head(10)

def predict_match(team_a, team_b, is_team_a_home=True):
    """
    Main prediction function
    """
    from data_fetcher import get_match_prediction_data
    
    # Get all data needed for prediction
    prediction_data = get_match_prediction_data(team_a, team_b)
    
    if not prediction_data:
        return None
    
    # Get team stats
    team_a_stats = prediction_data['team_a']
    team_b_stats = prediction_data['team_b']
    
    # Calculate expected goals
    team_a_exp_goals, team_b_exp_goals = predict_goals(
        team_a_stats, team_b_stats, is_team_a_home
    )
    
    print(f"Expected goals - {team_a_stats['team_name']}: {team_a_exp_goals:.2f}, {team_b_stats['team_name']}: {team_b_exp_goals:.2f}")
    
    # Get total goals probability table
    prob_table = calculate_total_goals_probabilities(team_a_exp_goals, team_b_exp_goals)
    
    # Calculate score probabilities for most likely scores
    score_probabilities = calculate_score_probabilities(team_a_exp_goals, team_b_exp_goals)
    
    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'team_a_expected_goals': team_a_exp_goals,
        'team_b_expected_goals': team_b_exp_goals, 
        'total_goals_probabilities': prob_table,
        'score_probabilities': score_probabilities,
        'most_likely_total': prob_table.loc[prob_table['probability'].idxmax(), 'total_goals'],
        'most_likely_score': score_probabilities.iloc[0]['score'] if not score_probabilities.empty else "Unknown"
    }