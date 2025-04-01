from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

@app.route("/")
def index():
    return render_template("index.html", chain=blockchain.chain)

@app.route("/transactions/new", methods=["GET", "POST"])
def new_transaction():
    if request.method == "POST":
        values = request.get_json()
        required = ["sender", "recipient", "amount"]
        if not all(k in values for k in required):
            return jsonify({"message": "Thiếu thông tin giao dịch"}), 400

        index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
        return jsonify({"message": f"Giao dịch sẽ được thêm vào block {index}"}), 201
    return render_template("transactions.html")

@app.route("/mine", methods=["POST"])
def mine_block():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block["proof"])
    blockchain.new_transaction(sender="0", recipient="miner_address", amount=1)
    new_block = blockchain.new_block(proof)

    return jsonify({
        "message": "Block mới đã được tạo!",
        "block": new_block
    }), 201

@app.route("/transactions/history", methods=["GET"])
def transaction_history():
    transactions = []
    for block in blockchain.chain:
        transactions.extend(block["transactions"])
    return jsonify({"transactions": transactions}), 200

@app.route("/chain")
def view_chain():
    return render_template("chain.html", chain=blockchain.chain)

if __name__ == "__main__":
    app.run(debug=True)
