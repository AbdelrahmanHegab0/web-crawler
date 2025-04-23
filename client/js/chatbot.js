
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");

function appendMessage(message, type = "incoming") {
    const li = document.createElement("li");
    li.className = `message ${type}`;
    li.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(li);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, "outgoing");
    userInput.value = "";

    appendMessage("Typing...", "incoming");

    try {
        const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyA5eW2FyX8FC9Mp8W5h5nEnKt6MtYAHf7A", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                contents: [
                    {
                        parts: [{ text: message }],
                        role: "user"
                    }
                ]
            })
        });

        const data = await response.json();

        // Gemini API بيرجع الرد في `candidates[0].content.parts[0].text`
        if (data.candidates && data.candidates.length > 0) {
            const botReply = data.candidates[0].content.parts[0].text.trim();

            // Remove "Typing..." placeholder
            const loadingMessage = document.querySelector(".message.incoming:last-child");
            if (loadingMessage) loadingMessage.remove();

            appendMessage(botReply, "incoming");
        } else {
            throw new Error("No response from API.");
        }

    } catch (err) {
        console.error(err);
        const errorMsg = document.querySelector(".message.incoming:last-child");
        if (errorMsg) errorMsg.textContent = "⚠️ Error getting response.";
    }
}

const chatbotContainer = document.querySelector(".chatbot-container");
const closeChatbot = () => {
    chatbotContainer.style.display = "none";
}

const openChatbot = ()=>{
    chatbotContainer.style.display = "flex";
}