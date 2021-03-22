import hashlib
import json
from time import time

from itertools import permutations
import random

# starting methods below taken from https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def print_blockchain(self):
        for block in self.chain:
            print(block)
            print()

    def new_block(self, proof, previous_hash=None):
        # creates a new block        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # add the new block to the chain
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        # adds a transaction to the current list
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        # returns index of block this transaction is in
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        # hashes a block

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode('utf-8')

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # returns the last block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"




if __name__ == "__main__":
    # simple testing
    blockchain = Blockchain()

    random.seed(0)

    users = ["Alice", "Bob", "Carmen", "Dan", "Edgar"]
    perm = list(permutations(users, 2))
    max_amount = 100

    num_transactions = 5
    num_blocks = 10

    for _ in range(num_blocks-1):
        # adds five new transactions from the user list
        for i in range(5):
            transaction = perm[random.randint(1, len(perm)-1)]
            amount = random.randint(1, max_amount)

            blockchain.new_transaction(transaction[0], transaction[1], amount)
        
        # mine new block
        last_proof = blockchain.last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # verify proof
        if blockchain.valid_proof(last_proof, proof):
            blockchain.new_block(proof)
            print("Block successfully added")
        else:
            print("Proof is not valid")
        
    # print status
    blockchain.print_blockchain()