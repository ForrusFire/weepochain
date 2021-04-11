import sqlite3


def save_block(block):
    conn = sqlite3.connect('weepochain/data/blocks.db')
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


def load_blocks():
    conn = sqlite3.connect('weepochain/data/blocks.db')
    cur = conn.cursor()

    for row in cur.execute("SELECT * FROM blocks"):
        print(row)

    conn.close()


def clear_blocks():
    conn = sqlite3.connect('weepochain/data/blocks.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM blocks")

    # Save changes
    conn.commit()
    conn.close()


if __name__ == "__main__":
    load_blocks()