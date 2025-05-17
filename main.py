#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Soccer Match Score Predictor
This script predicts the total goals in a soccer match between two teams
using historical data from the football-data.org API
"""

import pandas as pd
from model import predict_match
from config import HOME_TEAM, AWAY_TEAM, MATCHES_TO_CONSIDER

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

def print_team_stats(team_stats, is_home=True):
    """Print detailed team statistics"""
    team_name = team_stats['team_name']
    location = "Home" if is_home else "Away"
    
    print(f"\n{team_name} ({location}) Statistics:")
    print("-" * 40)
    print(f"Recent form: {team_stats['recent_form']}")
    print(f"Win rate: {team_stats['win_rate']:.2f}")
    
    # Print relevant averages
    if is_home:
        print(f"Home average goals scored: {team_stats['home_avg_goals_scored']:.2f}")
        print(f"Home average goals conceded: {team_stats['home_avg_goals_conceded']:.2f}")
    else:
        print(f"Away average goals scored: {team_stats['away_avg_goals_scored']:.2f}")
        print(f"Away average goals conceded: {team_stats['away_avg_goals_conceded']:.2f}")
    
    # Print head-to-head stats if available
    if 'h2h_avg_goals_scored' in team_stats:
        print(f"H2H average goals scored: {team_stats['h2h_avg_goals_scored']:.2f}")
        print(f"H2H average goals conceded: {team_stats['h2h_avg_goals_conceded']:.2f}")
        print(f"H2H win rate: {team_stats['h2h_win_rate']:.2f}")
    
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
    # Use the configured teams from config.py
    team_a = HOME_TEAM
    team_b = AWAY_TEAM
    
    # By default, Team A (HOME_TEAM) is the home team
    is_team_a_home = True
    
    print(f"Predicting match: {team_a} (Home) vs {team_b} (Away)")
    print("=" * 70)
    print(f"Using configuration from config.py")
    print(f"To change teams, edit HOME_TEAM and AWAY_TEAM in config.py")
    print(f"Looking for up to {MATCHES_TO_CONSIDER} historical matches between teams")
    print("Loading data and calculating predictions...")
    
    # Make prediction
    prediction = predict_match(team_a, team_b, is_team_a_home)
    
    if not prediction:
        print("Could not make a prediction. Please check team names in config.py and try again.")
        return
    
    # Display results
    print("\nMatch Prediction Results:")
    print("=" * 70)
    
    team_a_name = prediction['team_a']['team_name']
    team_b_name = prediction['team_b']['team_name']
    
    print(f"{team_a_name} vs {team_b_name}")
    print(f"Expected goals: {prediction['team_a_expected_goals']:.2f} - {prediction['team_b_expected_goals']:.2f}")
    print(f"Most likely total goals: {prediction['most_likely_total']}")
    
    # Always show detailed statistics since we're only using config.py values
    print_team_stats(prediction['team_a'], True)
    print_team_stats(prediction['team_b'], False)
    
    print("\nTotal Goals Probability Table:")
    print("-" * 40)
    
    # Display the probability table
    prob_table = format_probability_table(prediction['total_goals_probabilities'])
    pd.set_option('display.max_rows', None)
    print(prob_table.to_string(index=False))
    
    print("\nNote: This prediction is based on the most recent matches data from football-data.org")
    print("      To predict for different teams, edit the HOME_TEAM and AWAY_TEAM values in config.py")

if __name__ == "__main__":
    main()