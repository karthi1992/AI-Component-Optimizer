# AI-Component-Optimizer

AI Component Optimizer is a small FastAPI + OpenAI API that accepts React (TSX/JSX) component code and returns an AI-generated performance report. The report highlights issues (e.g. unnecessary re-renders, heavy useEffects), suggests improvements (memoization, splitting, state placement), and includes an example optimized version of the component.

## Setup

1. Clone and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=sk-your-key
   ```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  

## API

- **POST /analyze** — Body: `{ "code": "<React/TSX/JSX component source>" }`  
  Returns: `{ "issues": [], "suggestions": [], "optimized_example": "...", "summary": "..." }`
