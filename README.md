# NLP Projects — Applied NLP Portfolio

A collection of Natural Language Processing projects covering text classification, semantic similarity, recommendations, text generation, translation, summarization, named entity recognition, and question answering.

This repository documents my hands-on learning through notebooks, modular Python code, and application prototypes—from Bag of Words and TF-IDF to recurrent neural networks and Transformers.

## Project Guide

Explore 12 projects spanning classical NLP, recurrent neural networks, and Transformer applications. Each project name below links to its current repository directory.

| Project                                 | Focus                                                 | Methods and models                                                            |
| --------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| [**01. Customer Sentiment Intelligence System**](./01%20-%20Customer%20Sentiment%20Intelligence%20System/)       | Sentiment analysis of customer reviews                | Bag of Words, TF-IDF, Word2Vec; application uses a saved classifier and VADER |
| [**02. Intelligent Email Spam Detection System**](./02%20-%20Intelligent%20Email%20Spam%20Detection%20System/) | Classifying email text                                | CountVectorizer, saved classification model, FastAPI                          |
| [**03. Automated News Categorization Engine**](./03%20-%20Automated%20News%20Categorization%20Engine/)              | Categorizing news articles                            | TF-IDF, saved classification model, FastAPI                                   |
| [**04. Legal Document Similarity & Retrieval Engine**](./04%20-%20Legal%20Document%20Similarity%20%26%20Retrieval%20Engine/)          | Retrieving similar legal clauses                      | Word2Vec, averaged word embeddings, cosine similarity                         |
| [**05. Semantic Similarity Engine**](./05%20-%20Semantic%20Similarity%20Engine/)       | Searching a knowledge base                            | TF-IDF, Word2Vec, FastText                                                    |
| [**06. Content-Based Product Recommendation Engine**](./06%20-%20Content-Based%20Product%20Recommendation%20Engine/)           | Finding products from textual similarity              | TF-IDF, Word2Vec, FastText; FastText application                              |
| [**07. Neural Text Prediction & Generation System**](./07%20-Neural%20Text%20Prediction%20%26%20Generation%20System/)             | Predicting and generating text continuations          | SimpleRNN, LSTM, GRU                                                          |
| [**08. Multilingual Neural Translation System**](./08%20-%20%20Multilingual%20Neural%20Translation%20System/)             | Multilingual support-message translation              | NLLB-200 distilled 600M                                                       |
| [**09. AI-Powered Legal Document Summarizer**](./09%20-%20%20AI-Powered%20Legal%20Document%20Summarizer/)              | Summarizing English legal text                        | BART-large-CNN                                                                |
| [**10. AI-Powered Resume Screening & Candidate Ranking System**](./10%20-%20AI-Powered%20Resume%20Screening%20%26%20Candidate%20Ranking%20System/)                | Resume–job description matching and entity extraction | BGE embeddings, BERT NER                                                      |
| [**11. Clinical Named Entity Recognition System**](./11%20-%20Clinical%20Named%20Entity%20Recognition%20System/)                  | Medical named entity recognition experiments          | spaCy Transformers, BioClinicalBERT                                           |
| [**12. Transformer-Based Question Answering System**](./12%20-%20Transformer-Based%20Question%20Answering%20System/)              | Extracting answers from supplied passages             | DistilBERT, SQuAD                                                             |

## Skills Demonstrated

- Building text preprocessing, feature extraction, classification, and retrieval pipelines.
- Comparing sparse text representations, word embeddings, and recurrent neural architectures.
- Integrating pretrained Transformers into translation, summarization, document matching, and question-answering workflows.
- Organizing inference services, browser interfaces, model artifacts, and application tests.

## Featured Applications

### Semantic Search and Recommendations

- **Legal Document Similarity & Retrieval Engine:** Retrieves clauses using Word2Vec and cosine similarity.
- **Semantic Similarity Engine:** Compares TF-IDF, Word2Vec, and FastText retrieval.
- **Content-Based Product Recommendation Engine:** Uses FastText product vectors with a FastAPI backend and React frontend.

Project documentation:

- [Legal Document Similarity & Retrieval Engine](./04%20-%20Legal%20Document%20Similarity%20%26%20Retrieval%20Engine/README.md)
- [Semantic Similarity Engine](./05%20-%20Semantic%20Similarity%20Engine/semantic_similarity_fastapi/README.md)
- [Content-Based Product Recommendation Engine](./06%20-%20Content-Based%20Product%20Recommendation%20Engine/README.md)

### Next Word Studio

The notebook compares RNN, LSTM, and GRU models. The local browser application uses an exported GRU model to generate continuations and display next-word suggestions.

[Setup and model import instructions](./07%20-Neural%20Text%20Prediction%20%26%20Generation%20System/next-word-app/README.md)

### Language Studio

A Streamlit translation application using `facebook/nllb-200-distilled-600M`, with support for English, French, Spanish, Hindi, and Tamil. Includes source-language detection and protection of technical identifiers.

[Setup and usage](./08%20-%20%20Multilingual%20Neural%20Translation%20System/Language-Studio/README.md)

### Legal Summary Studio

A Flutter Web frontend and Flask backend using `facebook/bart-large-cnn`. Supports summary-length controls, pattern-based fact comparisons, and optional ROUGE evaluation against a reference summary.

[Setup and usage](./09%20-%20%20AI-Powered%20Legal%20Document%20Summarizer/legal_summary_studio/README.md)

### Resume Screening

A FastAPI and React application combining `BAAI/bge-large-en-v1.5` embeddings with `yashpwr/resume-ner-bert`. Supports document extraction, section matching, similarity ranking, and candidate evidence review.

Similarity scores describe textual matching. The normalized fit score is relative to the uploaded candidate pool, not a qualification percentage.

[Setup and usage](./10%20-%20AI-Powered%20Resume%20Screening%20%26%20Candidate%20Ranking%20System/README.md)

### Extractive Question Answering

A DistilBERT application with FastAPI and a browser interface. It selects answer spans from supplied context using overlapping token windows and combined start/end scoring.

The notebook filename mentions SQuADv2, but its dataset-loading code uses `rajpurkar/squad`—SQuAD v1. Reliable unanswerable-question detection should not be assumed.

[Setup and model preparation](./12%20-%20Transformer-Based%20Question%20Answering%20System/question-answering-app/README.md)

## Technology Stack

| Area                        | Technologies                                       |
| --------------------------- | -------------------------------------------------- |
| Text processing             | NLTK, spaCy, regular expressions                   |
| Traditional NLP             | scikit-learn, Gensim                               |
| Deep learning               | TensorFlow/Keras, PyTorch                          |
| Transformers and embeddings | Hugging Face Transformers, Sentence Transformers   |
| Data processing             | pandas, NumPy                                      |
| Document extraction         | PyMuPDF, python-docx                               |
| Backends                    | FastAPI, Flask                                     |
| Interfaces                  | Streamlit, React, Flutter Web, HTML/CSS/JavaScript |
| Development                 | Jupyter Notebook, Google Colab, pytest             |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sujinoven/NLP_Projects.git
cd NLP_Projects
```

### 2. Choose a project

Each project has its own structure and dependencies. Follow its README where available and create a separate environment to avoid conflicts between TensorFlow, PyTorch, spaCy, and Transformers versions.

From the selected project directory:

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install the project's dependencies from the directory containing its requirements file:

```bash
python -m pip install -r requirements.txt
```

Some applications keep this file inside `backend/`. There is no shared root-level dependency file. Follow each application's Python-version requirements and any provided lock file; React interfaces also require Node.js, and the summarization interface requires Flutter.

### 3. Prepare datasets and models

Check the project's instructions before launching:

- **Semantic Similarity:** Supply `data/knowledge_base.csv` and run the model-training script.
- **Product Recommendation:** Export the prepared product CSV, FastText model, and product vectors. Keep CSV rows aligned with vector rows.
- **Next Word Studio:** Import the GRU bundle containing `best_gru.keras`, `tokenizer.json`, and `config.json`.
- **Question Answering:** Place the exported DistilBERT model and tokenizer files in the application's `model/` directory.
- **Clinical NER:** Provide the spaCy training, development, and test datasets and review the Colab configuration paths.
- **Transformer applications:** Allow internet access and sufficient disk space for the first model download.

### 4. Run notebooks or applications

For notebooks, install Jupyter in the chosen environment:

```bash
python -m pip install notebook
jupyter notebook
```

Notebooks using `google.colab` or Google Drive paths require Colab or local adaptations. Some project-level guides retain older local directory names; use the current project links above when navigating this repository.

Application entry points differ. Use the linked project documentation for the correct startup commands, frontend requirements, and ports.

## Learning Progression

1. Text cleaning, tokenization, and vectorization
2. Classification with Bag of Words and TF-IDF
3. Word2Vec, FastText, and cosine similarity
4. RNN, LSTM, and GRU sequence modeling
5. Transformer translation and summarization
6. Named entity recognition and document matching
7. Extractive question answering
8. Packaging models into usable applications

## Status and Limitations

This repository contains learning exercises and application prototypes. Some projects require external datasets, exported models, path updates, or code corrections before execution.

Tests are included in several applications, but a fresh end-to-end run of every project has not been verified. Recorded notebook results are experiment-specific.

Generated summaries and translations can contain errors. Similarity scores, entity predictions, and extracted answers should be reviewed in the context of their intended use.

## Author

Maintained by [SUJINOVEN](https://github.com/sujinoven) as part of an ongoing journey in machine learning, deep learning, and natural language processing.
