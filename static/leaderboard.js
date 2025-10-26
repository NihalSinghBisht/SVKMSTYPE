document.addEventListener('DOMContentLoaded', () => {
    const globalLeaderboardTable = document.getElementById('global-leaderboard').querySelector('tbody');
    const collegeLeaderboardTable = document.getElementById('college-leaderboard').querySelector('tbody');
    const collegeSelect = document.getElementById('college-select');

    // Fetch and populate global leaderboard
    fetch('/api/leaderboard/global')
        .then(response => response.json())
        .then(data => {
            populateLeaderboard(globalLeaderboardTable, data);
        })
        .catch(error => console.error('Error fetching global leaderboard:', error));

    // Fetch and populate college leaderboard based on selection
    collegeSelect.addEventListener('change', () => {
        const college = collegeSelect.value;
        fetch(`/api/leaderboard/college?college=${college}`)
            .then(response => response.json())
            .then(data => {
                populateLeaderboard(collegeLeaderboardTable, data);
            })
            .catch(error => console.error('Error fetching college leaderboard:', error));
    });

    // Helper function to populate leaderboard table
    function populateLeaderboard(table, data) {
        table.innerHTML = '';
        data.forEach((entry, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${entry.name}</td>
                <td>${entry.wpm}</td>
                <td>${entry.accuracy}%</td>
            `;
            table.appendChild(row);
        });
    }
});