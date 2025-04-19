const dropdownButton = document.getElementById("dropdownButton");
        const dropdownMenu = document.getElementById("dropdownMenu");
        
        dropdownButton.addEventListener("click", () => {
            dropdownMenu.classList.toggle("hidden");
            dropdownMenu.classList.toggle("block");
        });
        document.addEventListener("click", (event) => {
            if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
                dropdownMenu.classList.add("hidden");
                dropdownMenu.classList.remove("block");
            }
        });