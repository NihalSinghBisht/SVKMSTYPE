document.addEventListener('DOMContentLoaded', () => {
    const leaderboardTable = document.querySelector('#leaderboard-table tbody');
    
    // Fetch leaderboard data
    fetch('/leaderboard')
        .then(response => response.text())
        .then(html => {
            // The data is already rendered in the HTML from Flask
            // Just ensure the table is visible
            if (leaderboardTable) {
                leaderboardTable.style.display = 'table-row-group';
            }
        })
        .catch(error => console.error('Error:', error));
});