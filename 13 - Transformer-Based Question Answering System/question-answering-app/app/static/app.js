document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const healthBadge = document.getElementById("healthBadge");
    const healthStatusText = document.getElementById("healthStatusText");

    const qaForm = document.getElementById("qaForm");
    const contextInput = document.getElementById("contextInput");
    const questionInput = document.getElementById("questionInput");
    const exampleSelect = document.getElementById("exampleSelect");

    const contextCharCount = document.getElementById("contextCharCount");
    const questionCharCount = document.getElementById("questionCharCount");

    const submitBtn = document.getElementById("submitBtn");
    const btnSpinner = document.getElementById("btnSpinner");
    const clearBtn = document.getElementById("clearBtn");

    const resultBadge = document.getElementById("resultBadge");
    const errorBanner = document.getElementById("errorBanner");
    const emptyState = document.getElementById("emptyState");
    const resultsContainer = document.getElementById("resultsContainer");

    const answerText = document.getElementById("answerText");
    const startCharValue = document.getElementById("startCharValue");
    const endCharValue = document.getElementById("endCharValue");
    const scoreValue = document.getElementById("scoreValue");
    const highlightedContext = document.getElementById("highlightedContext");

    // Sample Example Passages and Questions
    const EXAMPLES = {
        distilbert: {
            context: "DistilBERT is a small, fast, cheap and light Transformer model trained by distilling BERT base. It has 40% less parameters than bert-base-uncased, runs 60% faster while preserving over 95% of BERT's performances as measured on the GLUE language understanding benchmark. DistilBERT was created by Victor Sanh, Lysandre Debut, Julien Chaumond, and Thomas Wolf at Hugging Face.",
            question: "Who created DistilBERT?"
        },
        apollo: {
            context: "Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and Lunar Module Pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969, at 20:17 UTC. Armstrong became the first person to step onto the lunar surface six hours and 39 minutes later on July 21 at 02:56 UTC; Aldrin joined him 19 minutes later.",
            question: "When did Neil Armstrong step onto the Moon?"
        },
        photosynthesis: {
            context: "Photosynthesis is a biological process used by plants, algae, and certain bacteria to convert light energy into chemical energy. This chemical energy is stored in carbohydrate molecules, such as sugars, which are synthesized from carbon dioxide and water. Oxygen is released as a byproduct of this process.",
            question: "What byproduct is released during photosynthesis?"
        }
    };

    // 1. Initial Health Check
    checkHealth();

    async function checkHealth() {
        try {
            const response = await fetch("/api/health");
            if (!response.ok) throw new Error("Health check failed");
            const data = await response.json();

            if (data.model_loaded) {
                healthBadge.className = "status-badge ready";
                healthStatusText.textContent = "DistilBERT Ready";
            } else {
                healthBadge.className = "status-badge error";
                healthStatusText.textContent = "Model Missing";
                showError("Model files not found. Extract 'distilbert_squad_model.zip' into the model/ directory.");
            }
        } catch (err) {
            healthBadge.className = "status-badge error";
            healthStatusText.textContent = "Backend Offline";
        }
    }

    // 2. Character Counters
    function updateCharCounts() {
        const cLen = contextInput.value.length;
        const qLen = questionInput.value.length;

        contextCharCount.textContent = `${cLen.toLocaleString()} / 10,000`;
        questionCharCount.textContent = `${qLen.toLocaleString()} / 500`;
    }

    contextInput.addEventListener("input", updateCharCounts);
    questionInput.addEventListener("input", updateCharCounts);

    // 3. Example Selector
    exampleSelect.addEventListener("change", (e) => {
        const key = e.target.value;
        if (EXAMPLES[key]) {
            contextInput.value = EXAMPLES[key].context;
            questionInput.value = EXAMPLES[key].question;
            updateCharCounts();
            hideError();
        }
    });

    // 4. Clear Button
    clearBtn.addEventListener("click", () => {
        contextInput.value = "";
        questionInput.value = "";
        exampleSelect.selectedIndex = 0;
        updateCharCounts();
        hideError();
        resetResults();
    });

    function resetResults() {
        emptyState.hidden = false;
        resultsContainer.hidden = true;
        resultBadge.className = "badge badge-muted";
        resultBadge.textContent = "Awaiting Input";
    }

    // 5. HTML Escape Helper to prevent XSS
    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 6. Highlight Answer Span safely inside Context Text
    function renderHighlightedContext(fullContext, startChar, endChar) {
        if (startChar < 0 || endChar <= startChar || endChar > fullContext.length) {
            highlightedContext.textContent = fullContext;
            return;
        }

        const before = fullContext.slice(0, startChar);
        const match = fullContext.slice(startChar, endChar);
        const after = fullContext.slice(endChar);

        highlightedContext.innerHTML = `${escapeHtml(before)}<mark class="qa-highlight">${escapeHtml(match)}</mark>${escapeHtml(after)}`;
    }

    // 7. Error Banner Helpers
    function showError(message) {
        errorBanner.textContent = message;
        errorBanner.hidden = false;
    }

    function hideError() {
        errorBanner.hidden = true;
        errorBanner.textContent = "";
    }

    // 8. Form Submission
    qaForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError();

        const context = contextInput.value.trim();
        const question = questionInput.value.trim();

        if (!context || !question) {
            showError("Both Context Passage and Question are required fields.");
            return;
        }

        // Set Loading State
        submitBtn.disabled = true;
        btnSpinner.hidden = false;
        resultBadge.className = "badge badge-muted";
        resultBadge.textContent = "Extracting Answer...";

        try {
            const response = await fetch("/api/answer", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ context, question })
            });

            const data = await response.json();

            if (!response.ok) {
                const detailMsg = data.detail || "Failed to process question answering request.";
                throw new Error(detailMsg);
            }

            // Display Results
            answerText.textContent = data.answer;
            startCharValue.textContent = data.start_char;
            endCharValue.textContent = data.end_char;
            scoreValue.textContent = typeof data.score === 'number' ? data.score.toFixed(2) : data.score;

            renderHighlightedContext(context, data.start_char, data.end_char);

            emptyState.hidden = true;
            resultsContainer.hidden = false;
            resultBadge.className = "badge badge-success";
            resultBadge.textContent = "Answer Found";

        } catch (err) {
            showError(err.message || "An unexpected error occurred.");
            resetResults();
        } finally {
            submitBtn.disabled = false;
            btnSpinner.hidden = true;
        }
    });
});
