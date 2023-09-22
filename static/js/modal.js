const modalBtns = document.querySelectorAll("button[data-modal]");
const modal = document.getElementById("exampleModal");
const ledgerModal = document.getElementById("ledgerModal");
const ledgerModalLink = document.getElementById("ledger-modal-link");
const modalTitle = document.getElementById("exampleModalLabel");
const modalCloseBtns = document.querySelectorAll(
  "button[data-bs-dismiss='modal']"
);
const modalSelect = document.getElementById("select-customer");

ledgerModal.addEventListener("change", () => {
  let id = ledgerModal.querySelector("select").value;
  ledgerModalLink.setAttribute("href", "/ledger?id=" + id);
});

modalSelect.addEventListener("change", () => {
  let nextTextInput =
    modalSelect.parentElement.nextElementSibling.querySelector(
      "input[type='text']"
    );
  let nextNumberInput =
    modalSelect.parentElement.nextElementSibling.nextElementSibling.querySelector(
      "input[type='number']"
    );
  nextTextInput.value = modalSelect.querySelector(
    `option[value="${modalSelect.value}"]`
  ).innerHTML;
  nextNumberInput.focus();
});

modalCloseBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal.querySelectorAll("input").forEach((input) => {
      input.value = "";
      modalSelect.value = "اختر زبون";
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
      amountInput.value = 0;
    } else {
      amountInput.value = -amount;
    }

    modal.querySelector("input[type='text']").value = userId;

    setTimeout(() => {
      amountInput.focus();
      amountInput.select();
    }, 500);
  });
});
