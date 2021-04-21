# Weepo Chain

This is an experimental blockchain built from scratch, with a custom API and UI. The features of the blockchain are as follows:

* Proof of Work consensus mechanism, motivated by Satoshi Nakomoto's original paper
* Simple UTXO based transaction model with client-side account balances
* HTTP interface to control nodes on the network
* Simple conflict resolution between nodes


### Setup

For quick installation, enter:
   ```sh
   git clone https://github.com/ForrusFire/weepochain
   cd weepochain
   pip install -r requirements.txt
   ```

##### Node 
To start a blockchain node, execute run_blockchain.py
   ```sh
   python (insert path to run_blockchain.py here)
   ```

The default node port is http://localhost:5000/. Add another node to the blockchain by specifying a port that is not in use. For example:
   ```sh
   python (insert path to run_blockchain.py here) -p 5001
   ```

Access the blockchain node dashboard in order to mine blocks and receive mining rewards.

##### Client
To create wallets and send Weepo Coins, execute run_client.py
   ```sh
   python (insert path to run_blockchain.py here)
   ```

Then, access the client through http://localhost:8080/


### Node Network
The network uses websockets to communicate with other nodes (P2P). The communication protocols ensure that the longest valid chain is dominant on the network, and
node conflicts are resolved through chain length.

New nodes must connect to at least one node already on the network. This acts as an 'invite' to the main chain.

Node data and chain resolutions are persisted to a folder.


### Wallets and Transactions
Wallets are generated with public and private key encryption based on the RSA algorithm. Transactions are also generated through RSA encryption and signatures are verified
on the nodes.


### HTTP Server
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