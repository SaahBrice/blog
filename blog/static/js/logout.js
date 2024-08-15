function initializeLogout(logoutUrl) {
    const signOutBtn = document.getElementById('signOutBtn');
    
    signOutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const popup = document.createElement('div');
        popup.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center opacity-0 transition-opacity duration-300';
        popup.innerHTML = `
            <div class="bg-white p-8 rounded-lg shadow-xl max-w-sm mx-auto text-center transform scale-95 transition-transform duration-300">
                <div class="text-6xl mb-4">🥺</div>
                <h2 class="text-xl font-bold mb-4">Are you sure you want to sign out?</h2>
                <div class="flex justify-center space-x-4">
                    <button id="cancelSignOut" class="px-4 py-2 bg-green-400 text-gray-800 rounded-full hover:bg-gray-300 transition-colors duration-200">Cancel</button>
                    <button id="confirmSignOut" class="px-4 py-2 bg-gray-300 text-white rounded-full hover:bg-red-600 transition-colors duration-200">See you later</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);

        setTimeout(() => {
            popup.classList.remove('opacity-0');
            popup.querySelector('div').classList.remove('scale-95');
            popup.querySelector('div').classList.add('scale-100');
        }, 10);
        
        document.getElementById('cancelSignOut').addEventListener('click', function() {
            closePopup(popup);
        });
        
        document.getElementById('confirmSignOut').addEventListener('click', function() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = logoutUrl;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = getCookie('csrftoken');
            form.appendChild(csrfInput);
            document.body.appendChild(form);
            form.submit();
        });
    });

    function closePopup(popup) {
        popup.classList.add('opacity-0');
        popup.querySelector('div').classList.remove('scale-100');
        popup.querySelector('div').classList.add('scale-95');
        setTimeout(() => {
            document.body.removeChild(popup);
        }, 300);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof logoutUrl !== 'undefined') {
        initializeLogout(logoutUrl);
    }
});