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

    $(document).on('click', '.comment-reaction, .reply .comment-reaction', function(e) {
        e.preventDefault();
        const btn = $(this);
        const commentId = btn.data('comment-id');
        const reactionType = btn.data('type');
        btn.siblings('.reaction-options').toggle();
    });
    
    $(document).on('click', '.comment-reaction-amount, .reply .comment-reaction-amount', function() {
        const btn = $(this);
        const amount = btn.data('amount');
        const commentId = btn.closest('.comment-reactions').data('comment-id');
        const reactionType = btn.closest('.comment-reaction-container').find('.comment-reaction').data('type');
        
        $.ajax({
            url: `/articles/comment/${commentId}/react/`,
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
                    btn.closest('.comment-reactions').find(`.${reactionType}-count`).text(data[`${reactionType}_count`]);
                    $('#clap-count').text(data.article_clap_count);
                }
                btn.closest('.reaction-options').hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error in comment reaction:", textStatus, errorThrown);
                alert("An error occurred while processing your reaction.");
            }
        });
    });

    // Tribute configuration for @mentions
    var tribute = new Tribute({
        values: function (text, cb) {
            $.ajax({
                url: '/articles/user-suggestions/',
                data: { query: text },
                success: function (data) {
                    cb(data);
                }
            });
        },
        lookup: 'username',
        fillAttr: 'username',
        selectTemplate: function (item) {
            return '@' + item.original.username;
        }
    });

    // Initialize Tribute for main comment form
    tribute.attach(document.querySelector('#comment-form textarea'));

    // Initialize Tribute for existing reply forms
    $('.reply-form textarea').each(function() {
        tribute.attach(this);
    });

    // Handle main comment form submission
    $('#comment-form').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    // Prepend new comment to the list
                    $('#comments-section').prepend($(response.comment_html));
                    form.find('textarea').val('');
                    // Update comment count
                    $('#comment-count').text(response.comment_count);
                } else {
                    alert(response.error);
                }
            },
            error: function() {
                alert('An error occurred while posting your comment.');
            }
        });
    });

    // Handle reply form submissions (including dynamically added ones)
    $(document).on('submit', '.reply-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    // Append new reply to the correct comment
                    form.siblings('.replies').append($(response.reply_html));
                    form.find('textarea').val('');
                    // Update comment count
                    $('#comment-count').text(response.comment_count);
                } else {
                    alert(response.error);
                }
            },
            error: function() {
                alert('An error occurred while posting your reply.');
            }
        });
    });

    // Initialize Tribute for dynamically added reply forms
    $(document).on('focus', '.reply-form textarea', function() {
        if (!this.tribute) {
            tribute.attach(this);
        }
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