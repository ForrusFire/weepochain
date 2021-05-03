$(document).ready(function(){

    // Load unmined transactions
    $.ajax({
        url: "/blockchain/transactions",
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
        url: "/blockchain/blocks",
        type: "GET",
        success: function(response){
            var count = 0;
            var row = $('<div>', {class: "row"});

            // Add four blocks to each row, starting from the latest block
            for (i = response['length']-1; i >= 0; i--) {
                // Creates card text HTML element
                var card_text = $('<div>', {class: "card-text"});
                
                // Determine the current block's hash
                var hash = create_current_block_hash(i, response);

                // Genesis block
                if (i == 0) {
                    // Append genesis card with index and 'Genesis' title
                    let block_index = $('<h4>', {text: "Block #" + response['chain'][i]['index']});
                    let hr = $('<hr>');
                    let genesis_tag = $('<h3>', {class: "text-center text-secondary", text: "Genesis"})
                    card_text.append(block_index, hash, hr, genesis_tag);

                    // Assemble the block and add it to the row
                    let block = assemble_block(card_text);

                    row.append(block);
                    continue;
                };

                // Append card header with index, hash, and previous hash
                let block_index = $('<h4>', {text: "Block #" + response['chain'][i]['index']});
                let prev_hash = create_prev_block_hash(response);
                let hr = $('<hr>');
                card_text.append(block_index, hash, prev_hash, hr);

                // Add the block's transactions
                for (j = 0; j < response['chain'][i]['transactions'].length; j++){
                    let recipient_str = response['chain'][i]['transactions'][j]['recipient'];
                    let recipient_str_trim = str_trim(recipient_str, 6);
                    let sender_str = response['chain'][i]['transactions'][j]['sender'];
                    let sender_str_trim = str_trim(sender_str, 6);

                    let transaction = create_transaction(response, recipient_str_trim, sender_str_trim);

                    // Append transaction to card
                    card_text.append(transaction);
                };

                // Format date and time, and append it to the card
                var options = {year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"};
                var date = new Date(response["chain"][i]["timestamp"] * 1000);
                var formattedDateTime = $('<div>', {class: "text-end text-muted", text: date.toLocaleTimeString("en-us", options)});
                card_text.append(formattedDateTime);
                

                // Assemble the block and add it to the row
                let block = assemble_block(card_text);
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


    // Create and return transaction element
    function create_transaction(response, recipient_str, sender_str) {
        let transaction;

        // Change the transaction's background color depending on the type of transaction
        if (response['chain'][i]['transactions'][j]['sender'] == 'blockchain'){
            // Reward transaction
            transaction = $('<div>', {class: "alert alert-warning", text: "   " + response['chain'][i]['transactions'][j]['amount'] + " to "});

            let arrow = $('<span>', {class: "fa fa-angle-double-right"}); // Add right arrow
            transaction.prepend(arrow);
            transaction.append(recipient_str);
        } else if (response['chain'][i]['transactions'][j]['recipient'] == 'blockchain'){
            // Transaction fee
            transaction = $('<div>', {class: "alert alert-danger", text: "   " + response['chain'][i]['transactions'][j]['amount'] + " from "});

            let arrow = $('<span>', {class: "fa fa-angle-double-left"}); // Add left arrow
            transaction.prepend(arrow);
            transaction.append(sender_str);
        } else {
            // Standard transaction
            transaction = $('<div>', {class: "alert alert-success"});
            
            let recipient = $('<span>', {text: "   " + response['chain'][i]['transactions'][j]['amount'] + " to "});
            recipient.append(recipient_str);
            let arrow = $('<span>', {class: "fa fa-angle-double-right"}); // Add right arrow
            transaction.append(arrow, recipient);

            let br = $('<br><br>');

            let sender = $('<span>', {text: "   " + response['chain'][i]['transactions'][j]['amount'] + " from "});
            sender.append(sender_str);
            arrow = $('<span>', {class: "fa fa-angle-double-left"}); // Add left arrow
            transaction.append(br, arrow, sender);
        };
        
        return transaction
    }; 
    
    
    // Creates an element that contains the current block's hash
    function create_current_block_hash(i, response) {
        let hash = $('<span>', {text: "Hash: "});

        let hash_str;
        if (i != response['length']-1) {
            hash_str = response['chain'][i+1]['previous_hash']; // Set hash as previous hash of block in front of it
        } else {
            hash_str = get_latest_block_hash(); // For the latest block, get the hash explicitly since there is no block in front of it
        };

        let hash_str_trim = str_trim(hash_str, 5);
        hash.append(hash_str_trim);
        return hash
    };
    
    
    // Get the last block's hash
    function get_latest_block_hash() {
        var latest_block_hash;
        $.ajax({
            url: "/blockchain/block/latest/hash",
            type: "GET",
            async: false,
            success: function(response){
                latest_block_hash = response;
            },
            error: function(error){
                console.log(error);
            },
        });
        return latest_block_hash;
    };


    // Creates an element that contains the previous block's hash
    function create_prev_block_hash(response) {
        let prev_hash = $('<p>', {text: "Previous Hash: "});
        let prev_hash_str = response['chain'][i]['previous_hash'];
        let prev_hash_str_trim = str_trim(prev_hash_str, 5);
        prev_hash.append(prev_hash_str_trim);
        return prev_hash
    };

    
    // Trims a string and returns a strong element, leaving front and end of string
    function str_trim(string, n) {
        let trimmed_string = string.substring(0, n) + "..." + string.substring(string.length - n, string.length);
        return $('<strong>', {text: trimmed_string})
    };


    // Assembles block, given card text
    function assemble_block(card_text) {
        var block = $('<div>', {class: "col-lg-3"});
        var card = $('<div>', {class: "card"})
        var card_body = $('<div>', {class: "card-body"});

        card_body.append(card_text);
        card.append(card_body);
        block.append(card);
        return block
    };


    // Mine on click
    $("#mine_button").click(function(){
        loading(true);
        $.ajax({
            url: "/miner/mine",
            type: "POST",
            dataType : 'json',
            data: $('#mine_form').serialize(),
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