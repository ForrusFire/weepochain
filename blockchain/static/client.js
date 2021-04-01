$(document).ready(function(){

    // Load unmined transactions
    $.ajax({
        url: "/transactions",
        type: 'GET',
        success: function(response){
            // Generate unmined transactions table
            var transactions = [];
            count = 1;

            for (i = 0; i < response['transactions'].length; i++){ 
                transaction = [count,
                            response['transactions'][i]["recipient"],
                            response['transactions'][i]["sender"],
                            response['transactions'][i]["amount"]];

                transactions.push(transaction);
                count += 1;
            };

            // Restrict a column to 10 characters, do split words
            $('#unmined_transactions').dataTable({
                data: transactions,
                columns: [{title: "#"},
                        {title: "Recipient Address"},
                        {title: "Sender Address"},
                        {title: "Amount"}],
                columnDefs: [{targets: [1,2,3], render: $.fn.dataTable.render.ellipsis(25)}]
            });
        },
        error: function(error){
            console.log(error);
        },
    });


    // Load transactions on the chain
    $.ajax({
        url: "/blocks",
        type: "GET",
        success: function(response){
            // Generate transactions table
            var transactions = [];
            count = 1;
            
            // Date format
            var options = {year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"};
            var date = new Date(response["chain"][i]["timestamp"] * 1000);
            var formattedDateTime = date.toLocaleTimeString("en-us", options);

            for (i = 0; i < response['length']; i++){
                for (j = 0; j < response['chain'][i]['transactions'].length; j++){
                    transaction = [count,
                        response['chain'][i]['transactions'][j]['recipient'],
                        response['chain'][i]['transactions'][j]['sender'],
                        response['chain'][i]['transactions'][j]['amount'],
                        formattedDateTime,
                        response['chain'][i]['index']];

                    transactions.push(transaction);
                    count += 1;
                }
            }

            // Restrict a column to 10 characters, do split words
            $('#transactions').dataTable({
                data: transactions,
                columns: [{title: "#"},
                        {title: "Recipient Address"},
                        {title: "Sender Address"},
                        {title: "Amount"},
                        {title: "Time"},
                        {title: "Block"}],
                columnDefs: [{targets: [1,2,3,4,5], render: $.fn.dataTable.render.ellipsis(25)}]
            })
        },
        error: function(error){
            console.log(error);
        }
    });


    // Mine on click
    $("#mine_button").click(function(){
        loading(true);
        $.ajax({
            url: "/mine",
            type: "GET",
            success: function(response){
                window.location.reload();
            },
            error: function(error){
                console.log(error);
                loading(false);
            }
        });
    });


    // Loading mining button
    var loading = function(isLoading){
        if (isLoading){
            // Disable the mining button and show spinner
            $("#mine_button").prop("disabled", true);
            $("#spinner").removeClass("scbc-hidden");
            $("#mine_button_text").addClass("scbc-hidden");
        } else {
            // Enable the mining button and remove spinner
            $("#mine_button").prop("disabled", false);
            $("#spinner").addClass("scbc-hidden");
            $("#mine_button_text").removeClass("scbc-hidden");
        }
    };


    // Refresh transactions on click
    $("#refresh_transactions").click(function (){
        window.location.reload();
    });


    // Refresh blockchain on click
    $("#refresh_blockchain").click(function (){
        $.ajax({
            url: "/nodes/resolve",
            type: "GET",
            success: function(response){
                window.location.reload();
            },
            error: function(error){
                console.log(error);
            }
        });

    });
});
