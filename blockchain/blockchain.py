import hashlib
import json
from time import time
from collections import OrderedDict

import binascii
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

from uuid import uuid4
from urllib.parse import urlparse

import requests
import flask
from flask import jsonify, request, render_template
from flask_cors import CORS


MINING_ADDRESS = "blockchain"
MINING_REWARD = 100


class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

        # Node list
        self.nodes = set()


    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        # Check for valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def new_block(self, proof, previous_hash=None):
        """
        Creates a new block, appends it to the chain, and returns it
        """   
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # add the new block to the chain
        self.chain.append(block)
        return block

    
    def new_transaction(self, transaction, signature):
        """
        Adds a transaction to the current list, 
        and returns the index of the block the transaction is in
        """
        # if the transaction is a mining reward, skip verification
        if transaction["sender"] == MINING_ADDRESS:
            self.current_transactions.append(transaction)
            return len(self.chain) + 1
        # if not, verify the transaction
        else:
            verification = self.verify_transaction(transaction, signature)

            # returns index of block this transaction is in, or -1 if the transaction verification failed
            if verification:
                self.current_transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return -1


    def verify_transaction(self, transaction, signature):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key
        """
        public_key = RSA.importKey(binascii.unhexlify(transaction['sender']))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))
    

    @staticmethod
    def hash(block):
        """
        Hashes a block and returns the hash
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode('utf-8')

        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        # returns the last block in the chain
        return self.chain[-1]


    def proof_of_work(self):
        """
        Proof of Work Algorithm:
         - Find a number p such that hash(last_hash + p) contains leading 6 zeroes
        Returns the new proof
        """
        last_hash = self.hash(self.last_block)

        proof = 0
        while not self.valid_proof(last_hash, proof):
            proof += 1

        return proof


    @staticmethod
    def valid_proof(last_hash, proof):
        """
        Validates the Proof: Does hash(last_hash, proof) contain 6 leading zeroes?
        Returns a bool that validates the proof
        """

        guess = f'{last_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == "000000"

    
    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain nodes
        by replacing our chain with the longest one in the network.
        """
        nodes = self.nodes
        new_chain = None

        current_length = len(self.chain)

        for node in nodes:
            response = requests.get('http://' + node + '/blocks')
            
            # Handle response
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > current_length and self.valid_chain(chain):
                    current_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True

        return False


    def valid_chain(self, chain):
        """
        Check if a blockchain is valid
        """
        # Traverse chain
        for i in range(1, len(chain)):
            # Get next block
            block = chain[i]
            
            # Check hash of the block is correct
            if block['previous_hash'] != self.hash(chain[i-1]):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(block['previous_hash'], block['proof']):
                return False

        return True



app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

# Create the blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')



@app.route('/blockchain/blocks', methods=['GET'])
def get_blocks():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/blockchain/block', methods=['GET'])
def get_block():
    query_parameters = request.args

    index = query_parameters.get('index')
    block_hash = query_parameters.get('hash')

    if index:
        for block in blockchain.chain:
            if block['index'] == int(index):
                return jsonify(block), 200
    elif block_hash:
        for block in blockchain.chain:
            if blockchain.hash(block) == block_hash:
                return jsonify(block), 200
    else:
        return page_not_found(404)


@app.route('/blockchain/block/latest', methods=['GET'])
def get_latest_block():
    return jsonify(blockchain.last_block), 200


@app.route('/blockchain/block/latest/hash', methods=['GET'])
def get_latest_block_hash():
    return jsonify(blockchain.hash(blockchain.last_block)), 200


@app.route('/blockchain/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form

    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(i in values for i in required):
        return 'Missing values', 400
    
    # Create a new transaction
    transaction = OrderedDict({'sender': values['sender'],
                            'recipient': values['recipient'],
                            'amount': values['amount']})

    transaction_result = blockchain.new_transaction(transaction, values['signature'])

    if transaction_result == -1:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to Block ' + str(transaction_result)}
        return jsonify(response), 201


@app.route('/blockchain/transactions', methods=['GET'])
def get_transactions():
    # Get unconfirmed transactions from blockchain
    transactions = blockchain.current_transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/miner/mine', methods=['POST'])
def mine():
    values = request.form
    reward_address = values.get('reward_address')

    if not reward_address:
        return "Error: Please supply a reward address", 400

    # run the POW algorithm to get the next proof
    previous_hash = blockchain.hash(blockchain.last_block)
    proof = blockchain.proof_of_work()

    # Add mining reward transaction
    mining_transaction = OrderedDict({"sender": MINING_ADDRESS,
                                    "recipient": reward_address,       
                                    "amount": MINING_REWARD})

    blockchain.new_transaction(mining_transaction, "")

    # Add the new block to the chain
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes == ['']:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/peers', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


@app.route('/wallet/balance', methods=['POST'])
def get_balance():
    values = request.form
    wallet_address = values.get('wallet_address')

    balance = 0

    # Iterate through block's transactions
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['sender'] == wallet_address:
                balance -= transaction['amount']
            if transaction['recipient'] == wallet_address:
                balance += transaction['amount']
    
    # Iterate through pending transactions
    for transaction in blockchain.current_transactions:
        if transaction['sender'] == wallet_address:
            balance -= transaction['amount']
        if transaction['recipient'] == wallet_address:
            balance += transaction['amount']

    return jsonify(balance), 200


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)