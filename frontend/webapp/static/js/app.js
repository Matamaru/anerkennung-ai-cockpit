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

  const profileButtons = document.querySelectorAll(".js-use-profile");
  profileButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetName = btn.getAttribute("data-target");
      const value = btn.getAttribute("data-value") || "";
      if (!targetName) return;
      const scope = btn.closest("form") || document;
      const input = scope.querySelector(`input[name="${targetName}"], textarea[name="${targetName}"]`);
      if (input) {
        input.value = value;
        input.focus();
      }
      const profileFieldInput = scope.querySelector('input[name="profile_fields"]');
      if (profileFieldInput) {
        const key = targetName.replace(/^field_/, "");
        const current = (profileFieldInput.value || "").split(",").map((v) => v.trim()).filter(Boolean);
        if (!current.includes(key)) {
          current.push(key);
          profileFieldInput.value = current.join(",");
        }
      }
    });
  });
});
