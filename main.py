#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Soccer Match Score Predictor
This script predicts the total goals in a soccer match between two teams
using historical data from the football-data.org API with enhanced recency weighting
and support for neutral venues
"""

import pandas as pd
from model import predict_match
from config import HOME_TEAM_ID, AWAY_TEAM_ID, IS_NEUTRAL_VENUE, MATCHES_TO_CONSIDER
from data_fetcher import get_team_name

def format_probability_table(prob_table):
    """Format the probability table for display"""
    # Round to 2 decimal places and sort
    formatted = prob_table.copy()
    formatted['probability'] = formatted['probability'].round(2)
    formatted = formatted.sort_values('total_goals')
    
    # Format for display
    return formatted.rename(columns={
        'total_goals': 'Total Goals',
        'probability': 'Probability (%)'
    })

def format_score_probability_table(prob_table):
    """Format the score probability table for display"""
    # Round to 2 decimal places
    formatted = prob_table.copy()
    formatted['probability'] = formatted['probability'].round(2)
    
    # Format for display
    return formatted.rename(columns={
        'score': 'Score',
        'probability': 'Probability (%)'
    })[['Score', 'Probability (%)']]

def print_team_stats(team_stats, venue_label):
    """Print detailed team statistics"""
    team_name = team_stats['team_name']
    
    print(f"\n{team_name} ({venue_label}) Statistics:")
    print("-" * 40)
    print(f"Recent form: {team_stats['recent_form']}")
    print(f"Win rate: {team_stats['win_rate']:.2f}")
    
    # Print venue-specific averages
    if venue_label == "Home":
        print(f"Home average goals scored: {team_stats['home_avg_goals_scored']:.2f}")
        print(f"Home average goals conceded: {team_stats['home_avg_goals_conceded']:.2f}")
    elif venue_label == "Away":
        print(f"Away average goals scored: {team_stats['away_avg_goals_scored']:.2f}")
        print(f"Away average goals conceded: {team_stats['away_avg_goals_conceded']:.2f}")
    else:  # Neutral
        # Print neutral venue stats if available
        if team_stats.get('neutral_avg_goals_scored', 0) > 0:
            print(f"Neutral venue average goals scored: {team_stats['neutral_avg_goals_scored']:.2f}")
            print(f"Neutral venue average goals conceded: {team_stats['neutral_avg_goals_conceded']:.2f}")
            print(f"Neutral venue match count: {team_stats['num_neutral_matches']}")
        else:
            print("No neutral venue statistics available")
            print(f"Using blended home/away statistics:")
            print(f"  Home average goals scored: {team_stats['home_avg_goals_scored']:.2f}")
            print(f"  Away average goals scored: {team_stats['away_avg_goals_scored']:.2f}")
    
    # Print head-to-head stats if available
    if 'h2h_avg_goals_scored' in team_stats:
        print(f"H2H average goals scored: {team_stats['h2h_avg_goals_scored']:.2f}")
        print(f"H2H average goals conceded: {team_stats['h2h_avg_goals_conceded']:.2f}")
        print(f"H2H win rate: {team_stats['h2h_win_rate']:.2f}")
        
        # Print neutral venue H2H stats if available
        if venue_label == "Neutral" and 'h2h_neutral_win_rate' in team_stats:
            print(f"H2H neutral venue win rate: {team_stats['h2h_neutral_win_rate']:.2f}")
            if team_stats.get('h2h_neutral_matches', 0) > 0:
                print(f"H2H neutral venue matches: {team_stats['h2h_neutral_matches']}")
                print(f"H2H neutral venue average goals scored: {team_stats['h2h_neutral_avg_goals_scored']:.2f}")
    
    # Print the most recent matches
    print("\nRecent match history:")
    for i, match in enumerate(team_stats.get('match_history', [])[:5]):
        print(f"  {i+1}. {match}")
    
    # Print head-to-head history if available
    if 'h2h_history' in team_stats and team_stats['h2h_history']:
        print("\nHead-to-head history:")
        h2h_count = min(len(team_stats['h2h_history']), 10)  # Show up to 10 H2H matches
        for i, match in enumerate(team_stats['h2h_history'][:h2h_count]):
            print(f"  {i+1}. {match}")

def main():
    """Main function to run the prediction"""
    # Use the configured team IDs from config.py
    team_a_id = HOME_TEAM_ID
    team_b_id = AWAY_TEAM_ID
    is_neutral_venue = IS_NEUTRAL_VENUE
    
    # Get team names for display
    team_a_name = get_team_name(team_a_id)
    team_b_name = get_team_name(team_b_id)
    
    # Print match settings
    if is_neutral_venue:
        print(f"Predicting match at neutral venue: {team_a_name} vs {team_b_name}")
    else:
        print(f"Predicting match: {team_a_name} (Home) vs {team_b_name} (Away)")
    
    print("=" * 70)
    print(f"Using enhanced prediction model with recency-weighted stats")
    print(f"To change teams, edit HOME_TEAM_ID and AWAY_TEAM_ID in config.py")
    print(f"Analyzing up to {MATCHES_TO_CONSIDER} recent matches for each team")
    print(f"Venue setting: {'Neutral venue' if is_neutral_venue else 'Standard home/away'}")
    print("Loading data and calculating predictions...")
    
    # Make prediction
    prediction = predict_match(team_a_id, team_b_id, is_neutral_venue)
    
    if not prediction:
        print("Could not make a prediction. Please check team IDs in config.py and try again.")
        return
    
    # Display results
    print("\nMatch Prediction Results:")
    print("=" * 70)
    
    team_a_name = prediction['team_a']['team_name']
    team_b_name = prediction['team_b']['team_name']
    
    if is_neutral_venue:
        print(f"{team_a_name} vs {team_b_name} (Neutral Venue)")
    else:
        print(f"{team_a_name} (Home) vs {team_b_name} (Away)")
    
    print(f"Expected goals: {prediction['team_a_expected_goals']:.2f} - {prediction['team_b_expected_goals']:.2f}")
    print(f"Most likely score: {prediction['most_likely_score']}")
    print(f"Most likely total goals: {prediction['most_likely_total']}")
    
    # Display detailed statistics with appropriate venue labels
    if is_neutral_venue:
        print_team_stats(prediction['team_a'], "Neutral")
        print_team_stats(prediction['team_b'], "Neutral")
    else:
        print_team_stats(prediction['team_a'], "Home")
        print_team_stats(prediction['team_b'], "Away")
    
    print("\nMost Likely Scores:")
    print("-" * 40)
    
    # Display the score probability table
    if 'score_probabilities' in prediction:
        score_table = format_score_probability_table(prediction['score_probabilities'].head(5))
        pd.set_option('display.max_rows', None)
        print(score_table.to_string(index=False))
    
    print("\nTotal Goals Probability Table:")
    print("-" * 40)
    
    # Display the probability table
    prob_table = format_probability_table(prediction['total_goals_probabilities'])
    pd.set_option('display.max_rows', None)
    print(prob_table.to_string(index=False))
    
    print("\nNote: This prediction uses a recency-weighted model that prioritizes:")
    print("      - Most recent matches (with exponential decay for older matches)")
    print("      - Competitive matches over friendlies")
    print("      - Head-to-head history (with stronger weight to recent encounters)")
    print("      - Team form (with extra weight to most recent results)")
    
    if is_neutral_venue:
        print("      - Neutral venue adjustment (using neutral venue data when available)")
    else:
        print("      - Home field advantage (10% boost to expected goals)")
    
    print("\n      To predict for different teams, edit the HOME_TEAM_ID and AWAY_TEAM_ID values in config.py")
    print("      To set a neutral venue match, set IS_NEUTRAL_VENUE = True in config.py")

if __name__ == "__main__":
    main()