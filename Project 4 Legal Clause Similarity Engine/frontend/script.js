/**
 * Legal Clause Similarity Engine - Frontend Logic
 * ===============================================
 * 
 * Beginner Explanation:
 * ---------------------
 * This JavaScript file manages user interactions on the web UI:
 * 1. Checks backend health on page load.
 * 2. Counts words and characters live as the user types.
 * 3. Sends POST request to FastAPI backend (`http://127.0.0.1:8000/search`).
 * 4. Formats floating-point similarity scores (e.g. 0.9125 -> 91.25%).
 * 5. Dynamically renders clause search result cards onto the DOM.
 */

// ============================================================
// CONFIGURATION & DOM ELEMENTS
// ============================================================
const API_BASE_URL = "http://127.0.0.1:8000";

const clauseInput = document.getElementById("clauseInput");
const searchForm = document.getElementById("searchForm");
const searchBtn = document.getElementById("searchBtn");
const btnText = document.querySelector(".btn-text");
const btnSpinner = document.getElementById("btnSpinner");
const clearBtn = document.getElementById("clearBtn");
const exampleBtn = document.getElementById("exampleBtn");
const topKSelect = document.getElementById("topKSelect");
const wordCounter = document.getElementById("wordCounter");

const apiStatusBadge = document.getElementById("apiStatusBadge");
const apiStatusText = document.getElementById("apiStatusText");

const errorBanner = document.getElementById("errorBanner");
const errorMessage = document.getElementById("errorMessage");

const nlpInfoBar = document.getElementById("nlpInfoBar");
const tokenChips = document.getElementById("tokenChips");

const loadingContainer = document.getElementById("loadingContainer");
const emptyState = document.getElementById("emptyState");
const resultsList = document.getElementById("resultsList");
const statsBadge = document.getElementById("statsBadge");


// ============================================================
// INITIALIZATION & EVENT LISTENERS
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    checkApiHealth();
    updateWordCounter();

    // Event listeners
    clauseInput.addEventListener("input", updateWordCounter);
    searchForm.addEventListener("submit", searchClauses);
    clearBtn.addEventListener("click", clearForm);
    exampleBtn.addEventListener("click", insertExampleClause);
});


// ============================================================
// 1. HEALTH CHECK FUNCTION
// Checks backend status upon loading the frontend page
// ============================================================
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            apiStatusBadge.classList.add("connected");
            apiStatusBadge.classList.remove("error");
            apiStatusText.textContent = `API Connected (${data.clauses} clauses loaded)`;
        } else {
            setHealthErrorState();
        }
    } catch (err) {
        setHealthErrorState();
    }
}

function setHealthErrorState() {
    apiStatusBadge.classList.remove("connected");
    apiStatusBadge.classList.add("error");
    apiStatusText.textContent = "Backend Offline (Run uvicorn)";
}


// ============================================================
// 2. LIVE WORD & CHARACTER COUNTER
// ============================================================
function updateWordCounter() {
    const text = clauseInput.value.trim();
    const characters = clauseInput.value.length;
    const words = text ? text.split(/\s+/).length : 0;
    
    wordCounter.textContent = `Words: ${words} | Characters: ${characters}`;
}


// ============================================================
// 3. EXAMPLE CLAUSE CLICK HANDLER
// ============================================================
function insertExampleClause() {
    clauseInput.value = "The tenant shall pay the monthly rent before the fifth day of each month.";
    updateWordCounter();
    hideError();
    clauseInput.focus();
}


// ============================================================
// 4. CLEAR FORM & RESULTS HANDLER
// ============================================================
function clearForm() {
    clauseInput.value = "";
    updateWordCounter();
    hideError();
    
    // Hide NLP Token info bar
    nlpInfoBar.style.display = "none";
    tokenChips.innerHTML = "";
    
    // Reset Results area
    resultsList.innerHTML = "";
    statsBadge.style.display = "none";
    loadingContainer.style.display = "none";
    emptyState.style.display = "block";
}


// ============================================================
// 5. MAIN SEARCH FUNCTION
// Sends query to FastAPI POST /search endpoint
// ============================================================
async function searchClauses(event) {
    if (event) event.preventDefault();

    const text = clauseInput.value.trim();
    const topK = parseInt(topKSelect.value, 10) || 5;

    // Validate input
    if (!text) {
        showError("Please enter a legal clause, sentence, or paragraph.");
        return;
    }

    // Prepare UI state for loading
    hideError();
    setLoadingState(true);

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                clause: text,
                top_k: topK
            })
        });

        const data = await response.json();

        // Check if backend returned an error JSON
        if (data.error) {
            showError(data.error);
            showEmptyResults();
        } else if (data.results && data.results.length > 0) {
            displayNlpTokens(data.processed_tokens);
            displayResults(data.results);
        } else {
            showError("No similar legal clauses were found. Try entering a different clause.");
            showEmptyResults();
        }

    } catch (error) {
        console.error("Search request failed:", error);
        showError("Unable to connect to backend server. Please verify FastAPI is running at http://127.0.0.1:8000.");
        showEmptyResults();
    } finally {
        setLoadingState(false);
    }
}


// ============================================================
// 6. UI LOADING STATE CONTROL
// ============================================================
function setLoadingState(isLoading) {
    if (isLoading) {
        searchBtn.disabled = true;
        btnText.textContent = "Searching legal clauses...";
        btnSpinner.style.display = "inline-block";
        
        loadingContainer.style.display = "block";
        emptyState.style.display = "none";
        resultsList.innerHTML = "";
        statsBadge.style.display = "none";
        nlpInfoBar.style.display = "none";
    } else {
        searchBtn.disabled = false;
        btnText.textContent = "Find Similar Clauses";
        btnSpinner.style.display = "none";
        loadingContainer.style.display = "none";
    }
}


// ============================================================
// 7. DISPLAY NLP PREPROCESSED TOKENS
// ============================================================
function displayNlpTokens(tokens) {
    if (!tokens || tokens.length === 0) {
        nlpInfoBar.style.display = "none";
        return;
    }

    tokenChips.innerHTML = "";
    tokens.forEach(tok => {
        const chip = document.createElement("span");
        chip.className = "token-chip";
        chip.textContent = tok;
        tokenChips.appendChild(chip);
    });

    nlpInfoBar.style.display = "block";
}


// ============================================================
// 8. DISPLAY SEARCH RESULTS (CARDS)
// ============================================================
function displayResults(results) {
    resultsList.innerHTML = "";
    emptyState.style.display = "none";

    // Show statistics badge
    statsBadge.textContent = `${results.length} similar clause${results.length > 1 ? 's' : ''} found`;
    statsBadge.style.display = "inline-block";

    results.forEach((item) => {
        // Convert score decimal (e.g. 0.9125) to percentage string (91.25%)
        const scorePercentage = (item.similarity_score * 100).toFixed(2);
        
        // Determine color theme based on score
        let scoreClass = "score-low";
        if (item.similarity_score >= 0.75) {
            scoreClass = "score-high";
        } else if (item.similarity_score >= 0.50) {
            scoreClass = "score-medium";
        }

        // Create Card Element
        const card = document.createElement("div");
        card.className = "result-card";

        card.innerHTML = `
            <div class="card-top">
                <span class="rank-badge">#${item.rank}</span>
                <div class="card-meta">
                    <span class="type-badge">Category: ${escapeHtml(item.clause_type)}</span>
                    <span class="score-badge ${scoreClass}">Similarity: ${scorePercentage}%</span>
                </div>
            </div>
            <div class="clause-text-box">
                "${escapeHtml(item.clause_text)}"
            </div>
        `;

        resultsList.appendChild(card);
    });
}


function showEmptyResults() {
    resultsList.innerHTML = "";
    statsBadge.style.display = "none";
    emptyState.style.display = "block";
}


// ============================================================
// 9. ERROR HANDLING HELPERS
// ============================================================
function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.style.display = "flex";
}

function hideError() {
    errorBanner.style.display = "none";
    errorMessage.textContent = "";
}


// Utility to sanitize HTML text
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
}
