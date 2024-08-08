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
                        byFile: '/articles/upload-image/', // Adjust this path as needed
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


    // Form submission
    $('#article-form').on('submit', function(e) {
        e.preventDefault();
        
        editor.save().then((outputData) => {
            document.getElementById('id_content').value = JSON.stringify(outputData);
            
            // Use AJAX to submit the form
            $.ajax({
                url: $(this).attr('action'),
                type: 'POST',
                data: $(this).serialize(),
                success: function(response) {
                    if (response.success) {
                        window.location.href = response.redirect_url;
                    } else {
                        alert('Error saving article: ' + response.error);
                    }
                },
                error: function() {
                    alert('An error occurred while saving the article.');
                }
            });
        }).catch((error) => {
            console.log('Saving failed: ', error)
        });
    });
});