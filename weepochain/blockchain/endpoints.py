from flask import Blueprint, jsonify, request, render_template

from collections import OrderedDict

from ..constants import MINING_ADDRESS, TRANSACTION_FEE, MINING_REWARD
from .__init__ import blockchain


bp = Blueprint('bp', __name__)

@bp.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@bp.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')



@bp.route('/blockchain/blocks', methods=['GET'])
def get_blocks():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@bp.route('/blockchain/block', methods=['GET'])
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


@bp.route('/blockchain/block/latest', methods=['GET'])
def get_latest_block():
    return jsonify(blockchain.last_block), 200


@bp.route('/blockchain/block/latest/hash', methods=['GET'])
def get_latest_block_hash():
    return jsonify(blockchain.hash(blockchain.last_block)), 200


@bp.route('/blockchain/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form

    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(i in values for i in required):
        return 'Missing values', 400

    # Calculate sender's balance
    balance = 0

    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['sender'] == values['sender']:
                balance -= transaction['amount']
            if transaction['recipient'] == values['sender']:
                balance += transaction['amount']
    
    for transaction in blockchain.current_transactions:
        if transaction['sender'] == values['sender']:
            balance -= transaction['amount']
        if transaction['recipient'] == values['sender']:
            balance += transaction['amount']

    # Check if the sender has enough funds
    if balance < int(values['amount']):
        return "Error: Insufficient funds", 406
    
    # Create a new transaction
    transaction = OrderedDict({'sender': values['sender'],
                            'recipient': values['recipient'],
                            'amount': int(values['amount']) - TRANSACTION_FEE})

    transaction_result = blockchain.new_transaction(transaction, values['signature'])

    if transaction_result == -1:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        # Add transaction fee
        transaction_fee = OrderedDict({'sender': values['sender'],
                                    'recipient': MINING_ADDRESS,
                                    'amount': TRANSACTION_FEE})
        blockchain.new_transaction(transaction_fee, "")

        response = {'message': 'Transaction will be added to Block ' + str(transaction_result)}
        return jsonify(response), 201


@bp.route('/blockchain/transactions', methods=['GET'])
def get_transactions():
    # Get unconfirmed transactions from blockchain
    transactions = blockchain.current_transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


@bp.route('/miner/mine', methods=['POST'])
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


@bp.route('/nodes/register', methods=['POST'])
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


@bp.route('/nodes/resolve', methods=['GET'])
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


@bp.route('/nodes/peers', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


@bp.route('/wallet/balance', methods=['POST'])
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


@bp.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404