document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const teamASearch = document.getElementById('team-a-search');
    const teamBSearch = document.getElementById('team-b-search');
    const teamAResults = document.getElementById('team-a-results');
    const teamBResults = document.getElementById('team-b-results');
    const teamASelection = document.getElementById('team-a-selection');
    const teamBSelection = document.getElementById('team-b-selection');
    const teamAInput = document.getElementById('team_a_input');
    const teamBInput = document.getElementById('team_b_input');
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
                selectTeam(teamId, teamName, teamAInput, teamASelection, teamASearch, teamAResults, 'A');
            } else if (teamBResults.contains(teamResult)) {
                selectTeam(teamId, teamName, teamBInput, teamBSelection, teamBSearch, teamBResults, 'B');
            }
            
            // Enable the predict button if both teams have values
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
    function selectTeam(teamId, teamName, inputField, selectionContainer, searchInput, resultsContainer, teamLetter) {
        inputField.value = teamId;
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
                inputField.value = '';
                selectionContainer.innerHTML = '';
                checkEnablePredictButton();
            });
        }
    }
    
    // Listen for changes to the direct input fields
    teamAInput.addEventListener('input', function() {
        checkEnablePredictButton();
    });
    
    teamBInput.addEventListener('input', function() {
        checkEnablePredictButton();
    });
    
    // Function to check if predict button should be enabled
    function checkEnablePredictButton() {
        const teamAHasValue = teamAInput.value.trim() !== '';
        const teamBHasValue = teamBInput.value.trim() !== '';
        
        predictBtn.disabled = !(teamAHasValue && teamBHasValue);
    }
    
    // Initialize button state
    checkEnablePredictButton();
    
    // Initialize the goal threshold input
    const goalThresholdInput = document.getElementById('goal_threshold');
    if (goalThresholdInput) {
        // Set default step to 0.5
        goalThresholdInput.step = "0.5";
        
        // Add event to validate input
        goalThresholdInput.addEventListener('input', function() {
            validateGoalThreshold(this);
        });
    }
    
    // Function to validate goal threshold
    function validateGoalThreshold(input) {
        let value = input.value.trim();
        
        // Allow empty values
        if (value === '') {
            return;
        }
        
        // Convert to number
        let numValue = parseFloat(value);
        
        // Check if it's a valid number
        if (isNaN(numValue)) {
            input.value = '';
            return;
        }
        
        // Ensure it's not negative
        if (numValue < 0) {
            input.value = '0';
        }
        
        // If it's not a multiple of 0.5, round to nearest 0.5
        if (numValue % 0.5 !== 0) {
            input.value = (Math.round(numValue * 2) / 2).toFixed(1);
        }
    }
    
    // Add nice animation to predict button
    if (predictBtn) {
        predictBtn.addEventListener('mouseover', function() {
            this.classList.add('shadow-lg');
        });
        
        predictBtn.addEventListener('mouseout', function() {
            this.classList.remove('shadow-lg');
        });
        
        predictBtn.addEventListener('click', function() {
            if (!this.disabled) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                this.disabled = true;
                
                // Submit the form
                document.getElementById('prediction-form').submit();
            }
        });
    }
    
    // Add tooltips for better UX
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});