from db import conn
from blockchain import Block, Blockchain

class InvalidTransactionException(Exception):
    pass
class InsufficientFundsException(Exception):
    pass


class Table:
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = f"({','.join(args)})"
        self.columnsList = args

        #if table does not already exist, create it.
        if isnewtable(table_name):
            create_data = ""
            for column in self.columnsList:
                create_data += f"{column} varchar(100),"

            cur = conn.cursor() #create the table
            cur.execute(f"CREATE TABLE {self.table}({create_data[:len(create_data)-1]})")
            cur.close()

    #get all the values from the table
    def getall(self):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {self.table}")
        data = cur.fetchall()
        return data

    #get one value from the table based on a column's data
    #EXAMPLE using blockchain: ...getone("hash","00003f73gh93...")
    def getone(self, search, value):
        data = {}
        cur = conn.cursor()
        result = cur.execute(f'SELECT * FROM {self.table} WHERE {search} = "{value}"')
        if result:
            data = cur.fetchone()
        cur.close()
        return data

    #delete a value from the table based on column's data
    def deleteone(self, search, value):
        cur = conn.cursor()
        cur.execute(f'DELETE from {self.table} where {search} = "{value}"')
        conn.commit()
        cur.close()

    #delete all values from the table.
    def deleteall(self):
        self.drop() #remove table and recreate
        self.__init__(self.table, *self.columnsList)

    def drop(self):
        cur = conn.cursor()
        cur.execute(f"DROP TABLE {self.table}")
        cur.close()

    #insert values into the table
    def insert(self, *args):
        data = ""
        for arg in args: #convert data into string format
            data += f'"{arg}",'

        cur = conn.cursor()
        cur.execute(f"INSERT INTO {self.table}{self.columns} VALUES({data[:len(data)-1]})")
        conn.commit()
        cur.close()


def sql_raw(execution):
    cur = conn.cursor()
    cur.execute(execution)
    conn.commit()
    cur.close()

#check if table already exists
def isnewtable(tableName):
    cur = conn.cursor()

    try: #attempt to get data from table
        result = cur.execute("SELECT * from %s" %tableName)
        cur.close()
    except:
        return True
    else:
        return False

#check if user already exists
def isnewuser(username):
    #access the users table and get all values from column "username"
    users = Table("users", "name", "email", "username", "password")
    data = users.getall()
    usernames = [user[2] for user in data]

    return False if username in usernames else True

#send money from one user to another
def send_money(sender, recipient, amount):
    #verify that the amount is an integer or floating value
    try: amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.")

    #verify that the user has enough money to send (exception if it is the BANK)
    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient Funds.")

    #verify that the user is not sending money to themselves or amount is less than or 0
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException("Invalid Transaction.")

    #verify that the recipient exists
    elif isnewuser(recipient):
        raise InvalidTransactionException("User Does Not Exist.")

    #update the blockchain and sync to mysql
    blockchain = get_blockchain()
    number = len(blockchain.chain) + 1
    data = f"{sender}-->{recipient}-->{amount}"
    blockchain.mine(Block(number, data=data))
    sync_blockchain(blockchain)

#get the balance of a user
def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()

    #loop through the blockchain and update balance
    for block in blockchain.chain:
        data = block.data.split("-->")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance

def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    for block in blockchain_sql.getall():
        blockchain.add(Block(int(block[0]), block[2], block[3], int(block[-1])))

    return blockchain

def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    blockchain_sql.deleteall()

    for block in blockchain.chain:
        blockchain_sql.insert(str(block.block_number), block.hash(), block.previous_hash, block.data, block.nonce)

