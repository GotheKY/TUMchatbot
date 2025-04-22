async function sendMessage() {
    const userInputField = document.getElementById("user-input");
    const userInput = userInputField.value.trim();
    const chatBox = document.getElementById("chat-box");

    if (!userInput) return;

    chatBox.innerHTML += `<div class='user-msg'>You: ${userInput}</div>`;
    userInputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();
    const reply = data.reply;
    chatBox.innerHTML += `<div class='bot-msg'><strong>Bot:</strong> ${reply}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}