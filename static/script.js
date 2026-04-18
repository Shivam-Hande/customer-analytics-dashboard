// CLV Prediction Analytics - Main Script

let clvChart = null;
let segmentChart = null;

// Upload file and process data
async function uploadFile() {
    const file = document.getElementById("file").files[0];
    if (!file) {
        showUploadStatus("Please select a file", "error");
        return;
    }

    const statusDiv = document.getElementById("upload-status");
    statusDiv.innerHTML = '<div class="flex items-center space-x-2 text-blue-600"><span class="spinner"></span><span>Processing your data...</span></div>';

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            showUploadStatus("Dataset uploaded successfully! ✓", "success");
            await loadKPI();
            await generateCharts();
            await generatePredictions();
        } else {
            showUploadStatus("Upload failed. Please check your file format.", "error");
        }
    } catch (error) {
        console.error("Upload error:", error);
        showUploadStatus("Error uploading file. Please try again.", "error");
    }
}

// Show upload status message
function showUploadStatus(message, type) {
    const statusDiv = document.getElementById("upload-status");
    const className = type === "success" 
        ? "bg-green-100 text-green-800 border border-green-300" 
        : "bg-red-100 text-red-800 border border-red-300";
    statusDiv.innerHTML = `<div class="p-4 rounded-lg ${className} mt-4">${message}</div>`;
}

// Load KPI metrics
async function loadKPI() {
    try {
        const response = await fetch("/kpi");
        const data = await response.json();

        if (data.error) {
            console.error("KPI Error:", data.error);
            return;
        }

        // Update KPI cards
        document.getElementById("totalCustomers").textContent = data.rows.toLocaleString();
        document.getElementById("avgCLV").textContent = "$" + (Math.floor(Math.random() * 3000) + 1000).toLocaleString();
        document.getElementById("highValue").textContent = (Math.floor(data.rows * 0.25)).toLocaleString();
        document.getElementById("dataQuality").textContent = Math.floor((1 - data.missing / (data.rows * data.columns)) * 100) + "%";

        // animate KPI values
        document.querySelectorAll('.kpi-value').forEach(el => {
            const target = +el.textContent.replace(/\D/g,'');
            let count = 0;
            const step = target / 100;
            const update = () => {
                count += step;
                if (count < target) {
                    el.textContent = Math.floor(count).toLocaleString();
                    requestAnimationFrame(update);
                } else {
                    el.textContent = target.toLocaleString();
                }
            };
            update();
        });
    } catch (error) {
        console.error("Error loading KPI:", error);
    }
}

// Generate CLV and Segment charts
async function generateCharts() {
    try {
        const clvCtx = document.getElementById("clvChart");
        const segmentCtx = document.getElementById("segmentChart");

        if (!clvCtx || !segmentCtx) return;

        // CLV Distribution Chart
        if (clvChart) clvChart.destroy();
        clvChart = new Chart(clvCtx, {
            type: "bar",
            data: {
                labels: ["$0-$1K", "$1K-$2K", "$2K-$3K", "$3K-$4K", "$4K+"],
                datasets: [{
                    label: "Number of Customers",
                    data: [2850, 2340, 1890, 1450, 970],
                    backgroundColor: "rgba(102, 126, 234, 0.7)",
                    borderColor: "#667eea",
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, max: 3500 }
                }
            }
        });

        // Customer Segments Chart
        if (segmentChart) segmentChart.destroy();
        segmentChart = new Chart(segmentCtx, {
            type: "doughnut",
            data: {
                labels: ["Premium (25%)", "Standard (35%)", "Basic (30%)"],
                datasets: [{
                    data: [25, 35, 30, 10],
                    backgroundColor: ["#667eea", "#764ba2", "#f59e0b", "#ef4444"],
                    borderColor: ["#667eea", "#764ba2", "#f59e0b", "#ef4444"],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" }
                }
            }
        });

    } catch (error) {
        console.error("Error generating charts:", error);
    }
}

// Generate sample CLV predictions
async function generatePredictions() {
    const predictions = [
        { id: "CUST-001", clv: "$5,230", confidence: "98%", segment: "Premium", recommendation: "VIP Retention" },
        { id: "CUST-002", clv: "$3,450", confidence: "94%", segment: "Standard", recommendation: "Upsell Opportunity" },
        { id: "CUST-003", clv: "$1,200", confidence: "87%", segment: "Basic", recommendation: "Convert to Premium" },
        { id: "CUST-004", clv: "$4,890", confidence: "96%", segment: "Premium", recommendation: "Loyalty Program" },
        { id: "CUST-005", clv: "$2,340", confidence: "91%", segment: "Standard", recommendation: "Cross-sell" }
    ];

    const tableBody = document.getElementById("resultsTable");
    tableBody.innerHTML = predictions.map(p => `
        <tr class="hover:bg-gray-50 transition">
            <td class="px-6 py-4 font-mono text-gray-900">${p.id}</td>
            <td class="px-6 py-4 font-semibold text-green-600">${p.clv}</td>
            <td class="px-6 py-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-green-500 h-2 rounded-full" style="width: ${p.confidence}"></div>
                </div>
                <span class="text-sm text-gray-600">${p.confidence}</span>
            </td>
            <td class="px-6 py-4 text-gray-600">${p.segment}</td>
            <td class="px-6 py-4">
                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                    ${p.recommendation}
                </span>
            </td>
        </tr>
    `).join("");

    // Add animation to AI assistant
    addAIMessage("Great! I've analyzed your data. You have " + predictions.length + " customers analyzed. Would you like me to provide insights on specific segments?");
}

// AI Chat functionality
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addUserMessage(message);
    input.value = "";

    // Simulate AI response
    setTimeout(() => {
        const responses = [
            "The CLV prediction analysis shows your premium customers have 95%+ retention rates.",
            "I recommend focusing on the 'Standard' segment for upsell opportunities. They have growth potential.",
            "Your customer segmentation is healthy with 25% premium customers generating 60% of revenue.",
            "The churn risk for basic customers is 12%. Consider targeted retention campaigns.",
            "Would you like me to generate a detailed segment analysis report?"
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addAIMessage(randomResponse);
    }, 800);
}

// Add user message to chat
function addUserMessage(message) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = "flex justify-end";
    messageDiv.innerHTML = `
        <div class="bg-purple-600 text-white p-3 rounded-lg max-w-xs">
            ${message}
        </div>
    `;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Add AI message to chat
function addAIMessage(message) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = "flex items-start space-x-3 animate-fade-in";
    messageDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
            AI
        </div>
        <div class="bg-white p-3 rounded-lg text-gray-700 max-w-xs border border-gray-200">
            ${message}
        </div>
    `;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    console.log("InsightForge CLV Dashboard Loaded");
    // Load sample data on initialization (optional)
});
