Build a lightweight, beginner-friendly web app for my fine-tuned DistilBERT question-answering model.

Use:
- Frontend: plain HTML, CSS, and JavaScript.
- Backend: FastAPI with PyTorch and Hugging Face Transformers.
- Serve the frontend through FastAPI so the app runs with one command and requires no Node.js build step.

Model:
I have a ZIP file named `distilbert_squad_model.zip` containing my trained model and tokenizer. Load them from a local `model/` folder using `AutoTokenizer` and `AutoModelForQuestionAnswering`. Inspect the extracted folder structure and explain where the model files must go. Use local files only; do not silently download a replacement model.

This is extractive question answering: users provide a context passage and a question, and the model selects an answer from that passage.

Features:
- A clean, responsive interface with a light theme.
- A large context text area and a question field.
- “Get Answer,” “Load Example,” and “Clear” buttons.
- An answer card and a highlighted answer inside the original context.
- Loading indicators, clear validation messages, and friendly backend errors.
- A short explanation that answers come from the supplied passage.

Backend:
- Load the model and tokenizer once at application startup.
- Use CPU by default, `model.eval()`, and `torch.inference_mode()`.
- Provide `GET /api/health` and `POST /api/answer`.
- Validate empty inputs and enforce reasonable, documented input limits.
- Handle long contexts with overlapping token windows using `max_length=384`, `stride=128`, and `truncation="only_second"`.
- Use token offsets to return the original answer text and its character positions.
- Select valid answer spans only from context tokens, with the end at or after the start and a configurable maximum answer length.
- Compare valid candidate spans across windows; do not simply take independent start and end argmax values.
- Do not present raw model scores as confidence percentages.
- This model was trained on SQuAD v1, so clearly explain that it cannot reliably detect questions whose answers are absent. Do not invent a reliable “no answer” threshold.
- Render user-provided text safely in the frontend.

Keep the folder structure simple:

question-answering-app/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── qa_service.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── model/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md

Implementation requirements:
- Keep the code readable with helpful comments and minimal dependencies.
- Avoid React, databases, authentication, Docker, and unnecessary abstractions.
- Exclude model weights, ZIP files, caches, and virtual environments from Git.
- Include Windows PowerShell instructions to extract the model, create a virtual environment, install dependencies, and run the app.
- Provide a few example contexts and questions.
- Test input validation, valid span selection, and long-context handling.
- Run a real prediction using my local model if its files are available. Clearly distinguish real-model verification from tests using mocks.
- If the model is missing, finish the app and give precise placement instructions; do not claim inference was tested.

Create the complete working application, not just a plan. Finish with a short explanation of the folder structure, setup commands, and what was verified.