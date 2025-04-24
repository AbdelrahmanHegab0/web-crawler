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
