# Weepo Blockchain

This is an experimental blockchain, with a custom API and UI.

#### HTTP Server
The API handles requests to the blockchain, wallets, addresses, transactions, nodes, and mining.

The available endpoints are the following:

##### Blockchain

|Method|URL|Description|
|------|---|-----------|
|GET|/blockchain/blocks|Get all blocks|
|GET|/blockchain/block?index={index}|Get block by index|
|GET|/blockchain/block?hash={hash}|Get block by hash|
|GET|/blockchain/block/latest|Get the latest block|
|GET|/blockchain/block/latest/hash|Get the latest block's hash|
|POST|/blockchain/transactions/new|Add new transaction|
|GET|/blockchain/transactions|Get unconfirmed transactions|
|POST|/blockchain/mine|Mine a new block|
|POST|/blockchain/nodes/register|Create new nodes|
|GET|/blockchain/nodes/resolve|Resolve conflicts between nodes|
|GET|/blockchain/nodes/peers|Get all peers connected to node|
|POST|/blockchain/wallet/balance|Get blockchain wallet balance|


##### Client
|Method|URL|Description|
|------|---|-----------|
|GET|/client/wallet/new|Create a new blockchain wallet|
|POST|/client/transactions/make|Generate new transaction|