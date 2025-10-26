function handleTestCompletion(wpm, accuracy) {
    const data = {
        wpm: wpm,
        accuracy: accuracy
    };

    fetch('/submit_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;  // Redirect to leaderboard
        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}