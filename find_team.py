import requests

# Replace with your actual API key from football-data.org
API_KEY = "42941e9e63ae4f029b9a88377da23dec"

def find_team_id(team_name):
    """
    Search for a team by name and get its ID
    """
    # API endpoint
    url = "https://api.football-data.org/v4/teams"
    
    # Request headers
    headers = {
        "X-Auth-Token": API_KEY
    }
    
    # Parameters: limit to a reasonable number
    params = {
        "limit": 100,
        "name": team_name  # This parameter might be available depending on the API version
    }
    
    try:
        # Make request
        response = requests.get(url, headers=headers, params=params)
        
        # Handle response
        if response.status_code == 200:
            data = response.json()
            teams = data.get("teams", [])
            
            if teams:
                print("Teams found:")
                for idx, team in enumerate(teams):
                    print(f"{idx+1}. {team['name']} (ID: {team['id']})")
                
                # Return the first match as a default
                return teams[0]['id']
            else:
                print(f"No teams found with name '{team_name}'")
                return None
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_team_id():
    """
    Interactive tool to find team IDs
    """
    print("=== Team ID Finder ===")
    print("This tool helps you find team IDs to add to your config.py file")
    
    while True:
        team_name = input("\nEnter team name to search (or 'q' to quit): ")
        
        if team_name.lower() == 'q':
            break
        
        team_id = find_team_id(team_name)
        
        if team_id:
            print(f"\nTo add to the TEAM_IDS dictionary in config.py:")
            print(f'    "{team_name.lower()}": {team_id},')
    
    print("\nThank you for using the Team ID Finder!")

if __name__ == "__main__":
    get_team_id()