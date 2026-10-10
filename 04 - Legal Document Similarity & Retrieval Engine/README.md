# Legal Clause Similarity Engine ⚖️

An end-to-end Natural Language Processing (NLP) document similarity engine that accepts a legal clause, sentence, or paragraph and retrieves the most semantically similar clauses from a predefined legal dataset using **Word2Vec** vector representations and **Cosine Similarity**.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [NLP Preprocessing Pipeline](#-nlp-preprocessing-pipeline)
- [Word2Vec & Cosine Similarity Approach](#-word2vec--cosine-similarity-approach)
- [Project Structure](#-project-structure)
- [Installation & Requirements](#-installation--requirements)
- [How to Run the Application](#-how-to-run-the-application)
- [API Documentation](#-api-documentation)
- [Example API Request & Response](#-example-api-request--response)
- [Frontend User Interface](#-frontend-user-interface)
- [Key Limitations](#-key-limitations)
- [Beginner Presentation Talking Points](#-beginner-presentation-talking-points)

---

## 📌 Project Overview

Legal contracts and agreements contain thousands of clauses. Finding similar clauses across documents manually or using exact keyword matching (like CTRL+F) fails when different terms are used to express the same legal obligation (e.g., *"tenant"* vs *"lessee"*, or *"shall pay"* vs *"make monthly payments"*).

This project solves this by using **Semantic Search**:
- Words are converted into continuous vector spaces where words with similar meanings reside close to each other.
- Average word vectors represent the semantic meaning of an entire legal clause.
- Cosine similarity ranks dataset clauses from highest to lowest mathematical match.

---

## 🎯 Problem Statement

Design and implement a **Document Similarity Engine** that:
1. Preprocesses raw legal clause queries (tokenization, stopword removal, lemmatization).
2. Converts input text into a **100-dimensional Word2Vec feature vector**.
3. Computes **Cosine Similarity** against precomputed clause vectors (`clause_vectors.npy`).
4. Serves results via a high-performance **FastAPI** backend.
5. Displays results in an interactive, responsive **Vanilla HTML/CSS/JavaScript** frontend.

---

## 🧠 NLP Preprocessing Pipeline

When a user submits a legal clause, it undergoes the exact NLP pipeline used during model training:

```text
User Input Clause: "The tenant shall pay monthly rent before the 5th day."
       │
       ▼
1. Lowercase: "the tenant shall pay monthly rent before the 5th day."
       │
       ▼
2. Remove Punctuation & Numbers: "the tenant shall pay monthly rent before the  th day "
       │
       ▼
3. Tokenization: ["the", "tenant", "shall", "pay", "monthly", "rent", "before", "the", "th", "day"]
       │
       ▼
4. Stopword Removal (Preserving Legal Terms): ["tenant", "shall", "pay", "monthly", "rent", "day"]
   * Preserved terms: shall, must, may, not, no, without, unless, except, required
       │
       ▼
5. Lemmatization: ["tenant", "shall", "pay", "monthly", "rent", "day"]
```

---

## 📐 Word2Vec & Cosine Similarity Approach

### 1. Word2Vec Model Training Parameters
The Word2Vec model was trained using Gensim on legal domain corpora:
- `vector_size = 100`: Each word is represented by 100 floating-point numbers.
- `window = 5`: Context window size of 5 surrounding words.
- `min_count = 2`: Ignores rare words occurring fewer than 2 times.
- `sg = 1`: Skip-Gram architecture (predicts context words given a target word).
- `epochs = 20`: 20 training iterations over the corpus.

### 2. Clause Vector Generation
To represent an entire clause as a single vector:
$$\mathbf{v}_{\text{clause}} = \frac{1}{N} \sum_{i=1}^{N} \mathbf{v}_{\text{word}_i}$$
where $N$ is the number of tokens in the clause present in the Word2Vec vocabulary.

### 3. Cosine Similarity Formula
Cosine similarity measures the cosine of the angle between two vectors:
$$\text{Similarity}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

Scores range from `-1.0` (opposite meaning) to `1.0` (identical direction).

---

## 📁 Project Structure

```text
Legal Clause Similarity Engine/
│
├── data/
│   ├── raw/
│   │   └── legal_docs.csv              # Original dataset
│   └── processed/
│       └── processed_clauses.csv        # Cleaned dataset (clause_text, clause_type, tokens)
│
├── models/
│   ├── legal_word2vec.model           # Trained Gensim Word2Vec model
│   └── clause_vectors.npy             # Precomputed numpy vector matrix (N x 100)
│
├── src/
│   ├── preprocessing.py               # Tokenization and NLTK cleaning pipeline
│   ├── train_word2vec.py              # Script to train Word2Vec model
│   ├── model_testing.py               # Script to test Word2Vec vocabulary & similarity
│   └── similarity.py                  # Script to precompute clause_vectors.npy
│
├── backend/
│   ├── __init__.py                    # Python package marker
│   └── app.py                         # FastAPI backend implementation
│
├── frontend/
│   ├── index.html                     # HTML5 web page
│   ├── style.css                      # Modern legal-tech Vanilla CSS stylesheet
│   └── script.js                      # Vanilla JavaScript frontend logic
│
├── tests/
│   └── test_backend.py                # FastAPI PyTest test suite
│
├── requirements.txt                   # Python package dependencies
└── README.md                          # Project documentation
```

---

## ⚙️ Installation & Requirements

### Prerequisites
- Python 3.9+ installed on your system.

### Install Dependencies
Clone or open the project folder, then run:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

### 1. Start the Backend API (FastAPI)
Run from the root directory of the project:

```bash
uvicorn backend.app:app --reload
```

- Backend server: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Start the Frontend Web UI
Open a new terminal window, navigate to the `frontend/` directory, and start a simple HTTP server:

```bash
cd frontend
python -m http.server 5500
```

Open your browser and navigate to:
[http://127.0.0.1:5500](http://127.0.0.1:5500)

---

## 📡 API Documentation

### 1. GET `/`
- **Description**: Basic root endpoint confirming server status.
- **Response**:
```json
{
    "message": "Legal Clause Similarity Engine API is running."
}
```

---

### 2. GET `/health`
- **Description**: Health check endpoint returning dynamic clause count and vector dimension.
- **Response**:
```json
{
    "status": "healthy",
    "clauses": 21075,
    "vector_size": 100
}
```

---

### 3. POST `/search`
- **Description**: Main semantic search endpoint. Accepts user clause and returns top matching legal clauses.
- **Request Body**:
```json
{
    "clause": "The tenant shall pay monthly rent before the fifth day of each month.",
    "top_k": 5
}
```

- **Response Body**:
```json
{
    "query": "The tenant shall pay monthly rent before the fifth day of each month.",
    "processed_tokens": [
        "tenant",
        "shall",
        "pay",
        "monthly",
        "rent",
        "fifth",
        "day",
        "month"
    ],
    "results": [
        {
            "rank": 1,
            "clause_text": "The tenant shall pay the monthly rent...",
            "clause_type": "Payment",
            "similarity_score": 0.9125
        },
        {
            "rank": 2,
            "clause_text": "The lessee must make monthly rental payments...",
            "clause_type": "Rent",
            "similarity_score": 0.8742
        }
    ]
}
```

---

## 🖥️ Frontend User Interface

The frontend is built using standard **HTML5**, **CSS3**, and **Vanilla JavaScript**:
- **Live Word & Character Counter**: Updates in real time as text is typed.
- **Clickable Example Chips**: Allows quick 1-click testing of pre-set legal queries.
- **Formatted Score Badges**: Converts raw decimals (e.g. `0.9125`) to percentage display (`91.25%`).
- **NLP Token Chips**: Shows the user how NLTK cleaned their query string.
- **Responsive Layout**: Adjusts seamlessly across desktop, laptop, tablet, and mobile views.

---

## 🧪 Running Automated Tests

To run the automated API test suite:

```bash
pytest tests/test_backend.py
```

---

## ⚠️ Key Limitations

1. **Vocabulary Out-of-Bounds**: If an input clause contains only unknown jargon absent from the Word2Vec vocabulary, vector averaging produces a zero vector.
2. **Word Order Sensitivity**: Average Word2Vec bag-of-words representation does not retain word order (unlike Transformer models like BERT).
3. **Fixed Dataset Size**: The engine searches pre-computed static clause vectors stored in `clause_vectors.npy`.

---

## 🎓 Beginner Presentation Talking Points

If presenting this project for a college or technical evaluation:
1. **Why Word2Vec over TF-IDF/Keyword Matching?**
   - TF-IDF relies on exact term overlap. Word2Vec captures semantic relationships (e.g. knowing "tenant" is related to "lessee").
2. **Why Precompute Vectors (`clause_vectors.npy`)?**
   - Precomputing vectors for 21,000+ clauses once cuts search latency from seconds to under 10 milliseconds.
3. **Why preserve specific legal stopwords (`shall`, `must`, `may`)?**
   - In legal contracts, modal verbs carry binding obligations ("shall" vs "may"). Removing them alters legal meaning.
