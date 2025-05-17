#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Soccer Match Score Predictor
This script predicts the total goals in a soccer match between two teams
using historical data from the football-data.org API
"""

import argparse
import pandas as pd
from model import predict_match
from config import HOME_TEAM, AWAY_TEAM

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

def main():
    """Main function to run the prediction"""
    # Parse command line arguments (optional override of config)
    parser = argparse.ArgumentParser(description='Predict the score of a soccer match.')
    parser.add_argument('--team_a', type=str, default=HOME_TEAM, help='Name of Team A (home team by default)')
    parser.add_argument('--team_b', type=str, default=AWAY_TEAM, help='Name of Team B (away team by default)')
    parser.add_argument('--swap', action='store_true', help='Swap home and away teams (default: Team A is home)')
    
    args = parser.parse_args()
    
    team_a = args.team_a
    team_b = args.team_b
    
    # Determine which team is home (Team A is home by default)
    is_team_a_home = not args.swap
    
    home_team = team_a if is_team_a_home else team_b
    away_team = team_b if is_team_a_home else team_a
    
    print(f"Predicting match: {home_team} (Home) vs {away_team} (Away)")
    print("=" * 70)
    print("Loading data and calculating predictions...")
    
    # Make prediction
    prediction = predict_match(team_a, team_b, is_team_a_home)
    
    if not prediction:
        print("Could not make a prediction. Please check team names and try again.")
        return
    
    # Display results
    print("\nMatch Prediction Results:")
    print("=" * 70)
    
    team_a_name = prediction['team_a']['team_name']
    team_b_name = prediction['team_b']['team_name']
    
    print(f"{team_a_name} vs {team_b_name}")
    print(f"Expected goals: {prediction['team_a_expected_goals']:.2f} - {prediction['team_b_expected_goals']:.2f}")
    print(f"Most likely total goals: {prediction['most_likely_total']}")
    print("\nTotal Goals Probability Table:")
    print("-" * 40)
    
    # Display the probability table
    prob_table = format_probability_table(prediction['total_goals_probabilities'])
    pd.set_option('display.max_rows', None)
    print(prob_table.to_string(index=False))
    
    print("\nNote: The model uses historical data to calculate probabilities. Actual results may vary.")

if __name__ == "__main__":
    main()