$(document).ready(function() {
    $("#id_tags").selectize({
        valueField: 'name',
        labelField: 'name',
        searchField: 'name',
        create: true,
        load: function(query, callback) {
            if (!query.length) return callback();
            $.ajax({
                url: '/articles/get-tags/',
                type: 'GET',
                dataType: 'json',
                data: {
                    query: query
                },
                error: function() {
                    callback();
                },
                success: function(res) {
                    callback(res.map(function(item) {
                        return {name: item};
                    }));
                }
            });
        }
    });

    let editor;

    // Initialize Editor.js
    editor = new EditorJS({
        holder: 'editorjs',
        tools: {
            header: {
                class: Header,
                config: {
                    levels: [1, 2],
                    defaultLevel: 1
                }
            },

            SimpleImage: SimpleImage,
            quote: Quote,
            code: CodeTool,
            table: Table,
            embed: Embed,
            list: List,
            paragraph: {
                class: Paragraph,
                inlineToolbar: ['bold', 'italic', 'inlineCode']
            },
            image: {
                class: ImageTool,
                config: {
                    endpoints: {
                        byFile: '/articles/upload-image/', 
                    },
                    field: 'image',
                    types: 'image/*'
                }
            },
            
            inlineCode: {
                class: InlineCode,
                shortcut: 'CMD+SHIFT+M',
            }
        },
        data: JSON.parse(document.getElementById('id_content').value || '{}'),
        onChange: function() {
            editor.save().then((outputData) => {
                document.getElementById('id_content').value = JSON.stringify(outputData);
            });
        }
    });

    // Image preview functionality
    $('#id_thumbnail').on('change', function() {
        const file = this.files[0];
        const reader = new FileReader();
        const $preview = $('#thumbnail-preview');

        reader.onloadend = function () {
            $preview.attr('src', reader.result);
            $preview.show();
        }

        if (file) {
            reader.readAsDataURL(file);
        } else {
            $preview.attr('src', '');
            $preview.hide();
        }
    });

    // Show existing thumbnail if it exists
    if ($('#thumbnail-preview').attr('src')) {
        $('#thumbnail-preview').show();
    }

    // Form submission
    $('#article-form').on('submit', function(e) {
        e.preventDefault();
        
        editor.save().then((outputData) => {
            var formData = new FormData(this);
            formData.set('content', JSON.stringify(outputData));
            
            $.ajax({
                url: $(this).attr('action'),
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        window.location.href = response.redirect_url;
                    } else {
                        alert('Error saving article: ' + JSON.stringify(response.error));
                    }
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText);
                    alert('An error occurred while saving the article. Please check the console for details.');
                }
            });
        }).catch((error) => {
            console.log('Saving failed: ', error)
        });
    });

    console.log('Article form script loaded');
});
