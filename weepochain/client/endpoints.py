from flask import Blueprint, jsonify, request, render_template

import binascii
import Crypto.Random
from Crypto.PublicKey import RSA

from .transaction import Transaction
from ..constants import TRANSACTION_FEE


bp = Blueprint('bp', __name__)


@bp.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@bp.route('/transactions/create', methods=['GET'])
def create_transaction():
    return render_template("create_transaction.html")

@bp.route('/wallet/create', methods=['GET'])
def create_wallet():
    return render_template("create_wallet.html")


@bp.route('/wallet/new', methods=['GET'])
def new_wallet():
    """
    Creates a new wallet with a public and private key
    """
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    return jsonify(response), 200
    

@bp.route('/client/transactions/make', methods=['POST'])
def make_transaction():
    sender = request.form['sender']
    sender_private_key = request.form['sender_private_key']
    recipient = request.form['recipient']
    amount = request.form['amount']

    if not recipient:
        return "Error: Please input a recipient", 400

    # Check if the amount is an integer
    try:
        amount = int(amount)
    except ValueError:
        return "Error: Please input a valid amount", 400

    # Check if the amount is greater than or equal to the transaction fee
    if amount < TRANSACTION_FEE:
        return "Error: Please input a valid amount", 400

    # Create the transaction
    transaction = Transaction(sender, sender_private_key, recipient, amount - TRANSACTION_FEE)

    # Check if the private key is valid
    # TODO: Check if private key and public key match
    try:
        response = {'transaction': transaction.to_dict(), 'amount': amount, 'signature': transaction.sign_transaction()}
    except (ValueError, TypeError):
        return "Error: Invalid private key", 406

    return jsonify(response), 200