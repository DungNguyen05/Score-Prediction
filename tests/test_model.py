import unittest

from model import (
    _apply_dixon_coles_adjustment,
    calculate_over_under_probability,
    calculate_score_probabilities,
    calculate_total_goals_probabilities,
    predict_goals,
)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.team_a = {
            'weighted_goals_scored': 1.8,
            'weighted_goals_conceded': 1.0,
            'avg_goals_scored': 1.7,
            'avg_goals_conceded': 1.1,
            'home_avg_goals_scored': 2.1,
            'home_avg_goals_conceded': 0.9,
            'away_avg_goals_scored': 1.3,
            'away_avg_goals_conceded': 1.2,
            'neutral_avg_goals_scored': 1.4,
            'neutral_avg_goals_conceded': 1.0,
            'num_home_matches': 8,
            'num_away_matches': 8,
            'num_neutral_matches': 2,
            'recent_form': 'WWDLW',
            'h2h_avg_goals_scored': 1.6,
            'h2h_avg_goals_conceded': 1.1,
            'h2h_history': ['a', 'b', 'c'],
        }
        self.team_b = {
            'weighted_goals_scored': 1.2,
            'weighted_goals_conceded': 1.5,
            'avg_goals_scored': 1.1,
            'avg_goals_conceded': 1.4,
            'home_avg_goals_scored': 1.4,
            'home_avg_goals_conceded': 1.1,
            'away_avg_goals_scored': 1.0,
            'away_avg_goals_conceded': 1.8,
            'neutral_avg_goals_scored': 1.1,
            'neutral_avg_goals_conceded': 1.3,
            'num_home_matches': 7,
            'num_away_matches': 7,
            'num_neutral_matches': 1,
            'recent_form': 'LDDLL',
            'h2h_avg_goals_scored': 1.1,
            'h2h_avg_goals_conceded': 1.6,
            'h2h_history': ['a', 'b', 'c'],
        }

    def test_predict_goals_stays_in_reasonable_range(self):
        home_xg, away_xg = predict_goals(self.team_a, self.team_b, False)
        self.assertGreaterEqual(home_xg, 0.2)
        self.assertLessEqual(home_xg, 4.5)
        self.assertGreaterEqual(away_xg, 0.2)
        self.assertLessEqual(away_xg, 4.5)
        self.assertGreater(home_xg, away_xg)

    def test_total_goal_probabilities_sum_to_100(self):
        home_xg, away_xg = predict_goals(self.team_a, self.team_b, False)
        total_goals = calculate_total_goals_probabilities(home_xg, away_xg)
        self.assertAlmostEqual(total_goals['probability'].sum(), 100.0, places=6)

    def test_score_probabilities_are_sorted(self):
        home_xg, away_xg = predict_goals(self.team_a, self.team_b, False)
        scores = calculate_score_probabilities(home_xg, away_xg)
        self.assertLessEqual(len(scores), 10)
        self.assertTrue(scores['probability'].is_monotonic_decreasing)

    def test_over_under_whole_number_threshold_has_push(self):
        total_goals = calculate_total_goals_probabilities(1.4, 1.1)
        result = calculate_over_under_probability(total_goals, 2.0)
        self.assertIn('push', result)
        self.assertGreaterEqual(result['push'], 0)
        self.assertAlmostEqual(result['over'] + result['under'] + result['push'], 100.0, places=4)

    def test_dixon_coles_only_changes_low_scores(self):
        self.assertNotEqual(_apply_dixon_coles_adjustment(0, 0, 1.2, 1.1), 1.0)
        self.assertEqual(_apply_dixon_coles_adjustment(2, 2, 1.2, 1.1), 1.0)


if __name__ == '__main__':
    unittest.main()
