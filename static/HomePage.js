document.addEventListener("DOMContentLoaded", function () {
    const modeButton = document.getElementById("mode-button");
    const messageButton = document.querySelector(".message-button");
    const groupButton = document.querySelector(".group-button");

    modeButton.addEventListener("click", toggleMode);

    function toggleMode() {
        const body = document.body;
        if (body.classList.contains("inward-mode")) {
            // Switch to outward mode
            body.classList.remove("inward-mode");
            messageButton.disabled = false;
            groupButton.disabled = false;
        } else {
            // Switch to inward mode
            body.classList.add("inward-mode");
            messageButton.disabled = true;
            groupButton.disabled = true;
        }
    }
});
