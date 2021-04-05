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


    // Load blocks on the chain
    $.ajax({
        url: "/blocks",
        type: "GET",
        success: function(response){
            var count = 0;
            var row = $('<div>', {class: "row"});

            // Add four blocks to each row, starting from the latest block
            for (i = response['length']-1; i >= 0; i--){
                // Create block html elements
                var block = $('<div>', {class: "col-lg-3"});
                var card = $('<div>', {class: "card"})
                var card_body = $('<div>', {class: "card-body"});
                var card_text = $('<div>', {class: "card-text"});
                

                // Don't add transactions to the genesis block
                if (i != 0) {
                    // Append card header with index and previous hash
                    var block_index = $('<h4>', {text: "Block #" + response['chain'][i]['index']});
                    var prev_hash_str = response['chain'][i]['previous_hash'];
                    var prev_hash = $('<strong>', {text: prev_hash_str.substring(0, 5) + "..." + prev_hash_str.substring(prev_hash_str.length - 5, prev_hash_str.length)});
                    var prev_hash_elem = $('<p>', {text: "Previous Hash: "});
                    var hr = $('<hr>');
                    prev_hash_elem.append(prev_hash);
                    card_text.append(block_index, prev_hash_elem, hr);

                    // Add the block's transactions
                    var transaction;
                    for (j = 0; j < response['chain'][i]['transactions'].length; j++){
                        var recipient_str = response['chain'][i]['transactions'][j]['recipient'];
                        var recipient = $('<strong>', {text: recipient_str.substring(0, 6) + "..." + recipient_str.substring(recipient_str.length - 6, recipient_str.length)});
                        var sender_str = response['chain'][i]['transactions'][j]['sender'];
                        var sender = $('<strong>', {text: sender_str.substring(0, 6) + "..." + sender_str.substring(sender_str.length - 6, sender_str.length)});

                        // Change the transaction's background color depending on the type of transaction
                        if (response['chain'][i]['transactions'][j]['sender'] == 'blockchain'){
                            // Reward transaction
                            transaction = $('<div>', {class: "alert alert-warning", text: response['chain'][i]['transactions'][j]['amount'] + " to "});
                            transaction.append(recipient);
                        } else {
                            // Standard transaction
                            transaction = $('<div>', {class: "alert alert-success"});
                            
                            var recipient_transaction = $('<div>', {text: response['chain'][i]['transactions'][j]['amount'] + " to "});
                            recipient_transaction.append(recipient);
                            transaction.append(recipient_transaction);

                            var sender_transaction = $('<div>', {text: response['chain'][i]['transactions'][j]['amount'] + " from "});
                            sender_transaction.append(sender);
                            var br = $('<br>');
                            transaction.append(br, sender_transaction);
                        };

                        // Append transaction to card
                        card_text.append(transaction);
                    };

                    // Format date and time, and append it to the card
                    var options = {year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"};
                    var date = new Date(response["chain"][i]["timestamp"] * 1000);
                    var formattedDateTime = $('<div>', {class: "text-end text-muted", text: date.toLocaleTimeString("en-us", options)});
                    card_text.append(formattedDateTime);
                } else {
                    // Append card with index and 'Genesis' title
                    var block_index = $('<h4>', {text: "Block #" + response['chain'][i]['index']});
                    var hr = $('<hr>');
                    var genesis_tag = $('<h3>', {class: "text-center text-secondary", text: "Genesis"})
                    card_text.append(block_index, hr, genesis_tag);
                };
                

                // Assemble the block and add it to the row
                card_body.append(card_text);
                card.append(card_body);
                block.append(card);
                row.append(block);

                // Move down a row every four blocks
                count += 1;
                if (count % 4 == 0) {
                    var br = $('<br><br>');
                    $('#blockchain_visualizer').append(row, br);
                    row = $('<div>', {class: "row"});
                };
            };
            
            // Append final row
            $('#blockchain_visualizer').append(row);
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


    // Add nodes
    $('#add_node_button').click(function(){
        $.ajax({
            url: "/nodes/register",
            type: "POST",
            dataType : 'json',
            data: $('#node_form').serialize(),
            success: function(response){
                console.log(response);
                document.getElementById("nodes").value = "";  
                window.location.reload();
            },
            error: function(error){
                console.log(error);
            },
        });
    });


    // Load nodes
    $.ajax({
        url: '/nodes/peers',
        type: 'GET',
        success: function(response){
            console.log(response['nodes']);
            var node = '';
            
            for (i = 0; i < response['nodes'].length; i++){
                node = "<li> <a href=http://" + response['nodes'][i] + ">" + response['nodes'][i] + "</a></li>";
                document.getElementById("list_nodes").innerHTML += node;
            };
        },
        error: function(error){
            console.log(error);
        },
    });
});