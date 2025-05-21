import numpy as np
from scipy.stats import poisson
import pandas as pd

def predict_goals(team_a_stats, team_b_stats, is_neutral_venue=False):
    """
    Predict the expected goals for both teams using an enhanced Poisson model
    that prioritizes weighted recent performance and head-to-head history,
    with support for neutral venues.
    """
    # Use weighted goals statistics based on venue type
    if is_neutral_venue:
        # For neutral venue - use neutral venue stats if available, otherwise blend home/away
        if team_a_stats.get('neutral_avg_goals_scored', 0) > 0 and team_a_stats.get('num_neutral_matches', 0) >= 3:
            team_a_exp_goals = team_a_stats['neutral_avg_goals_scored'] * 0.8 + team_a_stats['weighted_goals_scored'] * 0.2
        else:
            # Blend home and away performance for neutral venue (with slight weight toward away performance)
            team_a_exp_goals = (team_a_stats['home_avg_goals_scored'] * 0.4) + (team_a_stats['away_avg_goals_scored'] * 0.6)
        
        if team_b_stats.get('neutral_avg_goals_scored', 0) > 0 and team_b_stats.get('num_neutral_matches', 0) >= 3:
            team_b_exp_goals = team_b_stats['neutral_avg_goals_scored'] * 0.8 + team_b_stats['weighted_goals_scored'] * 0.2
        else:
            # Blend home and away performance for neutral venue (with slight weight toward away performance)
            team_b_exp_goals = (team_b_stats['home_avg_goals_scored'] * 0.4) + (team_b_stats['away_avg_goals_scored'] * 0.6)
    else:
        # For Team A (home team)
        team_a_exp_goals = team_a_stats['home_avg_goals_scored'] * (team_b_stats['away_avg_goals_conceded'] / team_b_stats['weighted_goals_conceded'])
        # For Team B (away team)
        team_b_exp_goals = team_b_stats['away_avg_goals_scored'] * (team_a_stats['home_avg_goals_conceded'] / team_a_stats['weighted_goals_conceded'])
    
    # Add head-to-head adjustment with venue-appropriate weighting
    if 'h2h_avg_goals_scored' in team_a_stats and 'h2h_avg_goals_scored' in team_b_stats:
        if is_neutral_venue and 'h2h_neutral_avg_goals_scored' in team_a_stats and team_a_stats.get('h2h_neutral_matches', 0) >= 2:
            # Use neutral venue H2H stats with higher weight (50%) if we have enough neutral venue H2H matches
            team_a_exp_goals = (team_a_exp_goals * 0.5) + (team_a_stats['h2h_neutral_avg_goals_scored'] * 0.5)
            team_b_exp_goals = (team_b_exp_goals * 0.5) + (team_b_stats['h2h_neutral_avg_goals_scored'] * 0.5)
        else:
            # Use regular H2H stats with standard weight (40%)
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
    
    # Apply form adjustment (0.3 for standard venues, reduced to 0.2 for neutral venues)
    form_adjustment_weight = 0.2 if is_neutral_venue else 0.3
    form_adjustment = (team_a_form_score - team_b_form_score) * form_adjustment_weight
    team_a_exp_goals += form_adjustment
    team_b_exp_goals -= form_adjustment
    
    # Add home field advantage (only for non-neutral venues)
    if not is_neutral_venue:
        team_a_exp_goals *= 1.1  # 10% boost for home team
    
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

def predict_match(team_a_id, team_b_id, is_neutral_venue=False):
    """
    Main prediction function
    """
    from data_fetcher import get_match_prediction_data, get_team_name
    
    # Get team names for logging
    team_a_name = get_team_name(team_a_id)
    team_b_name = get_team_name(team_b_id)
    
    # Get all data needed for prediction
    prediction_data = get_match_prediction_data(team_a_id, team_b_id)
    
    if not prediction_data:
        return None
    
    # Get team stats
    team_a_stats = prediction_data['team_a']
    team_b_stats = prediction_data['team_b']
    
    # Calculate expected goals with venue consideration
    team_a_exp_goals, team_b_exp_goals = predict_goals(
        team_a_stats, team_b_stats, is_neutral_venue
    )
    
    print(f"Expected goals - {team_a_name}: {team_a_exp_goals:.2f}, {team_b_name}: {team_b_exp_goals:.2f}")
    
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
        'most_likely_score': score_probabilities.iloc[0]['score'] if not score_probabilities.empty else "Unknown",
        'is_neutral_venue': is_neutral_venue
    }