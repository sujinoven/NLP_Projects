const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const modelSelect = document.getElementById("model");
const topKInput = document.getElementById("top-k");
const compareCheckbox = document.getElementById("compare");
const searchButton = document.getElementById("search-button");
const statusBox = document.getElementById("status");
const resultsRoot = document.getElementById("results");

document.querySelectorAll(".example-query").forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.query;
    queryInput.focus();
  });
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setStatus(message = "", isError = false) {
  statusBox.textContent = message;

  if (!message) {
    statusBox.classList.add("hidden");
    statusBox.classList.remove("error");
    return;
  }

  statusBox.classList.remove("hidden");
  statusBox.classList.toggle("error", isError);
}

function resultCard(item) {
  const content = item.content.length > 320
    ? item.content.slice(0, 320) + "..."
    : item.content;

  return `
    <article class="result-card card">
      <div class="rank-badge">${item.rank}</div>

      <div class="result-meta">
        <span class="pill">${escapeHtml(item.document_id)}</span>
        <span class="pill">${escapeHtml(item.category)}</span>
        <span class="score">Similarity ${Number(item.similarity_score).toFixed(4)}</span>
      </div>

      <h3 class="result-title">${escapeHtml(item.title)}</h3>
      <p class="result-content">${escapeHtml(content)}</p>
    </article>
  `;
}

function renderModelSection(label, payload) {
  const items = payload.results || [];

  return `
    <section class="model-section">
      <div class="model-header">
        <h2 class="model-title">${escapeHtml(label)}</h2>
        <span class="pill">${items.length} result${items.length === 1 ? "" : "s"}</span>
      </div>
      ${items.length
        ? items.map(resultCard).join("")
        : `<div class="status">${escapeHtml(payload.message || "No results found.")}</div>`
      }
    </section>
  `;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  const topK = Number(topKInput.value);

  if (!query) {
    setStatus("Please enter a search query.", true);
    return;
  }

  searchButton.disabled = true;
  searchButton.textContent = "Searching...";
  setStatus("Running similarity search...");
  resultsRoot.innerHTML = "";

  try {
    const compare = compareCheckbox.checked;

    const endpoint = compare ? "/api/compare" : "/api/search";
    const payload = compare
      ? { query, top_k: topK }
      : { query, model: modelSelect.value, top_k: topK };

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Search failed.");
    }

    setStatus("");

    if (compare) {
      resultsRoot.innerHTML = [
        renderModelSection("TF-IDF", data.tfidf),
        renderModelSection("Word2Vec", data.word2vec),
        renderModelSection("FastText", data.fasttext),
      ].join("");
    } else {
      const labels = {
        tfidf: "TF-IDF",
        word2vec: "Word2Vec",
        fasttext: "FastText",
      };

      resultsRoot.innerHTML = renderModelSection(
        labels[data.model] || data.model,
        data
      );
    }
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    searchButton.disabled = false;
    searchButton.textContent = "Search";
  }
});
