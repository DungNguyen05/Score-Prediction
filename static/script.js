document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const teamASearch = document.getElementById('team-a-search');
    const teamBSearch = document.getElementById('team-b-search');
    const teamAResults = document.getElementById('team-a-results');
    const teamBResults = document.getElementById('team-b-results');
    const teamASelection = document.getElementById('team-a-selection');
    const teamBSelection = document.getElementById('team-b-selection');
    const teamAIdInput = document.getElementById('team_a_id');
    const teamBIdInput = document.getElementById('team_b_id');
    const predictBtn = document.getElementById('predict-btn');
    
    // Timer for delayed search
    let searchTimer;
    
    // Search for teams when typing in team A search box
    teamASearch.addEventListener('input', function() {
        clearTimeout(searchTimer);
        
        const query = teamASearch.value.trim();
        
        // Only search if query is at least 3 characters
        if (query.length >= 3) {
            searchTimer = setTimeout(function() {
                searchTeams(query, teamAResults);
            }, 300);
        } else {
            teamAResults.innerHTML = '';
        }
    });
    
    // Search for teams when typing in team B search box
    teamBSearch.addEventListener('input', function() {
        clearTimeout(searchTimer);
        
        const query = teamBSearch.value.trim();
        
        // Only search if query is at least 3 characters
        if (query.length >= 3) {
            searchTimer = setTimeout(function() {
                searchTeams(query, teamBResults);
            }, 300);
        } else {
            teamBResults.innerHTML = '';
        }
    });
    
    // Handle clicking outside search results to hide them
    document.addEventListener('click', function(event) {
        if (!teamASearch.contains(event.target) && !teamAResults.contains(event.target)) {
            teamAResults.innerHTML = '';
        }
        
        if (!teamBSearch.contains(event.target) && !teamBResults.contains(event.target)) {
            teamBResults.innerHTML = '';
        }
    });
    
    // Add event delegation for team selection
    document.addEventListener('click', function(event) {
        if (event.target.closest('.team-result')) {
            const teamResult = event.target.closest('.team-result');
            const teamId = teamResult.dataset.teamId;
            const teamName = teamResult.dataset.teamName;
            
            // Check which search results container this is in
            if (teamAResults.contains(teamResult)) {
                selectTeam(teamId, teamName, teamAIdInput, teamASelection, teamASearch, teamAResults);
            } else if (teamBResults.contains(teamResult)) {
                selectTeam(teamId, teamName, teamBIdInput, teamBSelection, teamBSearch, teamBResults);
            }
            
            // Enable the predict button if both teams are selected
            checkEnablePredictButton();
        }
    });
    
    // Function to search for teams
    function searchTeams(query, resultsContainer) {
        fetch(`/search_team?query=${encodeURIComponent(query)}`)
            .then(response => response.text())
            .then(html => {
                resultsContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Error searching for teams:', error);
                resultsContainer.innerHTML = '<div class="alert alert-danger mt-2">Error searching for teams</div>';
            });
    }
    
    // Function to select a team
    function selectTeam(teamId, teamName, idInput, selectionContainer, searchInput, resultsContainer) {
        idInput.value = teamId;
        selectionContainer.innerHTML = `
            <div class="team-selection">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${teamName}</strong>
                    <button type="button" class="btn-close" aria-label="Clear selection"></button>
                </div>
                <small class="text-muted">ID: ${teamId}</small>
            </div>
        `;
        searchInput.value = '';
        resultsContainer.innerHTML = '';
        
        // Add event listener to remove button
        const removeBtn = selectionContainer.querySelector('.btn-close');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                idInput.value = '';
                selectionContainer.innerHTML = '';
                checkEnablePredictButton();
            });
        }
    }
    
    // Function to check if predict button should be enabled
    function checkEnablePredictButton() {
        const teamASelected = teamAIdInput.value !== '';
        const teamBSelected = teamBIdInput.value !== '';
        
        predictBtn.disabled = !(teamASelected && teamBSelected);
    }
});