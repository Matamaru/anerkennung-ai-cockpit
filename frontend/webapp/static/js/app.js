document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll(".upload-form");
  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector(".upload-btn");
      const spinner = form.querySelector(".spinner-border");
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Uploading...";
      }
      if (spinner) {
        spinner.classList.remove("d-none");
      }
    });
  });
});
