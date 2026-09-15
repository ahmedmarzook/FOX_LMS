/** @odoo-module **/

document.addEventListener("click", (event) => {
    const button = event.target.closest(".delete_content");
    if (!button) {
        return;
    }

    event.preventDefault();
    const jobId = button.dataset.job_id;
    if (!jobId || !window.confirm("Are you sure you want to delete this record?")) {
        return;
    }

    const form = document.createElement("form");
    form.method = "post";
    form.action = `/alumni/job/delete/${jobId}`;

    const csrf = document.querySelector('input[name="csrf_token"]')?.value;
    if (csrf) {
        const csrfInput = document.createElement("input");
        csrfInput.type = "hidden";
        csrfInput.name = "csrf_token";
        csrfInput.value = csrf;
        form.appendChild(csrfInput);
    }

    document.body.appendChild(form);
    form.submit();
});
