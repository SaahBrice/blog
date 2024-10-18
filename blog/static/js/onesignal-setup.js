document.addEventListener('DOMContentLoaded', function() {
    OneSignal.push(function() {
        OneSignal.getUserId(function(userId) {
            if (userId) {
                fetch('/users/update-onesignal-id/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({onesignal_player_id: userId}),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('OneSignal ID updated successfully');
                    } else {
                        console.error('Failed to update OneSignal ID');
                    }
                })
                .catch(error => {
                    console.error('Error updating OneSignal ID:', error);
                });
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
