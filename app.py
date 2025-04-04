from datetime import datetime  # Đảm bảo có dòng này ở trên cùng
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import time
from datetime import datetime
from decimal import Decimal
from flask_migrate import Migrate  # Import Migrate
from models import db, User, Transaction  # 👉 Import từ models.py
from blockchain import Blockchain         # Import Blockchain bình thường

# Khởi tạo ứng dụng và các công cụ
app = Flask(__name__)
app.config.from_object('config.Config')

# Khởi tạo các công cụ
db.init_app(app)     # 👉 Khởi tạo SQLAlchemy từ models
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)
# Khởi tạo blockchain
blockchain = Blockchain()

# Load user cho Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Trang chủ
@app.route("/")
def index():
    return render_template("index.html", chain=blockchain.chain, user=current_user if current_user.is_authenticated else None)

# Đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password_raw = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password_raw != confirm_password:
            return "Mật khẩu xác nhận không khớp!"

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return "Tên đăng nhập hoặc email đã tồn tại!"

        password = bcrypt.generate_password_hash(password_raw).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html")

# Đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        return "Sai tài khoản hoặc mật khẩu!"
    return render_template("login.html")

# Đăng xuất
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Gửi giao dịch mới
@app.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'GET':
        return render_template('transactions.html', user=current_user)
    
    data = request.get_json()
    required_fields = ['sender', 'recipient', 'amount']
    
    # Kiểm tra các trường cần thiết
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Thiếu thông tin giao dịch'}), 400

    sender = data['sender']
    recipient = data['recipient']
    amount = Decimal(str(data['amount']))  # Chuyển đổi sang Decimal để tính toán chính xác hơn

    # Tìm người gửi và người nhận
    sender_user = User.query.filter_by(username=sender).first()
    recipient_user = User.query.filter_by(username=recipient).first()

    if not sender_user or not recipient_user:
        return jsonify({'message': 'Không tìm thấy người dùng'}), 404

    sender_balance = Decimal(str(sender_user.balance))
    
    # Kiểm tra số dư của người gửi
    if sender_balance < amount:
        return jsonify({'message': 'Số dư không đủ'}), 400

    # Cập nhật số dư người gửi và người nhận
    sender_user.balance = sender_balance - amount
    recipient_user.balance = Decimal(str(recipient_user.balance)) + amount
    db.session.commit()

    # Lưu giao dịch vào cơ sở dữ liệu
    tx = Transaction(sender=sender, recipient=recipient, amount=amount, timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(tx)
    db.session.commit()

    # Thực hiện giao dịch trên blockchain
    block_index = blockchain.new_transaction(sender, recipient, amount)

    # Tính toán proof-of-work và tạo block
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    # Trả về thông tin block
    return jsonify({
        'message': 'Giao dịch thành công',
        'block': {
            'index': block['index'],
            'previous_hash': block['previous_hash'],
            'transactions': block['transactions']
        }
    }), 201

# Mine block mới
@app.route("/mine", methods=["POST"])
@login_required
def mine_block():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block["proof"])
    blockchain.new_transaction(sender="0", recipient=current_user.username, amount=1)
    new_block = blockchain.new_block(proof)

    return jsonify({
        "message": "Block mới đã được tạo!",
        "block": new_block
    }), 201

# Xem lịch sử giao dịch
@app.route('/transactions/history')
@login_required
def transaction_history():
    transactions = db.session.query(Transaction).order_by(Transaction.timestamp.desc()).all()
    result = []
    for transaction in transactions:
        timestamp = transaction.timestamp if isinstance(transaction.timestamp, str) else transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        result.append({
            'sender': transaction.sender,
            'recipient': transaction.recipient,
            'amount': transaction.amount,
            'timestamp': timestamp
        })
    return jsonify({'transactions': result})

# Xem chuỗi blockchain
@app.route("/chain")
def view_chain():
    return render_template("chain.html", chain=blockchain.chain)

# Trang thông tin tài khoản
@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user, balance=user.balance)

# Chạy ứng dụng
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=port, debug=True)
