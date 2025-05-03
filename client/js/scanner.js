document.addEventListener("DOMContentLoaded", () => {
    const scanForm = document.getElementById("scan-form");
    const resultContainer = document.getElementById("scan-result");
    const loadingSpinner = document.getElementById("scanner-loading");

    // دالة فحص الموقع (مسح + فحص أمان)
    async function scanWebsite(domain, selectedScanners) {
        const url = `http://127.0.0.1:8000/scan/`; // السيرفر المحلي
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
            const objectUrl = URL.createObjectURL(blob); // منع تسريب الذاكرة
            link.href = objectUrl;
            link.download = "scan_report.txt"; // تحميل التقرير
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(objectUrl); // تفريغ الرابط المؤقت

            return { success: true };
        } catch (error) {
            console.error("Scan failed:", error);
            return { error: "Failed to scan the website. Please try again." };
        }
    }

    // حدث إرسال النموذج (مسح)
    scanForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const domain = document.getElementById("domain-input").value.trim();

        // دعم اختيار متعدد للأنواع
        const scannerSelect = document.getElementById("scan-types");
        const selectedScanners = Array.from(scannerSelect.selectedOptions).map(opt => opt.value);

        if (!domain) {
            resultContainer.innerHTML = `<p class="text-danger">Please enter a valid domain.</p>`;
            return;
        }

        if (selectedScanners.length === 0) {
            resultContainer.innerHTML = `<p class="text-danger">Please select at least one scan type (XSS, LFI, or Open Redirect).</p>`;
            return;
        }

        loadingSpinner.style.display = "block";
        resultContainer.style.display = "none";

        const result = await scanWebsite(domain, selectedScanners);

        loadingSpinner.style.display = "none";
        resultContainer.style.display = "block";

        resultContainer.innerHTML = result.error
            ? `<p class="text-danger">${result.error}</p>`
            : `<p class="text-success fw-bold">✅ Scan completed successfully. Your report has been downloaded.</p>`;
    });

    // حدث زر "Show Web Tree" (الذي يختص فقط بالكراولينج)
    document.getElementById("show-tree-btn").addEventListener("click", async () => {
        const domain = document.getElementById("domain-input").value.trim();

        if (!domain) {
            alert("Please enter a valid domain.");
            return;
        }

        // إرسال طلب للحصول على التراكيب فقط (Crawling)
        const response = await fetch(`/site-tree/?url=${domain}`);
        const data = await response.json();

        if (data.error) {
            alert("No links found to build the tree.");
            return;
        }

        // عرض الشجرة
        document.getElementById("tree-container").innerHTML = ""; // clear previous

        const width = 800, height = 600;
        const svg = d3.select("#tree-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(40,0)");

        const treeLayout = d3.tree().size([height, width - 160]);
        const root = d3.hierarchy(data, d => d.children);

        treeLayout(root);

        svg.selectAll('line')
            .data(root.links())
            .enter()
            .append('line')
            .attr('x1', d => d.source.y)
            .attr('y1', d => d.source.x)
            .attr('x2', d => d.target.y)
            .attr('y2', d => d.target.x)
            .attr('stroke', '#ccc');

        svg.selectAll('circle')
            .data(root.descendants())
            .enter()
            .append('circle')
            .attr('cx', d => d.y)
            .attr('cy', d => d.x)
            .attr('r', 5)
            .attr('fill', '#df0606');

        svg.selectAll('text')
            .data(root.descendants())
            .enter()
            .append('text')
            .attr('x', d => d.y + 10)
            .attr('y', d => d.x + 5)
            .text(d => d.data.name)
            .attr('fill', '#eee');
    });
});
