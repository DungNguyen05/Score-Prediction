import numpy as np
from scipy.stats import poisson
import pandas as pd


MIN_EXPECTED_GOALS = 0.2
MAX_EXPECTED_GOALS = 4.5
LOW_SCORE_RHO = -0.08


def _safe_rate(value, fallback, minimum=0.1):
    """Return a bounded scoring rate with sensible fallbacks."""
    if value is None or pd.isna(value) or value <= 0:
        value = fallback
    return max(minimum, float(value))


def _blend_with_overall(split_value, split_matches, overall_value, min_matches=6):
    """Blend venue-specific metrics with overall metrics based on sample size."""
    reliability = min(1.0, max(0.0, split_matches / float(min_matches)))
    return (split_value * reliability) + (overall_value * (1.0 - reliability))


def _form_score(form_string):
    """Convert recent form string into a recency-weighted score between 0 and 1."""
    weights = [0.40, 0.25, 0.18, 0.10, 0.07]
    points = {'W': 1.0, 'D': 0.5, 'L': 0.0}
    return sum(weights[i] * points.get(result, 0.5) for i, result in enumerate(form_string[:5]))


def _apply_dixon_coles_adjustment(home_goals, away_goals, home_lambda, away_lambda, rho=LOW_SCORE_RHO):
    """Low-score correlation adjustment for Poisson score lines."""
    if home_goals == 0 and away_goals == 0:
        return 1 - (home_lambda * away_lambda * rho)
    if home_goals == 0 and away_goals == 1:
        return 1 + (home_lambda * rho)
    if home_goals == 1 and away_goals == 0:
        return 1 + (away_lambda * rho)
    if home_goals == 1 and away_goals == 1:
        return 1 - rho
    return 1.0


def _build_joint_probability_matrix(team_a_exp_goals, team_b_exp_goals, max_goals):
    """Build a normalized joint probability table for score combinations."""
    probabilities = []

    for home_goals in range(max_goals + 1):
        home_prob = poisson.pmf(home_goals, team_a_exp_goals)
        for away_goals in range(max_goals + 1):
            away_prob = poisson.pmf(away_goals, team_b_exp_goals)
            adjustment = _apply_dixon_coles_adjustment(
                home_goals, away_goals, team_a_exp_goals, team_b_exp_goals
            )
            probabilities.append({
                'home_goals': home_goals,
                'away_goals': away_goals,
                'probability': max(0.0, home_prob * away_prob * adjustment)
            })

    prob_df = pd.DataFrame(probabilities)
    total_probability = prob_df['probability'].sum()
    if total_probability > 0:
        prob_df['probability'] = prob_df['probability'] / total_probability

    return prob_df


def predict_goals(team_a_stats, team_b_stats, is_neutral_venue=False):
    """
    Predict expected goals using a blended attack/defense strength model.

    Improvements over the original implementation:
    - blends venue-specific and overall stats based on sample reliability
    - uses both attacking and defensive strengths for each side
    - applies smaller, reliability-aware form and H2H adjustments
    - keeps predictions in a realistic scoring range
    """
    team_a_overall_scored = _safe_rate(team_a_stats.get('weighted_goals_scored'), team_a_stats.get('avg_goals_scored', 1.2))
    team_a_overall_conceded = _safe_rate(team_a_stats.get('weighted_goals_conceded'), team_a_stats.get('avg_goals_conceded', 1.2))
    team_b_overall_scored = _safe_rate(team_b_stats.get('weighted_goals_scored'), team_b_stats.get('avg_goals_scored', 1.2))
    team_b_overall_conceded = _safe_rate(team_b_stats.get('weighted_goals_conceded'), team_b_stats.get('avg_goals_conceded', 1.2))

    league_avg_goals = max(0.8, np.mean([
        team_a_overall_scored,
        team_a_overall_conceded,
        team_b_overall_scored,
        team_b_overall_conceded,
    ]))

    if is_neutral_venue:
        team_a_attack = _blend_with_overall(
            _safe_rate(team_a_stats.get('neutral_avg_goals_scored'), team_a_overall_scored),
            team_a_stats.get('num_neutral_matches', 0),
            (team_a_overall_scored + team_a_stats.get('away_avg_goals_scored', team_a_overall_scored)) / 2,
            min_matches=4,
        )
        team_a_defense = _blend_with_overall(
            _safe_rate(team_a_stats.get('neutral_avg_goals_conceded'), team_a_overall_conceded),
            team_a_stats.get('num_neutral_matches', 0),
            (team_a_overall_conceded + team_a_stats.get('away_avg_goals_conceded', team_a_overall_conceded)) / 2,
            min_matches=4,
        )
        team_b_attack = _blend_with_overall(
            _safe_rate(team_b_stats.get('neutral_avg_goals_scored'), team_b_overall_scored),
            team_b_stats.get('num_neutral_matches', 0),
            (team_b_overall_scored + team_b_stats.get('away_avg_goals_scored', team_b_overall_scored)) / 2,
            min_matches=4,
        )
        team_b_defense = _blend_with_overall(
            _safe_rate(team_b_stats.get('neutral_avg_goals_conceded'), team_b_overall_conceded),
            team_b_stats.get('num_neutral_matches', 0),
            (team_b_overall_conceded + team_b_stats.get('away_avg_goals_conceded', team_b_overall_conceded)) / 2,
            min_matches=4,
        )
        home_advantage = 1.0
    else:
        team_a_attack = _blend_with_overall(
            _safe_rate(team_a_stats.get('home_avg_goals_scored'), team_a_overall_scored),
            team_a_stats.get('num_home_matches', 0),
            team_a_overall_scored,
        )
        team_a_defense = _blend_with_overall(
            _safe_rate(team_a_stats.get('home_avg_goals_conceded'), team_a_overall_conceded),
            team_a_stats.get('num_home_matches', 0),
            team_a_overall_conceded,
        )
        team_b_attack = _blend_with_overall(
            _safe_rate(team_b_stats.get('away_avg_goals_scored'), team_b_overall_scored),
            team_b_stats.get('num_away_matches', 0),
            team_b_overall_scored,
        )
        team_b_defense = _blend_with_overall(
            _safe_rate(team_b_stats.get('away_avg_goals_conceded'), team_b_overall_conceded),
            team_b_stats.get('num_away_matches', 0),
            team_b_overall_conceded,
        )
        home_advantage = 1.08

    team_a_attack_strength = team_a_attack / league_avg_goals
    team_a_defense_strength = team_a_defense / league_avg_goals
    team_b_attack_strength = team_b_attack / league_avg_goals
    team_b_defense_strength = team_b_defense / league_avg_goals

    team_a_exp_goals = league_avg_goals * team_a_attack_strength * team_b_defense_strength * home_advantage
    team_b_exp_goals = league_avg_goals * team_b_attack_strength * team_a_defense_strength

    team_a_form_score = _form_score(team_a_stats.get('recent_form', ''))
    team_b_form_score = _form_score(team_b_stats.get('recent_form', ''))
    form_delta = team_a_form_score - team_b_form_score
    form_weight = 0.12 if is_neutral_venue else 0.16
    team_a_exp_goals *= 1 + (form_delta * form_weight)
    team_b_exp_goals *= 1 - (form_delta * form_weight)

    if 'h2h_avg_goals_scored' in team_a_stats and 'h2h_avg_goals_scored' in team_b_stats:
        if is_neutral_venue and team_a_stats.get('h2h_neutral_matches', 0) > 0:
            h2h_matches = min(team_a_stats.get('h2h_neutral_matches', 0), 4)
            h2h_weight = 0.08 * (h2h_matches / 4)
            team_a_h2h = _safe_rate(team_a_stats.get('h2h_neutral_avg_goals_scored'), team_a_exp_goals)
            team_b_h2h = _safe_rate(team_b_stats.get('h2h_neutral_avg_goals_scored'), team_b_exp_goals)
        else:
            h2h_matches = min(len(team_a_stats.get('h2h_history', [])), 5)
            h2h_weight = 0.12 * (h2h_matches / 5) if h2h_matches else 0.0
            team_a_h2h = _safe_rate(team_a_stats.get('h2h_avg_goals_scored'), team_a_exp_goals)
            team_b_h2h = _safe_rate(team_b_stats.get('h2h_avg_goals_scored'), team_b_exp_goals)

        team_a_exp_goals = (team_a_exp_goals * (1 - h2h_weight)) + (team_a_h2h * h2h_weight)
        team_b_exp_goals = (team_b_exp_goals * (1 - h2h_weight)) + (team_b_h2h * h2h_weight)

    team_a_exp_goals = float(np.clip(team_a_exp_goals, MIN_EXPECTED_GOALS, MAX_EXPECTED_GOALS))
    team_b_exp_goals = float(np.clip(team_b_exp_goals, MIN_EXPECTED_GOALS, MAX_EXPECTED_GOALS))

    return team_a_exp_goals, team_b_exp_goals


def calculate_total_goals_probabilities(team_a_exp_goals, team_b_exp_goals, max_goals=10):
    """
    Calculate probability distribution for total goals in a match.
    Uses a normalized joint score matrix instead of assuming independence only.
    """
    joint_df = _build_joint_probability_matrix(team_a_exp_goals, team_b_exp_goals, max_goals)
    joint_df['total_goals'] = joint_df['home_goals'] + joint_df['away_goals']

    prob_df = (
        joint_df.groupby('total_goals', as_index=False)['probability']
        .sum()
        .sort_values('total_goals')
    )
    prob_df['probability'] = prob_df['probability'] * 100
    return prob_df


def calculate_over_under_probability(total_goals_df, threshold):
    """
    Calculate the probability of total goals being over or under a given threshold
    
    Args:
        total_goals_df: DataFrame with total_goals and probability columns
        threshold: The number of goals to calculate over/under probabilities for
    
    Returns:
        Dictionary with over and under probabilities as percentages
    """
    threshold = float(threshold)
    total_goals = total_goals_df['total_goals'].values
    probabilities = total_goals_df['probability'].values / 100

    over_prob = 0
    under_prob = 0
    equal_prob = 0

    for goals, prob in zip(total_goals, probabilities):
        if goals > threshold:
            over_prob += prob
        elif goals < threshold:
            under_prob += prob
        else:
            equal_prob += prob

    if threshold == int(threshold):
        result = {
            'over': over_prob * 100,
            'under': under_prob * 100,
            'push': equal_prob * 100
        }
    else:
        result = {
            'over': over_prob * 100,
            'under': (under_prob + equal_prob) * 100,
            'push': 0
        }

    return result


def calculate_score_probabilities(team_a_exp_goals, team_b_exp_goals, max_goals=5):
    """Calculate probability distribution for specific scores."""
    prob_df = _build_joint_probability_matrix(team_a_exp_goals, team_b_exp_goals, max_goals)
    prob_df['score'] = prob_df['home_goals'].astype(str) + '-' + prob_df['away_goals'].astype(str)
    prob_df['probability'] = prob_df['probability'] * 100
    return prob_df.sort_values('probability', ascending=False).head(10)


def predict_match(team_a_id, team_b_id, is_neutral_venue=False, goal_threshold=None):
    """
    Main prediction function with added over/under threshold
    """
    from data_fetcher import get_match_prediction_data, get_team_name

    team_a_name = get_team_name(team_a_id)
    team_b_name = get_team_name(team_b_id)

    prediction_data = get_match_prediction_data(team_a_id, team_b_id)

    if not prediction_data:
        return None

    team_a_stats = prediction_data['team_a']
    team_b_stats = prediction_data['team_b']

    team_a_exp_goals, team_b_exp_goals = predict_goals(
        team_a_stats, team_b_stats, is_neutral_venue
    )

    print(f"Expected goals - {team_a_name}: {team_a_exp_goals:.2f}, {team_b_name}: {team_b_exp_goals:.2f}")

    prob_table = calculate_total_goals_probabilities(team_a_exp_goals, team_b_exp_goals)
    score_probabilities = calculate_score_probabilities(team_a_exp_goals, team_b_exp_goals)

    over_under_result = None
    if goal_threshold is not None:
        try:
            goal_threshold = float(goal_threshold)
            over_under_result = calculate_over_under_probability(prob_table, goal_threshold)
            print(f"Over/Under {goal_threshold} goals - Over: {over_under_result['over']:.2f}%, Under: {over_under_result['under']:.2f}%")
        except (ValueError, TypeError) as e:
            print(f"Error calculating over/under: {e}")

    return {
        'team_a': team_a_stats,
        'team_b': team_b_stats,
        'team_a_expected_goals': team_a_exp_goals,
        'team_b_expected_goals': team_b_exp_goals,
        'total_goals_probabilities': prob_table,
        'score_probabilities': score_probabilities,
        'most_likely_total': prob_table.loc[prob_table['probability'].idxmax(), 'total_goals'],
        'most_likely_score': score_probabilities.iloc[0]['score'] if not score_probabilities.empty else "Unknown",
        'is_neutral_venue': is_neutral_venue,
        'over_under_result': over_under_result,
        'goal_threshold': goal_threshold
    }
