// ✅ دالة المسح (تشمل الكراول + الاسكان مع بعض)
async function scanWebsite(domain, selectedScanners) {
    const url = `http://127.0.0.1:8000/scan/`; // رابط الـ backend الذي يعالج الفحص
    const payload = {
        url: domain,
        scanners: selectedScanners.length > 0 ? selectedScanners : []  // إرسال الماسحات المحددة فقط
    };

    try {
        // إرسال البيانات إلى الـ API
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        // إذا كانت الاستجابة غير ناجحة
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // استلام النتيجة كـ Blob (ملف)
        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "scan_report.txt";  // اسم الملف
        link.click();  // تشغيل التحميل
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
        const domain = domainInput.value.trim();
        const selectedScanners = Array.from(document.querySelectorAll('#scanner-options input[type="checkbox"]:checked'))
                              .map(cb => cb.value);

        // التحقق من وجود الدومين
        if (!domain) {
            resultContainer.innerHTML = `<p class="text-danger">Please enter a valid domain.</p>`;
            return;
        }

        // التحقق من وجود خيارات للمسح
        if (selectedScanners.length === 0) {
            resultContainer.innerHTML = `<p class="text-danger">Please select at least one scanner (XSS, LFI, or Open Redirect).</p>`;
            return;
        }

        // عرض رسالة "Processing..." أثناء انتظار النتيجة
        resultContainer.innerHTML = `<p class="text-info">Processing... Please wait.</p>`;

        // إجراء الفحص باستخدام دالة scanWebsite
        const result = await scanWebsite(domain, selectedScanners);

        // عرض النتيجة بناءً على النتيجة
        if (result.error) {
            resultContainer.innerHTML = `<p class="text-danger">${result.error}</p>`;
        } else {
            resultContainer.innerHTML = `<p class="text-info">Your scan report is ready. <a href="#" onclick="scanWebsite('${domain}', ${JSON.stringify(selectedScanners)})">Download the report</a>.</p>`;
        }
    });
});
