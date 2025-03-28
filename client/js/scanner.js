async function scanWebsite(type, domain) {
    const url = `http://127.0.0.1:8000/scan/${type}`;  
    const payload = { target_url: domain };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Scan failed:", error);
        return { error: "Failed to scan the website. Please try again." };
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const scanForm = document.getElementById("scan-form");
    const resultContainer = document.getElementById("scan-result");

    scanForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const domainInput = document.getElementById("domain-input");
        const scanType = document.getElementById("scan-type");

        const domain = domainInput.value.trim();
        const type = scanType.value;

        if (!domain) {
            resultContainer.innerHTML = `<p class="text-danger">Please enter a valid domain.</p>`;
            return;
        }

        resultContainer.innerHTML = `<p class="text-info">Scanning... Please wait.</p>`;

        const result = await scanWebsite(type, domain);

        if (result.error) {
            resultContainer.innerHTML = `<p class="text-danger">${result.error}</p>`;
        } else {
            resultContainer.innerHTML = `<pre class="text-light bg-dark p-3">${JSON.stringify(result, null, 2)}</pre>`;
        }
    });
});
