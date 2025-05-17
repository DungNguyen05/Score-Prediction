# Soccer Match Score Predictor

This program predicts the total goals in a soccer match between two teams using historical data from the football-data.org API and a statistical Poisson model.

## Features

- Fetches the most recent match data for both teams
- Analyzes head-to-head history between the teams
- Considers home/away performance
- Takes into account recent form
- Provides probability distribution for total goals in the match
- **Optimized data fetching with caching**
- **Configurable data sources**

## Prerequisites

- Python 3.6+
- API key from [football-data.org](https://www.football-data.org/) (free tier works fine)

## Installation

1. Clone this repository or download the files
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Configuration

Edit the `config.py` file to customize the prediction:

### Team Settings
```python
HOME_TEAM = "real madrid"  # The home team for the match to predict
AWAY_TEAM = "barcelona"    # The away team for the match to predict
```

### Data Fetching Optimization
```python
# Model configuration
MATCHES_TO_CONSIDER = 20   # Number of recent matches to analyze
MAX_H2H_MATCHES = 10       # Maximum number of head-to-head matches to use

# Data fetching optimization 
FETCH_RECENT_MATCHES = True  # Whether to fetch recent team matches (set to False to skip and use H2H only)
FETCH_H2H_MATCHES = True     # Whether to fetch head-to-head matches
```

### Optimization Options

By configuring these options, you can control exactly which data is fetched:

- **Focus on head-to-head matches only**: Set `FETCH_RECENT_MATCHES = False` and `FETCH_H2H_MATCHES = True` 
  - This will only analyze direct match history between the two teams
  - Useful for derby matches or traditional rivalries where past meetings are most relevant

- **Focus on recent form only**: Set `FETCH_RECENT_MATCHES = True` and `FETCH_H2H_MATCHES = False`
  - This will only analyze recent team performance
  - Useful when teams haven't met recently or are from different leagues

- **Use both data sources**: Set both to `True` (default)
  - This provides the most comprehensive prediction
  - Combines recent form with head-to-head history

## Usage

Simply run the main script:

```bash
python main.py
```

The program will:
1. Fetch data based on your configuration settings
2. Calculate statistics from the specified data sources
3. Display a detailed prediction with probability table
4. Cache results to improve performance on subsequent runs

## Caching System

The program now includes a caching system that:

1. Saves API responses to a local `.cache` directory
2. Reuses cached data for 24 hours before refreshing
3. Significantly reduces API calls and speeds up repeat predictions

## Sample Output

```
Predicting match: real madrid (Home) vs barcelona (Away)
======================================================================
Using configuration from config.py
Data fetching settings:
  - Recent matches: Enabled (max: 20)
  - Head-to-head matches: Enabled (max: 10)
Loading data and calculating predictions...
Using cached data: Found 20 recent matches for real madrid
Using cached data: Found 20 recent matches for barcelona
Using cached data: Found 46 head-to-head matches between real madrid and barcelona
Expected goals - real madrid: 2.31, barcelona: 1.86

Match Prediction Results:
======================================================================
real madrid vs barcelona
Expected goals: 2.31 - 1.86
Most likely total goals: 4

...
```

## How to Add New Teams

If the team you want isn't in the TEAM_IDS dictionary, you can add it:

1. First try searching for it in the existing list (in config.py)
2. If it's not there, you can find the team ID using the find_team.py utility:

```bash
python find_team.py
```

Then add the team to the TEAM_IDS dictionary in config.py.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [football-data.org](https://www.football-data.org/) for the API service
- Poisson distribution model based on academic research on soccer prediction