from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Optional, Union
import pandas as pd
import os
import re

# Import our prediction model
from model import predict_match
from data_fetcher import get_team_name, get_cached_data, save_to_cache
from find_team import search_teams

app = FastAPI(title="Soccer Match Score Predictor")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs(".cache", exist_ok=True)

# Cache for team search results
TEAM_SEARCH_CACHE_KEY = "team_search_results"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with the prediction form"""
    return templates.TemplateResponse("index.html", {"request": request})

def validate_team_input(team_input: str) -> int:
    """
    Validate and convert team input (name or ID) to team ID
    
    Returns:
        int: The team ID
    Raises:
        ValueError: If the input can't be converted to a valid team ID
    """
    # Check if it's directly a team ID
    if team_input.isdigit():
        return int(team_input)
    
    # Search for the team by name
    teams = search_teams(team_input)
    if teams:
        return teams[0]['id']
    
    # If we get here, the input is neither a valid ID nor a found team name
    raise ValueError(f"Could not find team ID for: {team_input}")

@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    team_a_input: str = Form(...),
    team_b_input: str = Form(...),
    is_neutral_venue: bool = Form(False),
    goal_threshold: Optional[float] = Form(None)
):
    """Process prediction request and display results"""
    try:
        # Convert team inputs to IDs
        try:
            team_a_id = validate_team_input(team_a_input)
            team_b_id = validate_team_input(team_b_input)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get team names for display
        team_a_name = get_team_name(team_a_id)
        team_b_name = get_team_name(team_b_id)
        
        # Make prediction, including the over/under threshold if provided
        prediction = predict_match(team_a_id, team_b_id, is_neutral_venue, goal_threshold)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Could not make prediction. Please check team inputs.")
            
        # Format probability tables for display
        total_goals_table = format_probability_table(prediction['total_goals_probabilities'])
        score_table = format_score_probability_table(prediction['score_probabilities'].head(10))
        
        # Set venue labels for display
        if is_neutral_venue:
            team_a_venue = "Neutral"
            team_b_venue = "Neutral"
            match_venue = "Neutral Venue"
        else:
            team_a_venue = "Home"
            team_b_venue = "Away"
            match_venue = "Standard Venue"
        
        # Prepare over/under result for display
        over_under_result = prediction.get('over_under_result')
        
        return templates.TemplateResponse(
            "prediction.html", 
            {
                "request": request,
                "team_a_name": team_a_name,
                "team_b_name": team_b_name,
                "team_a_id": team_a_id,
                "team_b_id": team_b_id,
                "team_a_venue": team_a_venue,
                "team_b_venue": team_b_venue,
                "match_venue": match_venue,
                "is_neutral_venue": is_neutral_venue,
                "team_a_expected_goals": prediction['team_a_expected_goals'],
                "team_b_expected_goals": prediction['team_b_expected_goals'],
                "most_likely_score": prediction['most_likely_score'],
                "most_likely_total": prediction['most_likely_total'],
                "team_a_stats": prediction['team_a'],
                "team_b_stats": prediction['team_b'],
                "total_goals_table": total_goals_table,
                "score_table": score_table,
                "goal_threshold": prediction.get('goal_threshold'),
                "over_under_result": over_under_result
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/search_team", response_class=HTMLResponse)
async def search_team(request: Request, query: Optional[str] = None):
    """Search for teams by name"""
    results = []
    
    if query and len(query) >= 3:
        # Try to get from cache first
        cached_data = get_cached_data(TEAM_SEARCH_CACHE_KEY)
        all_teams = cached_data if cached_data else []
        
        # Filter teams based on query
        if all_teams:
            results = [team for team in all_teams if query.lower() in team['name'].lower()]
        
        # If no results or no cache, search via API
        if not results:
            results = search_teams(query)
            
            # Update cache with new results
            if results:
                # Merge with existing cache if available
                if all_teams:
                    # Create a dictionary to eliminate duplicates
                    teams_dict = {team['id']: team for team in all_teams}
                    # Add new teams
                    for team in results:
                        teams_dict[team['id']] = team
                    # Convert back to list
                    all_teams = list(teams_dict.values())
                else:
                    all_teams = results
                
                # Save updated list to cache
                save_to_cache(TEAM_SEARCH_CACHE_KEY, all_teams)
    
    return templates.TemplateResponse(
        "search_results.html", 
        {"request": request, "results": results, "query": query}
    )

def format_probability_table(prob_table):
    """Format the probability table for display"""
    # Round to 2 decimal places and sort
    formatted = prob_table.copy()
    formatted['probability'] = formatted['probability'].round(2)
    
    return formatted.to_dict('records')

def format_score_probability_table(prob_table):
    """Format the score probability table for display"""
    # Round to 2 decimal places
    formatted = prob_table.copy()
    formatted['probability'] = formatted['probability'].round(2)
    
    return formatted.to_dict('records')

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)