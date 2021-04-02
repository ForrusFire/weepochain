$(document).ready(function(){

    // Show the transactions of the requested node
    $('#view_transactions').click(function(){
        $.ajax({
            url: $('#node_url').val() + '/blocks',
            type: 'GET',
            success: function(response){
                // Generate transactions table
                var transactions = [];
                count = 1;

                for (i = 0; i < response['length']; i++){
                    for (j = 0; j < response['chain'][i]['transactions'].length; j++){
                        // Date format
                        var options = {year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"};
                        var date = new Date(response["chain"][i]["timestamp"] * 1000);
                        var formattedDateTime = date.toLocaleTimeString("en-us", options);

                        // Create table row
                        transaction = [count,
                            response['chain'][i]['transactions'][j]['recipient'],
                            response['chain'][i]['transactions'][j]['sender'],
                            response['chain'][i]['transactions'][j]['amount'],
                            formattedDateTime,
                            response['chain'][i]['index']];

                        transactions.push(transaction);
                        count += 1;
                    };
                };

                // Restrict a column to 10 characters, do split words
                $('#transactions').dataTable({
                    data: transactions,
                    columns: [{title: "#"},
                            {title: "Recipient Address"},
                            {title: "Sender Address"},
                            {title: "Amount"},
                            {title: "Time"},
                            {title: "Block"}],
                    columnDefs: [{targets: [1,2,3,4,5], render: $.fn.dataTable.render.ellipsis(25)}],
                });
            },
            error: function(error){
                console.log(error);
            },
        });
    });
});