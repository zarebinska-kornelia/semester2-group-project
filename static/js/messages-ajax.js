document.addEventListener('DOMContentLoaded', (event) => {
    const chatWindow = document.getElementById('chat-window');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    let atBottom = true;

    // Function to fetch and display messages
    function fetchMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                const previousScrollHeight = chatWindow.scrollHeight;
                chatWindow.innerHTML = '';
                data.forEach(message => {
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('message-bubble');
                    if (message.sender === currentUser) { // currentUser needs to be passed to JS
                        messageDiv.classList.add('sent-message');
                    }
                    messageDiv.innerHTML = `
                        <p class="sender">${message.sender} <span class="message-time">${message.timestamp}</span></p>
                        <p class="message-content">${message.content}</p>
                    `;
                    chatWindow.appendChild(messageDiv);
                });

                // Check if the user was at the bottom before messages update
                if (atBottom) {
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                } else {
                    chatWindow.scrollTop += chatWindow.scrollHeight - previousScrollHeight;
                }
            });
    }

    // Initial fetch of messages
    fetchMessages();

    // Set interval to refresh messages
    setInterval(fetchMessages, 5000); // Adjust the interval as necessary

    // Handle form submission via AJAX
    sendButton.addEventListener('click', (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        fetch('/chat', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                input.value = ''; // Clear input field
                fetchMessages(); // Refresh messages
                chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom on sending
            }
        });
    });

    // Track user scroll position
    chatWindow.addEventListener('scroll', () => {
        const scrollThreshold = 50; // Adjust as needed for sensitivity
        const isScrolledToBottom = chatWindow.scrollTop + chatWindow.clientHeight >= chatWindow.scrollHeight - scrollThreshold;
        atBottom = isScrolledToBottom;
    });
});
// Get the input field
var input = document.getElementById("chat-input");

// Execute a function when the user presses a key on the keyboard
input.addEventListener("keypress", function(event) {
  // If the user presses the "Enter" key on the keyboard
  if (event.key === "Enter") {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    document.getElementById("send-button").click();
  }
});
