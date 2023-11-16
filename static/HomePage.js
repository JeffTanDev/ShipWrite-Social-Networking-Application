document.addEventListener("DOMContentLoaded", function () {
    const modeButton = document.getElementById("mode-button");
    const messageButton = document.querySelector(".message-button");
    const groupButton = document.querySelector(".group-button");

    // Fetch mode from backend on page load
    fetchMode();

    // Event listener for mode toggle
    modeButton.addEventListener("click", toggleAndUploadMode);

    // Function to toggle mode on button click
    function toggleAndUploadMode() {
        toggleMode();

        // Define the new mode based on the current state
        const newMode = document.body.classList.contains("inward-mode") ? 0 : 1;

        // Update mode on backend
        axios.post('/api/updatemode', { mode: newMode })
            .then(response => {
                console.log('Mode updated:', response.data.message);
            })
            .catch(error => {
                console.error('Error updating mode:', error.response.data.error);
            });
    }

    // Function to toggle mode UI
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

    // Function to fetch and set mode from backend
    function fetchMode() {
        axios.get('/api/userinfo')
            .then(response => {
                const mode = response.data.mode;
                if (mode === 0) {
                    document.body.classList.add("inward-mode");
                    messageButton.disabled = true;
                    groupButton.disabled = true;
                } else {
                    document.body.classList.remove("inward-mode");
                    messageButton.disabled = false;
                    groupButton.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error fetching mode:', error.response.data.error);
            });
    }
});
