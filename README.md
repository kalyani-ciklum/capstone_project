# AI Agentic Expense Assistant

A local Python capstone project that answers employee expense policy questions,
checks expense claims, retrieves policy context, optionally uses Gemini for
answer wording, calls tools, reflects on its answers, and runs a small
evaluation suite.

No API key is required for the local RAG path. Gemini is optional.

## What This Project Demonstrates

- Menu-driven CLI assistant in `main.py`
- Agent routing and reasoning in `agent.py`
- Local RAG retrieval in `rag_pipeline.py`
- Optional Gemini client in `llm/llm_client.py`
- Tool calling in `tools.py`
- Self-reflection scoring in `reflection.py`
- Keyword-based evaluation in `evaluation.py`
- Sample policies, expenses, evaluation questions, and output folders

## Technologies Used

- Python 3
- scikit-learn
- google-genai, optional Gemini client
- python-dotenv, optional `.env` loading
- TF-IDF retrieval with `TfidfVectorizer`
- cosine similarity for top-3 policy chunk search
- Python standard libraries: `csv`, `json`, `pathlib`, `re`, and `datetime`
- Mermaid diagram in `architecture.mmd`

## Project Structure

```text
.
├── main.py
├── agent.py
├── rag_pipeline.py
├── tools.py
├── reflection.py
├── evaluation.py
├── architecture.mmd
├── llm/
│   ├── __init__.py
│   └── llm_client.py
├── data/
│   ├── approval_policy.md
│   ├── meal_expense_policy.md
│   ├── reimbursement_policy.md
│   └── travel_expense_policy.md
├── expenses/
│   └── sample_expenses.csv
├── eval/
│   └── test_questions.json
├── outputs/
│   └── .gitkeep
├── .env.example
├── requirements.txt
└── .gitignore
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional Gemini setup:

```bash
cp .env.example .env
```

Then edit `.env`:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run the assistant:

```bash
python main.py
```

If your system uses `python3`:

```bash
python3 main.py
```

## CLI Menu

```text
====================================
 AI AGENTIC EXPENSE ASSISTANT
====================================
1. Ask an expense policy question
2. Check an expense claim
3. Summarize a policy
4. Run evaluation
5. Give feedback
6. Exit
====================================
```

## Sample Inputs for Review

Try these from the menu:

- `Are taxi expenses reimbursable?`
- `Can I claim dinner worth 900 INR?`
- `What is the maximum meal reimbursement?`
- `When does manager approval become necessary?`
- Run option `4` to execute evaluation.

Expected evaluation result:

```text
Passed: 4 / 4 (100.00%)
```

## How the Logic Works

1. `main.py` collects user input from the CLI.
2. `agent.py` detects intent and chooses a tool or RAG response path.
3. `rag_pipeline.py` loads Markdown policy files, cleans text, splits it into
   chunks, builds TF-IDF vectors, and retrieves the top 3 relevant chunks.
4. `llm/llm_client.py` optionally sends grounded prompts to Gemini with retry
   handling when `GEMINI_API_KEY` is configured.
5. `tools.py` handles policy search, expense checks, summaries, feedback,
   flagging, and evaluation.
6. `reflection.py` scores each answer for relevance, groundedness, and clarity.
7. `evaluation.py` compares answers against expected keywords in
   `eval/test_questions.json`.

## Architecture Diagram

Open `architecture.mmd` in any Mermaid-compatible viewer to review the flow.

## Notes for Mentors

- The assistant is intentionally local and beginner-friendly.
- RAG works without external LLM APIs; Gemini enhancement is optional.
- Runtime feedback and flagged expense CSV files are ignored by Git through
  `outputs/*.csv`.
- `outputs/.gitkeep` keeps the output directory present in the repository.
