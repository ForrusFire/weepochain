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


    // Generate Wallet
    $('#wallet_generator').click(function(){
        $.ajax({
            url: '/wallet/new',
            type: 'GET',
            success: function(response){
                // Display the wallet keys
                $('#public_key').html(response['public_key']);
                $('#private_key').html(response['private_key']);
                $('#warning').removeClass('scc-hidden');
            },
            error: function(error){
                console.log(error);
            },
        });
    });


    // Create new transaction
    $('#generate_transaction').click(function(){
        $.ajax({
            url: '/transactions/make',
            type: 'POST',
            dataType : 'json',
            data: $('#transaction_form').serialize(),
            success: function(response){
                // Fill in modal values
                $('#confirmation_sender').val(response['transaction']['sender']);
                $('#confirmation_recipient').val(response['transaction']['recipient']);
                $('#confirmation_amount').val(response['transaction']['amount']);
                $('#transaction_signature').val(response['signature']);

                $('#transactionModal').modal('show');
            },
            error: function(error){
                console.log(error);
            },
        });
    });


    // Confirm transaction
    $('#button_confirm_transaction').click(function(){
        $.ajax({
            url: $('#node_url').val() + '/transactions/new',
            type: 'POST',
            headers: {'Access-Control-Allow-Origin':'*'},
            dataType: 'json',
            data: $('#confirmation_transaction_form').serialize(),
            success: function(response){
                // Reset forms
                $("#transaction_form")[0].reset();
                $("#confirmation_transaction_form")[0].reset();
                                
                // Clean text boxes
                $("#sender").val("");
                $("#sender_private_key").val("");
                $("#recipient").val("");
                $("#amount").val("");

                $("#transactionModal").modal('hide');
                $("#success_transaction_modal").modal('show');
            },
            error: function(error){
                console.log(error);
            },
        });
    });
});