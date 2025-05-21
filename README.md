# Soccer Match Score Predictor (Enhanced)

This program predicts the total goals in a soccer match between two teams using historical data from the football-data.org API and a statistical Poisson model. The enhanced version supports team IDs directly and includes neutral venue predictions.

## New Features

- **Direct team ID usage** instead of team names
- **Neutral venue support** for matches with no home advantage
- Enhanced prediction model incorporating:
  - Neutral venue historical data when available
  - Head-to-head statistics at neutral venues
  - Adjusted form weighting for neutral matches
- Optimized data fetching with better caching
- Improved team search utility

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
# Team configuration (using team IDs directly)
HOME_TEAM_ID = 340  # Southampton
AWAY_TEAM_ID = 57   # Arsenal

# Match venue setting
IS_NEUTRAL_VENUE = False  # Set to True for matches at neutral venues
```

### Data Fetching Optimization
```python
# Model configuration
MATCHES_TO_CONSIDER = 20   # Number of recent matches to analyze
MAX_H2H_MATCHES = 10       # Maximum number of head-to-head matches to use
CACHE_MAX_AGE = 12         # Hours before cache expires
```

## Finding Team IDs

To find the ID for a team:

```bash
python find_team.py
```

The utility will allow you to search for teams and provide their IDs for use in `config.py`.

## Usage

Simply run the main script:

```bash
python main.py
```

The program will:
1. Fetch data based on your configuration settings
2. Calculate statistics from the specified data sources
3. Adjust predictions based on venue (home/away or neutral)
4. Display a detailed prediction with probability table
5. Cache results to improve performance on subsequent runs

## Neutral Venue Predictions

When `IS_NEUTRAL_VENUE = True`, the prediction model:

1. Uses actual neutral venue data when available
2. Blends home and away performance statistics
3. Adjusts team form weighting appropriately
4. Removes home field advantage
5. Applies head-to-head neutral venue history if available

## Caching System

The program includes a caching system that:

1. Saves API responses to a local `.cache` directory
2. Reuses cached data for 12 hours before refreshing
3. Significantly reduces API calls and speeds up repeat predictions

## Sample Output

```
Predicting match at neutral venue: Real Madrid vs Barcelona
======================================================================
Using enhanced prediction model with recency-weighted stats
Venue setting: Neutral venue
Loading data and calculating predictions...
Using cached data: Found 20 recent matches for Real Madrid
Using cached data: Found 20 recent matches for Barcelona
Using cached data: Found 8 head-to-head matches between Real Madrid and Barcelona
Expected goals - Real Madrid: 1.82, Barcelona: 1.65

Match Prediction Results:
======================================================================
Real Madrid vs Barcelona (Neutral Venue)
Expected goals: 1.82 - 1.65
Most likely score: 2-1
Most likely total goals: 3

...
```

## How It Works

The prediction model uses several factors to estimate match outcomes:

1. **Recency-weighted team performance** - gives more weight to recent matches
2. **Competition importance** - prioritizes data from important competitions
3. **Head-to-head history** - considers previous meetings between the teams
4. **Recent form** - weights the most recent 5 matches for each team
5. **Venue analysis** - adjusts for home/away advantage or neutral venues
6. **Poisson distribution** - calculates goal probability distributions

For neutral venue matches, the model:
- Uses actual neutral venue statistics when available
- Blends home/away performance data (weighted toward away performance)
- Utilizes neutral venue head-to-head data when available
- Removes the standard home field advantage

## License

This project