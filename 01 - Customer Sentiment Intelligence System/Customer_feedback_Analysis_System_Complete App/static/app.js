document.addEventListener('DOMContentLoaded', () => {
    // State management
    let activeFilter = 'all';
    let feedbackRecords = [];

    // Elements
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const feedbackForm = document.getElementById('feedbackForm');
    const submitBtn = document.getElementById('submitBtn');
    const reviewText = document.getElementById('reviewText');
    const charCount = document.getElementById('charCount');
    const starRating = document.getElementById('starRating');
    const ratingValue = document.getElementById('ratingValue');

    // Sample buttons
    const loadSampleNeg = document.getElementById('loadSampleNeg');
    const loadSamplePos = document.getElementById('loadSamplePos');
    const loadSampleNeu = document.getElementById('loadSampleNeu');

    // Result card elements
    const resultEmpty = document.getElementById('resultEmpty');
    const resultContent = document.getElementById('resultContent');
    const sentimentBanner = document.getElementById('sentimentBanner');
    const sentimentIcon = document.getElementById('sentimentIcon');
    const sentimentLabel = document.getElementById('sentimentLabel');
    const confidenceBadge = document.getElementById('confidenceBadge');
    const telegramAlertBox = document.getElementById('telegramAlertBox');
    const telegramAlertTitle = document.getElementById('telegramAlertTitle');
    const telegramAlertDesc = document.getElementById('telegramAlertDesc');
    const resCustomerName = document.getElementById('resCustomerName');
    const resCategory = document.getElementById('resCategory');
    const resRating = document.getElementById('resRating');
    const resRawText = document.getElementById('resRawText');
    const resCleanedText = document.getElementById('resCleanedText');

    // Dashboard elements
    const kpiTotal = document.getElementById('kpiTotal');
    const kpiPositive = document.getElementById('kpiPositive');
    const kpiNeutral = document.getElementById('kpiNeutral');
    const kpiNegative = document.getElementById('kpiNegative');
    const kpiAlerts = document.getElementById('kpiAlerts');
    const kpiPosPct = document.getElementById('kpiPosPct');
    const kpiNeuPct = document.getElementById('kpiNeuPct');
    const kpiNegPct = document.getElementById('kpiNegPct');
    const feedbackTableBody = document.getElementById('feedbackTableBody');
    const refreshFeedBtn = document.getElementById('refreshFeedBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const filterButtons = document.querySelectorAll('.filter-btn');

    // Donut chart elements
    const donutChart = document.getElementById('donutChart');
    const donutTotal = document.getElementById('donutTotal');
    const legPos = document.getElementById('legPos');
    const legNeu = document.getElementById('legNeu');
    const legNeg = document.getElementById('legNeg');

    // Telegram settings elements
    const telegramConfigForm = document.getElementById('telegramConfigForm');
    const botTokenInput = document.getElementById('botToken');
    const chatIDInput = document.getElementById('chatID');
    const autoDetectChatBtn = document.getElementById('autoDetectChatBtn');
    const sendTestAlertBtn = document.getElementById('sendTestAlertBtn');

    // Toast
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    // 1. Navigation Tab Switcher
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (target === 'owner-dashboard') {
                loadDashboardData();
            } else if (target === 'telegram-settings') {
                loadTelegramConfig();
            }
        });
    });

    // 2. Star Rating Handler
    const stars = starRating.querySelectorAll('i');
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            ratingValue.value = rating;
            stars.forEach((s, idx) => {
                if (idx < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });

    // 3. Live Character Count
    reviewText.addEventListener('input', () => {
        charCount.textContent = `${reviewText.value.length} characters`;
    });

    // 4. Sample Review Presets
    if (loadSampleNeg) {
        loadSampleNeg.addEventListener('click', () => {
            document.getElementById('customerName').value = "David Miller";
            document.getElementById('category').value = "Electronics";
            reviewText.value = "The product arrived broken and completely stopped working within 2 days! Terrible build quality and dreadful customer support.";
            setStarRating(1);
            charCount.textContent = `${reviewText.value.length} characters`;
        });
    }

    if (loadSamplePos) {
        loadSamplePos.addEventListener('click', () => {
            document.getElementById('customerName').value = "Sophia Martinez";
            document.getElementById('category').value = "Software & Apps";
            reviewText.value = "Outstanding product! Extremely fast delivery, superb performance, and excellent customer service. Highly recommend to everyone!";
            setStarRating(5);
            charCount.textContent = `${reviewText.value.length} characters`;
        });
    }

    if (loadSampleNeu) {
        loadSampleNeu.addEventListener('click', () => {
            document.getElementById('customerName').value = "Jordan Taylor";
            document.getElementById('category').value = "Home & Kitchen";
            reviewText.value = "Package arrived on time. The item quality is average, fits the description but nothing special.";
            setStarRating(3);
            charCount.textContent = `${reviewText.value.length} characters`;
        });
    }

    function setStarRating(rating) {
        ratingValue.value = rating;
        stars.forEach((s, idx) => {
            if (idx < rating) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });
    }

    // 5. Submit Feedback Form
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = reviewText.value.trim();
        if (!text) return;

        setLoading(true);

        const payload = {
            text: text,
            customer_name: document.getElementById('customerName').value || "Anonymous Customer",
            category: document.getElementById('category').value,
            rating: parseInt(ratingValue.value)
        };

        try {
            const res = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Prediction failed");

            renderResultCard(payload, data);
            showToast(`Analysis complete! Sentiment: ${data.sentiment.toUpperCase()}`);

        } catch (err) {
            showToast(`Error: ${err.message}`, true);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner');
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = "Analyzing NLP Model...";
            spinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit & Analyze Sentiment';
            spinner.classList.add('hidden');
        }
    }

    // 6. Render Sentiment Result
    function renderResultCard(input, result) {
        resultEmpty.classList.add('hidden');
        resultContent.classList.remove('hidden');

        const sentiment = result.sentiment.toLowerCase();
        const confidencePct = (result.confidence * 100).toFixed(1);

        // Update banner styling
        sentimentBanner.className = `sentiment-banner ${sentiment}`;
        sentimentLabel.textContent = sentiment.toUpperCase();
        confidenceBadge.textContent = `${confidencePct}% Match`;

        if (sentiment === 'positive') {
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-smile"></i>';
        } else if (sentiment === 'neutral') {
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-meh"></i>';
        } else {
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-frown"></i>';
        }

        // Telegram alert status
        if (sentiment === 'negative') {
            telegramAlertBox.classList.remove('hidden');
            if (result.telegram_alert_sent) {
                telegramAlertTitle.textContent = "Telegram Alert Dispatched!";
                telegramAlertDesc.innerHTML = `Negative feedback alert was sent immediately to the business owner on Telegram via <strong>@Feedback_Analyser_bot</strong>.`;
            } else {
                telegramAlertTitle.textContent = "Telegram Alert Warning";
                telegramAlertDesc.innerHTML = `Model flagged negative review. ${result.alert_error || "Please configure Chat ID in Telegram Settings to receive push alerts."}`;
            }
        } else {
            telegramAlertBox.classList.add('hidden');
        }

        // Metadata
        resCustomerName.textContent = input.customer_name;
        resCategory.textContent = input.category;
        resRating.textContent = "★".repeat(input.rating) + "☆".repeat(5 - input.rating);
        resRawText.textContent = input.text;
        
        // Cleaned text approximation
        resCleanedText.textContent = input.text.toLowerCase().replace(/[^a-z\s]/g, '');
    }

    // 7. Dashboard Data Loader
    async function loadDashboardData() {
        try {
            const statsRes = await fetch('/api/stats');
            const stats = await statsRes.json();

            kpiTotal.textContent = stats.total;
            kpiPositive.innerHTML = `${stats.positive} <small class="pct-badge">${stats.positive_pct}%</small>`;
            kpiNeutral.innerHTML = `${stats.neutral} <small class="pct-badge">${stats.neutral_pct}%</small>`;
            kpiNegative.innerHTML = `${stats.negative} <small class="pct-badge">${stats.negative_pct}%</small>`;
            kpiAlerts.textContent = stats.alerts_sent;

            // Donut chart updates
            donutTotal.textContent = stats.total;
            legPos.textContent = stats.positive;
            legNeu.textContent = stats.neutral;
            legNeg.textContent = stats.negative;

            if (stats.total > 0) {
                const posDeg = (stats.positive / stats.total) * 360;
                const neuDeg = posDeg + (stats.neutral / stats.total) * 360;
                donutChart.style.background = `conic-gradient(var(--positive) 0deg ${posDeg}deg, var(--neutral) ${posDeg}deg ${neuDeg}deg, var(--negative) ${neuDeg}deg 360deg)`;
            }

            // Load feed history
            await loadFeedbackFeed();

        } catch (err) {
            console.error("Error loading dashboard stats:", err);
        }
    }

    async function loadFeedbackFeed() {
        try {
            const url = activeFilter === 'all' ? '/api/history' : `/api/history?sentiment=${activeFilter}`;
            const res = await fetch(url);
            const data = await res.json();

            feedbackRecords = data.records || [];
            renderFeedbackTable(feedbackRecords);
        } catch (err) {
            console.error("Error loading feedback feed:", err);
        }
    }

    function renderFeedbackTable(records) {
        if (!records.length) {
            feedbackTableBody.innerHTML = `<tr><td colspan="8" class="text-center py-4">No feedback records found.</td></tr>`;
            return;
        }

        feedbackTableBody.innerHTML = records.map(rec => {
            const sent = rec.sentiment ? rec.sentiment.toLowerCase() : 'neutral';
            const badgeClass = sent === 'positive' ? 'badge-pos' : (sent === 'negative' ? 'badge-neg' : 'badge-neu');
            const alertBadge = rec.telegram_alert_sent 
                ? `<span class="badge badge-pos"><i class="fa-brands fa-telegram"></i> Alert Sent</span>`
                : (sent === 'negative' ? `<span class="badge badge-neg"><i class="fa-solid fa-triangle-exclamation"></i> Not Sent</span>` : `<span class="badge" style="background:rgba(255,255,255,0.05);color:#94a3b8;">N/A</span>`);

            const starsStr = rec.rating ? "★".repeat(rec.rating) : "-";

            return `
                <tr>
                    <td style="font-size:12px;color:#94a3b8;">${rec.timestamp || 'Just now'}</td>
                    <td><strong>${escapeHtml(rec.customer_name || 'Anonymous')}</strong></td>
                    <td>${escapeHtml(rec.category || 'General')}</td>
                    <td style="color:#fbbf24;">${starsStr}</td>
                    <td style="max-width:280px;" title="${escapeHtml(rec.text)}">${escapeHtml(truncate(rec.text, 65))}</td>
                    <td><span class="badge ${badgeClass}">${sent.toUpperCase()}</span></td>
                    <td>${alertBadge}</td>
                    <td>
                        ${sent === 'negative' ? `
                            <button class="btn btn-secondary btn-sm" onclick="resendAlert('${rec.id}')">
                                <i class="fa-brands fa-telegram"></i> Re-Alert
                            </button>
                        ` : '-'}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Filter Buttons
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.dataset.filter;
            loadFeedbackFeed();
        });
    });

    if (refreshFeedBtn) {
        refreshFeedBtn.addEventListener('click', loadDashboardData);
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', async () => {
            if (confirm("Are you sure you want to clear all feedback history?")) {
                await fetch('/api/history', { method: 'DELETE' });
                showToast("Feedback history cleared!");
                loadDashboardData();
            }
        });
    }

    // Global helper for re-sending alert
    window.resendAlert = async function(recordId) {
        try {
            const res = await fetch(`/api/history/${recordId}/resend-alert`, { method: 'POST' });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Failed to resend alert");
            showToast("Telegram alert re-sent successfully!");
            loadDashboardData();
        } catch (err) {
            showToast(`Error: ${err.message}`, true);
        }
    };

    // 8. Telegram Bot Settings & Auto-Detect
    async function loadTelegramConfig() {
        try {
            const res = await fetch('/api/telegram/config');
            const data = await res.json();
            if (data.token) botTokenInput.value = data.token;
            if (data.chat_id) chatIDInput.value = data.chat_id;
        } catch (err) {
            console.error("Error loading Telegram config:", err);
        }
    }

    if (telegramConfigForm) {
        telegramConfigForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = botTokenInput.value.trim();
            const chat_id = chatIDInput.value.trim();

            try {
                const res = await fetch('/api/telegram/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, chat_id })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Failed to save configuration");
                showToast("Telegram Bot Configuration saved!");
            } catch (err) {
                showToast(`Error: ${err.message}`, true);
            }
        });
    }

    if (autoDetectChatBtn) {
        autoDetectChatBtn.addEventListener('click', async () => {
            autoDetectChatBtn.disabled = true;
            autoDetectChatBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Detecting...';

            try {
                const res = await fetch('/api/telegram/auto-detect', { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Failed to auto-detect chat ID");
                
                chatIDInput.value = data.chat_id;
                showToast(data.message || `Found Chat ID: ${data.chat_id}`);
            } catch (err) {
                showToast(`Error: ${err.message}`, true);
            } finally {
                autoDetectChatBtn.disabled = false;
                autoDetectChatBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Auto-Detect';
            }
        });
    }

    if (sendTestAlertBtn) {
        sendTestAlertBtn.addEventListener('click', async () => {
            sendTestAlertBtn.disabled = true;
            sendTestAlertBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

            try {
                const chatId = chatIDInput.value.trim();
                const res = await fetch('/api/telegram/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chat_id: chatId })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Failed to send test alert");
                showToast("Test notification sent to Telegram!");
            } catch (err) {
                showToast(`Error: ${err.message}`, true);
            } finally {
                sendTestAlertBtn.disabled = false;
                sendTestAlertBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send Test Notification';
            }
        });
    }

    // 9. Batch Mode
    const runBatchBtn = document.getElementById('runBatchBtn');
    const batchTextInput = document.getElementById('batchTextInput');
    const batchResultContainer = document.getElementById('batchResultContainer');

    if (runBatchBtn) {
        runBatchBtn.addEventListener('click', async () => {
            const raw = batchTextInput.value.trim();
            if (!raw) {
                showToast("Please enter or upload reviews first", true);
                return;
            }

            const lines = raw.split('\n').filter(l => l.trim().length > 0);
            const reviews = lines.map(text => ({ text, customer_name: "Batch User", category: "Batch Import" }));

            runBatchBtn.disabled = true;
            runBatchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Batch...';

            try {
                const res = await fetch('/api/batch-predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reviews })
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Batch processing failed");

                const results = data.results || [];
                const total = results.length;
                const pos = results.filter(r => r.sentiment === 'positive').length;
                const neu = results.filter(r => r.sentiment === 'neutral').length;
                const neg = results.filter(r => r.sentiment === 'negative').length;
                const alerts = results.filter(r => r.telegram_alert_sent).length;

                document.getElementById('bTotal').textContent = total;
                document.getElementById('bPos').textContent = pos;
                document.getElementById('bNeu').textContent = neu;
                document.getElementById('bNeg').textContent = neg;
                document.getElementById('bAlerts').textContent = alerts;

                batchResultContainer.classList.remove('hidden');
                showToast(`Batch completed: ${total} reviews classified!`);

            } catch (err) {
                showToast(`Error: ${err.message}`, true);
            } finally {
                runBatchBtn.disabled = false;
                runBatchBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Run Batch Sentiment Classifier';
            }
        });
    }

    // Utilities
    function showToast(msg, isError = false) {
        toastMessage.textContent = msg;
        toast.style.borderColor = isError ? 'var(--negative)' : 'var(--primary)';
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 4000);
    }

    function truncate(str, max = 50) {
        if (!str) return '';
        return str.length > max ? str.substring(0, max) + '...' : str;
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // Initial config load
    loadTelegramConfig();
});
