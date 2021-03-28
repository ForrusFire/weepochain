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