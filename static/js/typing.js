function handleTestCompletion(wpm, accuracy) {
    console.log('Test completed - WPM:', wpm, 'Accuracy:', accuracy);
    
    const data = {
        wpm: wpm,
        accuracy: accuracy,
        duration_seconds: 60  // Adding duration explicitly
    };

    console.log('Sending test data to server:', data);

    fetch('/submit_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Server response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Server response data:', data);
        if (data.success) {
            console.log('Redirecting to:', data.redirect);
            window.location.href = data.redirect;
        } else {
            console.error('Server reported error:', data.error);
            alert('Error saving your score. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error submitting results:', error);
        alert('Error saving your score. Please try again.');
    });
}