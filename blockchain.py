import hashlib
import json
import time
from uuid import uuid4

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash="1", proof=100)  # Tạo block gốc

    def new_block(self, proof, previous_hash=None):
        """Tạo một block mới"""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """Thêm giao dịch mới"""
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        })
        return self.last_block["index"] + 1

    @staticmethod
    def hash(block):
        """Tạo hash SHA-256 cho block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Lấy block cuối cùng"""
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """Thuật toán Proof of Work"""
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """Kiểm tra proof hợp lệ"""
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
