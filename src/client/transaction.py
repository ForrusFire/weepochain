from collections import OrderedDict

import binascii
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA


# TODO: Consolidate globals
TRANSACTION_FEE = 1


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



