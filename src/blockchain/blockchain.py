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

from constants import MINING_ADDRESS, MINING_REWARD, TRANSACTION_FEE


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
        # if the transaction is a mining reward or transaction fee, skip verification
        if transaction["sender"] == MINING_ADDRESS or transaction['recipient'] == MINING_ADDRESS:
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