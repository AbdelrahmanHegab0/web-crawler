// ✅ دالة المسح XSS
async function scanWebsite(type, domain) {
    const url = `http://127.0.0.1:8000/scan/${type}`;
    const payload = { url: domain };

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

// ✅ دالة جديدة لاستدعاء الـ Crawler
async function crawlWebsite(domain) {
    const url = `http://127.0.0.1:8000/crawl?url=${encodeURIComponent(domain)}`;

    console.log("[*] Sending crawl request to:", url); // ✅ Debugging

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log("[+] Crawl Results:", result); // ✅ تأكد إن الرد وصل
        return result;
    } catch (error) {
        console.error("Crawling failed:", error);
        return { error: "Failed to crawl the website. Please try again." };
    }
}

// ✅ استدعاء الفحص أو الزحف بناءً على الاختيار
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

        resultContainer.innerHTML = `<p class="text-info">Processing... Please wait.</p>`;

        let result;
        if (type === "crawl") {
            result = await crawlWebsite(domain);
        } else {
            result = await scanWebsite(type, domain);
        }

        if (result.error) {
            resultContainer.innerHTML = `<p class="text-danger">${result.error}</p>`;
        } else {
            resultContainer.innerHTML = `<pre class="text-light bg-dark p-3">${JSON.stringify(result, null, 2)}</pre>`;
        }
    });
});
