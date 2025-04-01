document.addEventListener("DOMContentLoaded", function () {
    fetch("/chain")
    .then(response => response.json())
    .then(data => {
        console.log("Blockchain hiện tại:", data);
    })
    .catch(error => console.error("Lỗi khi tải blockchain:", error));
});
