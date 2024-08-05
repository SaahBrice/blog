$(document).ready(function() {
    // Setup CSRF token for AJAX requests
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#followAuthorBtn').click(function() {
        var authorId = $(this).data('author-id');
        $.post(`/articles/follow-author/${authorId}/`, function(data) {
            if (data.is_following) {
                $('#followAuthorBtn').text('Unfollow Author');
            } else {
                $('#followAuthorBtn').text('Follow Author');
            }
        });
    });

    $('#bookmarkBtn').click(function() {
        var articleId = $(this).data('article-id');
        $.post(`/articles/${articleId}/bookmark/`, function(data) {
            if (data.bookmarked) {
                $('#bookmarkBtn').text('Remove Bookmark');
            } else {
                $('#bookmarkBtn').text('Bookmark');
            }
        });
    });

    $('.reaction-btn').click(function(e) {
        e.preventDefault();
        $(this).siblings('.reaction-options').toggle();
    });


    $('.reaction-amount').click(function() {
        const amount = $(this).data('amount');
        const reactionType = $(this).closest('.reaction-container').find('.reaction-btn').data('type');
        const articleId = $(this).closest('.reaction-container').find('.reaction-btn').data('article-id');
        
        $.ajax({
            url: `/articles/${articleId}/react/`,
            type: 'POST',
            data: {
                reaction_type: reactionType,
                amount: amount
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(data) {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Update all reaction counts
                    $(`#clap-count`).text(data.clap_count);
                    $(`#sad-count`).text(data.sad_count);
                    $(`#laugh-count`).text(data.laugh_count);
                }
                // Hide the reaction options after selection
                $('.reaction-options').hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error in reaction:", textStatus, errorThrown);
                alert("An error occurred while processing your reaction.");
            }
        });
    });

});

// Helper function to get CSRF token from cookies
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to check if the request method is safe
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}