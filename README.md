# Weepo Chain

This is an experimental blockchain, with a custom API and UI. This blockchain is secured with a Proof of Work consensus mechanism, and the blocks store transaction data between addresses.

#### HTTP Server
The API handles requests to the blockchain, wallets, addresses, transactions, nodes, and mining.

The available endpoints are the following:

##### Blockchain

|Method|URL|Location|Description|
|------|---|--------|-----------|
|GET|/blockchain/blocks|blockchain|Get all blocks|
|GET|/blockchain/block?index={index}|blockchain|Get block by index|
|GET|/blockchain/block?hash={hash}|blockchain|Get block by hash|
|GET|/blockchain/block/latest|blockchain|Get the latest block|
|GET|/blockchain/block/latest/hash|blockchain|Get the latest block's hash|
|POST|/blockchain/transactions/new|blockchain|Add new transactions|
|GET|/blockchain/transactions|blockchain|Get unconfirmed transactions|

##### Client
|Method|URL|Location|Description|
|------|---|--------|-----------|
|POST|/client/transactions/make|client|Generate new transactions|

##### Miner
|Method|URL|Location|Description|
|------|---|--------|-----------|
|POST|/miner/mine|blockchain|Mine a new block|

##### Nodes
|Method|URL|Location|Description|
|------|---|--------|-----------|
|POST|/nodes/register|blockchain|Connect new nodes|
|GET|/nodes/resolve|blockchain|Resolve conflicts between nodes|
|GET|/nodes/peers|blockchain|Get all peers connected to node|

##### Wallet
|Method|URL|Location|Description|
|------|---|--------|-----------|
|GET|/wallet/new|client|Create a new blockchain wallet|
|POST|/wallet/balance|blockchain|Get blockchain wallet's balance|