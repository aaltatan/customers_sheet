const confirmBtns = document.querySelectorAll(".confirm");

if (confirmBtns.length) {
  confirmBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      let href = btn.getAttribute("href");
      e.preventDefault();
      let result = confirm("Are You Sure Want to delete every Closed Account?");
      if (result) {
        location.assign(href);
      }
    });
  });
}
