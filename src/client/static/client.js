$(document).ready(function(){

    // Show the balance of the requested wallet
    $('#view_balance').click(function(){
        $.ajax({
            url: $('#node_url').val() + '/wallet/balance',
            type: 'POST',
            dataType : 'json',
            data: $('#wallet_address').serialize(),
            success: function(response){
                $('#wallet_balance').html(response);
                $('#wallet_balance_card').removeClass('scc-hidden');
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
            url: '/client/transactions/make',
            type: 'POST',
            dataType : 'json',
            data: $('#transaction_form').serialize(),
            success: function(response){
                // Fill in modal values
                $('#confirmation_sender').val(response['transaction']['sender']);
                $('#confirmation_recipient').val(response['transaction']['recipient']);
                $('#confirmation_amount').val(response['amount']);
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
            url: $('#node_url').val() + '/blockchain/transactions/new',
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