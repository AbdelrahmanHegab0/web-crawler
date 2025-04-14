// ✅ دالة المسح (تشمل الكراول + الاسكان مع بعض)
async function scanWebsite(domain, selectedScanners) {
    const url = `http://127.0.0.1:8000/scan/`; // رابط الـ backend
    const payload = {
        url: domain,
        scanners: selectedScanners.length > 0 ? selectedScanners : []
    };

    try {
        // إرسال البيانات
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // استلام Blob وتحميله
        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "scan_report.txt";
        link.click();

        return { success: true }; // نرجع نجاحة العملية
    } catch (error) {
        console.error("Scan failed:", error);
        return { error: "Failed to scan the website. Please try again." };
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const scanForm = document.getElementById("scan-form");
    const resultContainer = document.getElementById("scan-result");
    const loadingSpinner = document.getElementById("scanner-loading");

    scanForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const domainInput = document.getElementById("domain-input");
        const domain = domainInput.value.trim();
        const selectedScanner = document.getElementById("scan-types").value;

        // تحقق من الإدخالات
        if (!domain) {
            resultContainer.innerHTML = `<p class="text-danger">Please enter a valid domain.</p>`;
            return;
        }

        if (!selectedScanner) {
            resultContainer.innerHTML = `<p class="text-danger">Please select a scan type (XSS, LFI, or Open Redirect).</p>`;
            return;
        }

        // عرض الـ Animation وإخفاء النتائج
        loadingSpinner.style.display = "block";
        resultContainer.style.display = "none";

        // إجراء الفحص
        const result = await scanWebsite(domain, [selectedScanner]);

        // إخفاء الـ Animation بعد انتهاء الفحص
        loadingSpinner.style.display = "none";
        resultContainer.style.display = "block";

        // عرض النتيجة
        if (result.error) {
            resultContainer.innerHTML = `<p class="text-danger">${result.error}</p>`;
        } else {
            resultContainer.innerHTML = `<p class="text-success fw-bold">✅ Scan completed successfully. Your report has been downloaded.</p>`;
        }
    });
});
