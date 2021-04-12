import sqlite3


DB_PATH = 'weepochain/data/blocks.db'

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE blocks
               (ind real, time real, trans text, proof real, prev_hash text)''')

    # Save changes
    conn.commit()
    conn.close()


def print_blocks():
    """
    Prints the current blocks in the database
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for row in cur.execute("SELECT * FROM blocks"):
        print(row)

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


if __name__ == "__main__":
    print_blocks()