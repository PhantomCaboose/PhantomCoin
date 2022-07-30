import hashlib

class Block:
    def __init__(self,block_number = 0, previous_hash = '0' * 64, data = None, nonce = 0):
        self.data = data
        self.block_number = block_number
        self.previous_hash = previous_hash
        self.nonce = nonce

    def hash(self):
        return update_hash(self.previous_hash, self.block_number, self.data, self.nonce)

    def __str__(self):
        return f"Block: {self.block_number}   Nonce: {self.nonce}   Data: {self.data}\nHash: {self.hash()}\nPrevious Hash: {self.previous_hash}\n"

class Blockchain:
    difficulty = 4
    def __init__(self):
        self.chain = []

    def add(self, block):
        self.chain.append(block)

    def remove(self, block):
        self.chain.remove(block)

    def mine(self, block):
        try:
            block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass

        while True:
            if block.hash()[:self.difficulty] == '0' * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1

    def is_valid(self):
        for index in range(1, len(self.chain)):
            _previous = self.chain[index].previous_hash
            _current = self.chain[index - 1].hash()
            if (_previous != _current) or (_current[:self.difficulty] != "0" * self.difficulty):
                return "Houston we have a problem. The Blockcahin is invalid."
        return "All good. The Blockchain is valid."


def update_hash(*args):
    hashing_text = ""
    hashed = hashlib.sha256()
    for arg in args:
        hashing_text += str(arg)
    hashed.update(hashing_text.encode('utf-8'))
    return hashed.hexdigest()

def main():
    blockchain = Blockchain()
    data_list = ["hello world", "what's up", "hello", "bye"]
    num = 0
    for data in data_list:
        num += 1
        blockchain.mine(Block(data, num))

    for block in blockchain.chain:
        print(block)
    print(blockchain.is_valid())

if __name__ == "__main__":
    print("\n")
    main()