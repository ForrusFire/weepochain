import hashlib
import json
from time import time
from collections import OrderedDict

from itertools import permutations
import random

import binascii
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA


class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

        # (TODO) Add a node list with node ids on the network;
        # will also probably need methods that add nodes to the network

    def print_blockchain(self):
        """
        Prints the blockchain
        """
        for block in self.chain:
            print(block)
            print()

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

        # (TODO): Add mining reward

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
         - Find a number p such that hash(last_hash + p) contains leading 4 zeroes
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
        Validates the Proof: Does hash(last_hash, proof) contain 4 leading zeroes?
        Returns a bool that validates the proof
        """

        guess = f'{last_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    @staticmethod
    def valid_chain(self, chain):
        """
        (TODO): Check if a blockchain is valid
        """
    
    def resolve_conflicts(self):
        """
        (TODO): Resolve conflicts between blockchain nodes
        by replacing our chain with the longest one in the network.
        """


# (TODO): Put the Transaction class in a separate client file with Flask
class Transaction:
    def __init__(self, sender, sender_private_key, recipient, amount):
        self.sender = sender
        self.sender_private_key = sender_private_key
        self.recipient = recipient
        self.amount = amount

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        """
        Returns the transaction as an ordered dictionary
        """
        return OrderedDict({'sender': self.sender,
                            'recipient': self.recipient,
                            'amount': self.amount})

    def sign_transaction(self):
        """
        Signs the transaction with the sender's private key and returns the signature
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

def new_wallet():
    """
    Creates a new wallet with a public and private key
    """
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    keys = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    return keys



if __name__ == "__main__":
    # create blockchain instance
    blockchain = Blockchain()
    random.seed(0)

    # establish users and users' wallets
    users = ["Alice", "Bob", "Carmen", "Dan", "Edgar"]
    users_perm = list(permutations(users, 2))
    wallets = {user: new_wallet() for user in users}

    # parameters
    max_amount = 100

    num_transactions = 5
    num_blocks = 10

    for _ in range(num_blocks-1):
        # adds five new transactions from the user list
        for _ in range(num_transactions):
            sender, recipient = users_perm[random.randint(1, len(users_perm)-1)]
            amount = random.randint(1, max_amount)
            
            transaction = Transaction(wallets[sender]['public_key'], wallets[sender]['private_key'], wallets[recipient]['public_key'], amount)
            blockchain.new_transaction(transaction.to_dict(), transaction.sign_transaction())
        
        # mine new block
        last_hash = blockchain.hash(blockchain.last_block)
        proof = blockchain.proof_of_work()

        # verify proof
        if blockchain.valid_proof(last_hash, proof):
            blockchain.new_block(proof)
            print("Block successfully added")
        else:
            print("Proof is not valid")
        
    # print status
    blockchain.print_blockchain()