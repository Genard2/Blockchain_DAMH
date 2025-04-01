document.addEventListener("DOMContentLoaded", function () {
    const transactionForm = document.getElementById("transaction-form");
    
    if (transactionForm) {
        transactionForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Ngăn chặn form reload trang
            
            const sender = document.getElementById("sender").value;
            const recipient = document.getElementById("recipient").value;
            const amount = document.getElementById("amount").value;

            fetch("/transactions/new", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sender, recipient, amount })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.href = "/"; // Quay lại trang chính sau khi thêm giao dịch
            })
            .catch(error => console.error("Lỗi khi gửi giao dịch:", error));
        });
    }
});
