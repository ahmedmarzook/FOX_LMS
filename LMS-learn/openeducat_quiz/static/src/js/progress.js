/** @odoo-module **/

function updateProgress() {
    const progressElement = document.querySelector(".progress-value");
    const progressBar = document.querySelector("#progressBar");

    if (!progressElement || !progressBar) {
        return;
    }

    const percent = Math.max(0, Math.min(100, Number.parseFloat(progressElement.textContent) || 0));
    const bar = progressBar.querySelector("div");

    if (!bar) {
        return;
    }

    const width = `${percent}%`;
    bar.animate(
        [{ width: "0%" }, { width }],
        { duration: 1200, fill: "forwards", easing: "ease-out" }
    );
    bar.textContent = `${percent}% `;
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateProgress, { once: true });
} else {
    updateProgress();
}
