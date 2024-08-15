document.addEventListener('DOMContentLoaded', function() {
    const shareBtn = document.getElementById('shareBtn');
    const articleTitle = document.querySelector('.article-title').textContent;
    const articleUrl = window.location.href;

    shareBtn.addEventListener('click', async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: articleTitle,
                    url: articleUrl
                });
                console.log('Article shared successfully');
            } catch (err) {
                console.error('Error sharing article:', err);
            }
        } else {
            fallbackShare();
        }
    });

    function fallbackShare() {
        const shareText = `Check out this article: ${articleTitle} ${articleUrl}`;
        const tempInput = document.createElement('input');
        document.body.appendChild(tempInput);
        tempInput.value = shareText;
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        alert('Share link copied to clipboard!');
    }
});