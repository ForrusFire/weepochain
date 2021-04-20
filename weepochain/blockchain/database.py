import sqlite3

from collections import OrderedDict


DB_PATH = 'weepochain/data/blocks.db'

def save_block(block):
    """
    Saves a block into the database
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Turn the transactions list into a string
    transactions_str = ''
    for transaction in block['transactions']:
        transactions_str += transaction['sender'] + "," + transaction['recipient'] + "," + str(transaction['amount']) + ","

    cur.execute("INSERT INTO blocks VALUES (?, ?, ?, ?, ?)", 
            (block['index'], block['timestamp'], transactions_str, block['proof'], block['previous_hash']))

    # Save changes
    conn.commit()
    conn.close()


def save_blocks(chain):
    """
    Saves an entire chain into the database
    """
    conn = sqlite3.connect(DB_PATH)

    clear_blocks()

    for block in chain:
        save_block(block)

    # Save changes
    conn.commit()
    conn.close()


def load_blocks(blockchain):
    """
    Loads all blocks from the database onto the chain OR
    saves the genesis block if the database is empty
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # If there are zero or one items in the database, save the new genesis block
    cur.execute("SELECT COUNT (*) FROM blocks")
    if cur.fetchone()[0] <= 1:
        clear_blocks()
        save_block(blockchain.chain[0])

    # Otherwise, load the database into the chain
    else:
        # Pop current genesis block
        blockchain.db_pop_genesis()

        # Iterate through database
        for row in cur.execute("SELECT * FROM blocks ORDER BY ind"):
            # Remove the comma from the end of the transaction string before splitting
            raw_transactions = row[2][:-1].split(',')

            # Generate transactions list
            transactions = []
            for i in range(len(raw_transactions) // 3):
                # Create the transaction
                transaction = OrderedDict({'sender': raw_transactions[3*i],
                        'recipient': raw_transactions[3*i + 1],
                        'amount': int(raw_transactions[3*i + 2])})
                transactions.append(transaction)

            # Create block
            block = {
                'index': row[0],
                'timestamp': row[1],
                'transactions': transactions,
                'proof': row[3],
                'previous_hash': row[4],
            }

            # Add block to the chain
            blockchain.db_add_block(block)

    conn.close()


def clear_blocks():
    """
    Clears all blocks from the database
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM blocks")

    # Save changes
    conn.commit()
    conn.close()
