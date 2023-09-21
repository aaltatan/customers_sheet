const modalBtns = document.querySelectorAll("button[data-modal]");
const modal = document.getElementById("exampleModal");
const modalTitle = document.getElementById("exampleModalLabel");
const modalCloseBtns = document.querySelectorAll(
  "button[data-bs-dismiss='modal']"
);

modalCloseBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal.querySelectorAll("input").forEach((input) => {
      input.value = "";
    });
  });
});

modalBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    let type = btn.getAttribute("data-modal");
    let amount = btn.parentElement.getAttribute("data-amount");
    let userId = btn.parentElement.getAttribute("data-customer-id");
    let amountInput = modal.querySelector("input[type='number']");

    if (type === "sales") {
      modalTitle.innerHTML = "اضافة مبيعات";
      amountInput.value = 0;
    } else {
      modalTitle.innerHTML = "اضافة مقبوضات";
      amountInput.value = -amount;
    }

    modal.querySelector("input[type='text']").value = userId;
  });
});
