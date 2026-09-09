async function sendMessage() {

    const input = document.getElementById("messageInput");

    if (!input) return;

    const message = input.value.trim();

    if (!message) return;

    addUserMessage(message);

    input.value = "";

    addTypingMessage();

    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        const data = await response.json();

        removeTypingMessage();

        addAIMessage(data.response);

    } catch (error) {

        removeTypingMessage();

        addAIMessage(
            "I'm sorry, something went wrong. Please try again."
        );
    }
}


function sendQuickRequest(message) {

    const input = document.getElementById("messageInput");

    if (!input) return;

    input.value = message;

    sendMessage();
}


function handleEnter(event) {

    if (event.key === "Enter") {
        sendMessage();
    }
}


function addUserMessage(message) {

    const container =
        document.getElementById("chatMessages");

    if (!container) return;

    const div = document.createElement("div");

    div.className = "message user-message";

    div.innerHTML = `
        <div class="message-avatar">👤</div>
        <div>
            <strong>You</strong>
            <p>${escapeHtml(message)}</p>
        </div>
    `;

    container.appendChild(div);

    container.scrollTop = container.scrollHeight;
}


function addAIMessage(message) {

    const container =
        document.getElementById("chatMessages");

    if (!container) return;

    const div = document.createElement("div");

    div.className = "message ai-message";

    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div>
            <strong>HotelAI</strong>
            <p>${message}</p>
        </div>
    `;

    container.appendChild(div);

    container.scrollTop = container.scrollHeight;
}


function addTypingMessage() {

    const container =
        document.getElementById("chatMessages");

    if (!container) return;

    const div = document.createElement("div");

    div.id = "typingMessage";

    div.className = "message ai-message";

    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div>
            <strong>HotelAI</strong>
            <p>Thinking...</p>
        </div>
    `;

    container.appendChild(div);

    container.scrollTop = container.scrollHeight;
}


function removeTypingMessage() {

    const typing =
        document.getElementById("typingMessage");

    if (typing) {
        typing.remove();
    }
}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}