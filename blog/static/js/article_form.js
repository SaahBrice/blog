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
});