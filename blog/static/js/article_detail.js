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
        e.stopPropagation();
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
        const commentId = btn.closest('.comment-reaction-container').find('.comment-reaction').data('comment-id');
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
    $('#comment-form').off('submit').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var submitButton = form.find('button[type="submit"]');
        
        if (form.data('submitting')) return false;
        form.data('submitting', true);
        submitButton.prop('disabled', true);
        
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    var commentsSection = $('#comments-section');
                    commentsSection.append($(response.comment_html));
                    form.find('textarea').val('');
                    $('#comment-count').text(response.comment_count);
                    
                    // Show comments section if hidden
                    commentsSection.removeClass('hidden');
                    
                    // Scroll to the new comment
                    var newComment = commentsSection.children().last();
                    $('html, body').animate({
                        scrollTop: newComment.offset().top - 100
                    }, 1000);
                } else {
                    alert(response.error);
                }
            },
            error: function() {
                alert('An error occurred while posting your comment.');
            },
            complete: function() {
                form.data('submitting', false);
                submitButton.prop('disabled', false);
            }
        });
    });




    
    // Handle reply form submissions (including dynamically added ones)
    $(document).on('submit', '.reply-form', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var textarea = form.find('textarea');
        var content = textarea.val().trim();
        var parentCommentId = form.closest('.comment').attr('id').replace('comment-', '');
        
        if (!content) {
            alert('Please enter a comment before submitting.');
            return;
        }
        
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    var replySection = $('.reply-form');
                    replySection.addClass('hidden');
                    addReplyToDOM(response.reply_html, parentCommentId);
                    $('#comment-count').text(response.comment_count);
                    form.find('textarea').val('');  // Clear the textarea
                } else {
                    alert(response.error);
                }
            },
            error: function() {
                alert('An error occurred while posting your reply.');
            }
        });
    });

    function addReplyToDOM(replyHtml, parentCommentId) {
        var parentComment = $('#comment-' + parentCommentId);
        var subcommentsContainer = parentComment.find('#subcomments-' + parentCommentId);
        
        if (subcommentsContainer.length === 0) {
            parentComment.append('<div id="subcomments-' + parentCommentId + '" class="ml-11 mt-2"></div>');
            subcommentsContainer = parentComment.find('#subcomments-' + parentCommentId);
        }
        
        subcommentsContainer.append(replyHtml);
        subcommentsContainer.removeClass('hidden');
        
        // Update reply count
        var replyCountElem = parentComment.find('.toggle-subcomments .reply-count');
        var currentCount = parseInt(replyCountElem.text(), 10);
        replyCountElem.text(currentCount + 1);
        
        // Ensure the toggle button is visible
        parentComment.find('.toggle-subcomments').removeClass('hidden');
    }










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



document.addEventListener('DOMContentLoaded', () => {
    const ttsButton = document.getElementById('ttsButton');
    const articleContent = document.getElementById('article-content').innerHTML;
    const apiKey = document.getElementById('speechify-api-key').value;

    if (apiKey && typeof TextToSpeech !== 'undefined') {
        let tts = null;
        let isInitialized = false;

        ttsButton.addEventListener('click', async () => {
            if (!isInitialized) {
                ttsButton.textContent = 'Loading...';
                ttsButton.disabled = true;
                tts = new TextToSpeech(apiKey);
                try {
                    console.log('Starting TTS initialization');
                    await tts.initialize(articleContent);
                    isInitialized = true;
                    ttsButton.textContent = 'Read gist';
                    ttsButton.disabled = false;
                    console.log('TTS initialization complete');
                } catch (error) {
                    console.error('TTS Initialization Error:', error);
                    ttsButton.textContent = 'TTS Error';
                    alert(`Failed to initialize Text-to-Speech: ${error.message}`);
                    return;
                }
            }

            try {
                console.log('Triggering playPause');
                const isPlaying = await tts.playPause();
                ttsButton.textContent = isPlaying ? 'Pause' : 'Read gist';
            } catch (error) {
                console.error('TTS Playback Error:', error);
                ttsButton.textContent = 'TTS Error';
                alert(`An error occurred during playback: ${error.message}`);
            }
        });
    } else {
        ttsButton.textContent = 'TTS Unavailable';
        ttsButton.disabled = true;
    }
});
