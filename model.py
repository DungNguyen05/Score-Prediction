import numpy as np
from scipy.stats import poisson
import pandas as pd

def predict_goals(team_a_stats, team_b_stats, is_team_a_home=True):
    """
    Predict the expected goals for both teams using a simple Poisson model
    """
    # Base average goals calculation
    if is_team_a_home:
        team_a_exp_goals = team_a_stats['home_avg_goals_scored'] * (team_b_stats['away_avg_goals_conceded'] / team_b_stats['avg_goals_conceded'])
        team_b_exp_goals = team_b_stats['away_avg_goals_scored'] * (team_a_stats['home_avg_goals_conceded'] / team_a_stats['avg_goals_conceded'])
    else:
        team_a_exp_goals = team_a_stats['away_avg_goals_scored'] * (team_b_stats['home_avg_goals_conceded'] / team_b_stats['avg_goals_conceded'])
        team_b_exp_goals = team_b_stats['home_avg_goals_scored'] * (team_a_stats['away_avg_goals_conceded'] / team_a_stats['avg_goals_conceded'])
    
    # Add head-to-head adjustment if available
    if 'h2h_avg_goals_scored' in team_a_stats and 'h2h_avg_goals_scored' in team_b_stats:
        team_a_exp_goals = (team_a_exp_goals * 0.7) + (team_a_stats['h2h_avg_goals_scored'] * 0.3)
        team_b_exp_goals = (team_b_exp_goals * 0.7) + (team_b_stats['h2h_avg_goals_scored'] * 0.3)
    
    # Form adjustment (simple version)
    team_a_form_score = sum([1 if r == 'W' else 0.5 if r == 'D' else 0 for r in team_a_stats['recent_form']]) / 5 if team_a_stats['recent_form'] else 0.5
    team_b_form_score = sum([1 if r == 'W' else 0.5 if r == 'D' else 0 for r in team_b_stats['recent_form']]) / 5 if team_b_stats['recent_form'] else 0.5
    
    form_adjustment = (team_a_form_score - team_b_form_score) * 0.2
    team_a_exp_goals += form_adjustment
    team_b_exp_goals -= form_adjustment
    
    # Ensure positive values
    team_a_exp_goals = max(0.1, team_a_exp_goals)
    team_b_exp_goals = max(0.1, team_b_exp_goals)
    
    return team_a_exp_goals, team_b_exp_goals

def calculate_total_goals_probabilities(team_a_exp_goals, team_b_exp_goals, max_goals=7):
    """
    Calculate probability distribution for total goals in a match
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
        if max_goals in probabilities:
            probabilities[max_goals] += remaining
        else:
            probabilities[max_goals] = remaining
    
    # Convert to dataframe for easier display
    prob_df = pd.DataFrame({
        'total_goals': list(probabilities.keys()),
        'probability': list(probabilities.values())
    }).sort_values('total_goals')
    
    # Convert to percentages
    prob_df['probability'] = prob_df['probability'] * 100
    
    return prob_df

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
    
    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'team_a_expected_goals': team_a_exp_goals,
        'team_b_expected_goals': team_b_exp_goals, 
        'total_goals_probabilities': prob_table,
        'most_likely_total': prob_table.loc[prob_table['probability'].idxmax(), 'total_goals']
    }