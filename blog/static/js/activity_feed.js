$(document).ready(function() {
    $('#load-more').click(function() {
        var btn = $(this);
        var page = btn.data('page');
        $.get('?page=' + page, function(data) {
            $('#articles-container').append(data);
            btn.data('page', page + 1);
            if (!data.trim()) {
                btn.remove();
            }
        });
    });
});