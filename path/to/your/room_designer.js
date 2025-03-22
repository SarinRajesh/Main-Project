// Fix 1: Ensure canvas gets focus after upload and prevent default arrow key behavior
function handleModelUpload(event) {
    // ... existing upload handling code ...
    
    // After upload completes, focus the canvas to ensure keyboard controls work
    document.getElementById('3d-canvas').focus(); // Replace with your actual canvas ID
    
    // ... existing code ...
}

// Fix 2: Improve your key event handlers to prevent scrolling
document.addEventListener('keydown', function(event) {
    // Only handle keys if a model is selected or we're in navigation mode
    if (currentSelectedModel || navigationActive) {
        // Arrow keys
        if ([37, 38, 39, 40].includes(event.keyCode)) {
            // Prevent default scrolling behavior
            event.preventDefault();
            
            // Handle model movement based on arrow keys
            switch(event.keyCode) {
                case 37: // Left arrow
                    moveSelectedModel('left');
                    break;
                case 38: // Up arrow
                    moveSelectedModel('forward');
                    break;
                case 39: // Right arrow
                    moveSelectedModel('right');
                    break;
                case 40: // Down arrow
                    moveSelectedModel('backward');
                    break;
            }
        }
        
        // Page Up/Down for height
        if (event.keyCode === 33 || event.keyCode === 34) {
            event.preventDefault();
            if (event.keyCode === 33) moveSelectedModel('up');
            else moveSelectedModel('down');
        }
    }
}, {capture: true}); // Use capture to get event before it reaches scrollable elements

// Fix 3: Add a click handler to the canvas to ensure it gets focus
document.getElementById('3d-canvas').addEventListener('click', function(event) {
    // Focus the canvas when clicked
    this.focus();
});

// Fix 4: Add a tabindex attribute to your canvas element in your HTML
// This can be done dynamically if needed
function makeCanvasFocusable() {
    const canvas = document.getElementById('3d-canvas');
    if (canvas && !canvas.hasAttribute('tabindex')) {
        canvas.setAttribute('tabindex', '0');
    }
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', makeCanvasFocusable); 