// ✅ دالة المسح (تشمل الكراول + الاسكان مع بعض)
async function scanWebsite(domain, selectedScanners) {
    const url = `http://127.0.0.1:8000/scan/`; // عنوان السيرفر المحلي
    const payload = {
        url: domain,
        scanners: selectedScanners
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "scan_report.txt"; // تحميل التقرير
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        return { success: true };
    } catch (error) {
        console.error("Scan failed:", error);
        return { error: "Failed to scan the website. Please try again." };
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const scanForm = document.getElementById("scan-form");
    const resultContainer = document.getElementById("scan-result");
    const loadingSpinner = document.getElementById("scanner-loading");

    scanForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const domain = document.getElementById("domain-input").value.trim();
        const selectedScanner = document.getElementById("scan-types").value;

        if (!domain) {
            resultContainer.innerHTML = `<p class="text-danger">Please enter a valid domain.</p>`;
            return;
        }

        if (!selectedScanner) {
            resultContainer.innerHTML = `<p class="text-danger">Please select a scan type (XSS, LFI, or Open Redirect).</p>`;
            return;
        }

        loadingSpinner.style.display = "block";
        resultContainer.style.display = "none";

        const result = await scanWebsite(domain, [selectedScanner]);

        loadingSpinner.style.display = "none";
        resultContainer.style.display = "block";

        resultContainer.innerHTML = result.error
            ? `<p class="text-danger">${result.error}</p>`
            : `<p class="text-success fw-bold">✅ Scan completed successfully. Your report has been downloaded.</p>`;
    });
});

// ✅ شات بوت (للتفاعل مع الـ OpenAI API)
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
        const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyA5eW2FyX8FC9Mp8W5h5nEnKt6MtYAHf7A", {
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

