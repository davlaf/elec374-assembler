async function loadProgram(filename) {
    const textArea = document.getElementById('assemblyCode');
    
    try {
        // Fetch the file from the static folder
        const response = await fetch(`/static/${filename}`);
        
        if (!response.ok) {
            throw new Error(`Could not find ${filename}`);
        }

        // Get the raw text from the file
        const code = await response.text();
        
        // Update the UI
        textArea.value = code;
        
    } catch (error) {
        console.error("Error loading program:", error);
        textArea.value = "; Error: Could not load the file from the server.";
    }
}

