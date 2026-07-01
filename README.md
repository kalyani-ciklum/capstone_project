# AI Agentic Expense Assistant

A beginner-friendly Python capstone project that demonstrates an AI-agentic
retrieval augmented generation (RAG) assistant for employee expense management.
The project runs locally, uses policy documents as its knowledge base, calls
tools, reflects on answers, and includes a small evaluation workflow.

## Project Overview

Employees often ask the same questions about meals, travel, approvals, receipts,
and reimbursement limits. This assistant helps answer those questions using
local company policy documents instead of paid APIs.

The assistant can:

- Answer expense policy questions
- Retrieve relevant policy chunks with TF-IDF
- Check whether a claim is allowed, not allowed, or needs approval
- Summarize specific policies
- Flag expenses for review
- Save user feedback
- Run a keyword-based evaluation suite
- Reflect on its own answer quality

## Real-World Problem Statement

Finance and HR teams spend time answering repeated policy questions. Employees
also submit claims that may miss receipts, exceed limits, or need approval. A
local RAG assistant can reduce confusion by giving grounded answers from policy
documents and by explaining why a claim is allowed, not allowed, or needs review.

## System Architecture

```text
User CLI
  |
  v
ExpenseAgent
  |
  +-- RAG Pipeline
  |     +-- Load Markdown policy files
  |     +-- Clean text
  |     +-- Split into chunks
  |     +-- Build TF-IDF vectors
  |     +-- Retrieve top 3 policy chunks
  |
  +-- Tools
  |     +-- search_policy()
  |     +-- check_expense()
  |     +-- summarize_policy()
  |     +-- flag_expense()
  |     +-- save_feedback()
  |     +-- run_evaluation()
  |
  +-- Self-Reflection
        +-- Relevance score
        +-- Groundedness score
        +-- Clarity score
```

## Data Preparation

Policy documents are stored in the `data/` folder as Markdown files:

- `travel_expense_policy.md`
- `meal_expense_policy.md`
- `reimbursement_policy.md`
- `approval_policy.md`

The RAG pipeline loads these files, cleans the text, and splits the text into
overlapping chunks so the retriever can find relevant sections.

Sample expense claims are stored in:

```text
expenses/sample_expenses.csv
```

## RAG Pipeline

The RAG pipeline is implemented in `rag_pipeline.py`.

It uses:

- `TfidfVectorizer` from scikit-learn
- cosine similarity
- top 3 chunk retrieval

No paid API keys are required.

## Agent Reasoning

The agent is implemented in `agent.py`.

For each user request, the agent:

1. Detects the user intent.
2. Chooses the right tool.
3. Retrieves relevant policy context when needed.
4. Decides whether the retrieved context is enough.
5. Produces a grounded answer.
6. Explains why a claim is allowed, not allowed, or needs approval.
7. Runs self-reflection on the response.

## Tool Calling

Tools are implemented in `tools.py`.

Available tools:

- `search_policy(query)`
- `check_expense(amount, category, description)`
- `summarize_policy(policy_name)`
- `flag_expense(expense_id, reason)`
- `save_feedback(question, answer, rating)`
- `run_evaluation()`

Example routing:

- "Can I claim dinner worth 900 INR?" calls `check_expense()`
- "What is the travel policy?" calls `summarize_policy()`
- "Is taxi reimbursement allowed?" calls `search_policy()`
- "Run evaluation" calls `run_evaluation()`

## Self-Reflection

After each answer, `reflection.py` scores the response on:

- Relevance
- Groundedness
- Clarity

Each score is out of 10 and includes a short explanation plus an improvement
suggestion.

## Evaluation Method

Evaluation is implemented in `evaluation.py`.

Test questions live in:

```text
eval/test_questions.json
```

Each test case contains a question and expected keywords. The evaluation checks
whether the assistant's answer contains those keywords and reports:

- Passed questions
- Total questions
- Percentage score

## Sample Demo Flow

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
Enter your choice (1-6): 1
Ask your question: Are taxi expenses reimbursable?

Answer
Based on the retrieved expense policy context:
- Taxi and cab expenses are reimbursable for client meetings...
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

On some macOS systems, use:

```bash
python3 main.py
```

## Future Improvements

- Add a web interface with Streamlit or Flask
- Add semantic embeddings for better retrieval
- Store feedback in a database
- Add more policy documents
- Add expense anomaly detection
- Add unit tests for each tool
- Add role-based approval workflows
