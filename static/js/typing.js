function handleTestCompletion(wpm, accuracy) {
    const data = {
        email: userEmail,
        wpm: wpm,
        accuracy: accuracy,
        raw_wpm: rawWPM
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
        if (data.success && data.redirect) {
            window.location.href = data.redirect;
        }
    })
    .catch(error => console.error('Error:', error));
}