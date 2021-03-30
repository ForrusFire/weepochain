# PogU-Niversity-Coin

This is a test blockchain, with a custom API and UI.

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
|POST|/blockchain/transactions/new|Add new transaction|
|GET|/blockchain/transactions|Get unconfirmed transactions|
|GET|/blockchain/mine|Mine a new block|
|POST|/blockchain/nodes/register|Create new nodes|
|GET|/blockchain/nodes/resolve|Resolve conflicts between nodes|
|GET|/blockchain/nodes/peers|Get all peers connected to node|