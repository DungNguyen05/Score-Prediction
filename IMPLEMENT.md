# Soccer Match Predictor Web Application

This is a web-based interface for the Soccer Match Score Predictor, implementing the prediction model with FastAPI and a modern Bootstrap interface.

## Features

- User-friendly web interface with Bootstrap styling
- Team search functionality with autocomplete
- Home/away and neutral venue match prediction
- Detailed results display with statistics
- Interactive UI for selecting teams
- Responsive design for desktop and mobile

## Prerequisites

- Python 3.7+
- API key from [football-data.org](https://www.football-data.org/) (free tier works fine)

## Installation

1. Clone the repository or download the files
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Project Structure

```
soccer-predictor-web/
├── app.py                 # FastAPI application
├── model.py               # Prediction model
├── data_fetcher.py        # Data fetching functionality
├── find_team.py           # Team search functionality
├── config.py              # Configuration with API key
├── static/                # Static assets
│   ├── styles.css         # Custom CSS
│   └── script.js          # Client-side JavaScript
├── templates/             # HTML templates
│   ├── index.html         # Home page with prediction form
│   ├── prediction.html    # Prediction results page
│   └── search_results.html # Team search results snippet
└── requirements.txt       # Python dependencies
```

## Running the Web Application

To start the web application:

```bash
uvicorn app:app --reload
```

Then open your browser and visit: http://localhost:8000

## How to Use

1. **Team Selection**:
   - Type a team name in the search box (minimum 3 characters)
   - Select a team from the dropdown results
   - Repeat for the second team

2. **Venue Setting**:
   - By default, Team A is home and Team B is away
   - Check the "Neutral Venue Match" box if the match will be played at a neutral venue

3. **Get Prediction**:
   - Click the "Predict Match" button
   - View the detailed prediction results

## Configuration Options

You can modify the following in `config.py`:

```python
# API configuration
API_KEY = "your-api-key"

# Match prediction configuration
MATCHES_TO_CONSIDER = 20  # Number of recent matches to analyze
MAX_H2H_MATCHES = 10      # Maximum number of head-to-head matches to use

# Cache configuration
CACHE_MAX_AGE = 12  # hours
```

## Technical Details

The web application uses:

- **FastAPI**: For the backend API and route handling
- **Jinja2**: For HTML templating
- **Bootstrap 5**: For UI components and responsive design
- **Javascript**: For interactive team search and selection
- **SQLite Cache**: For storing API responses to reduce load

## API Endpoints

- `GET /`: Home page with prediction form
- `POST /predict`: Submit prediction request and get results
- `GET /search_team?query=...`: Search for teams by name

## Troubleshooting

- If the team search is not working, ensure your API key is valid
- If predictions take too long, check your internet connection
- If the application fails to start, ensure all requirements are installed
- Clear the `.cache` directory if you encounter stale data issues

## Future Improvements

- Add user accounts to save prediction history
- Implement additional prediction models
- Add visualization of prediction data with charts
- Create match scheduler for upcoming matches
- Compare predictions with actual results over time