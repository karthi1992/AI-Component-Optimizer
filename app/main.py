"""
AI Component Optimizer — FastAPI + OpenAI API.
Accepts React (TSX/JSX) component code and returns an AI-generated performance report.
"""

import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Component Optimizer",
    description="Analyze React/TSX/JSX components for performance and get optimization suggestions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    code: str


class AnalyzeResponse(BaseModel):
    issues: list[str]
    suggestions: list[str]
    optimized_example: str
    summary: str


SYSTEM_PROMPT = """You are an expert React performance engineer. Given React (TSX/JSX) component code, produce a structured performance report in the following JSON format only (no markdown, no extra text):

{
  "issues": ["issue 1", "issue 2", ...],
  "suggestions": ["suggestion 1", "suggestion 2", ...],
  "optimized_example": "full optimized component code as a single string (escape newlines as \\n)",
  "summary": "Brief 1-2 sentence overall assessment"
}

Guidelines:
- issues: Highlight problems like unnecessary re-renders, heavy or missing dependency arrays in useEffect, inline object/function creation in render, missing memoization, large component that could be split, state that could be lifted or colocated, etc.
- suggestions: Concrete improvements (e.g. wrap in React.memo, use useCallback/useMemo, split component, move state, add key, lazy load).
- optimized_example: A complete, runnable optimized version of the component. Use \\n for newlines in the JSON string.
- summary: Short overall takeaway.
Respond with only valid JSON."""


@app.get("/")
def root():
    return {"message": "AI Component Optimizer API", "docs": "/docs"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set. Add it to a .env file.",
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.code},
            ],
            temperature=0.3,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")

    content = (response.choices[0].message.content or "").strip()
    # Remove markdown code fence if present
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not parse AI response as JSON: {e}. Raw: {content[:500]}",
        )

    issues = data.get("issues") or []
    suggestions = data.get("suggestions") or []
    optimized_example = data.get("optimized_example") or ""
    summary = data.get("summary") or ""

    return AnalyzeResponse(
        issues=issues,
        suggestions=suggestions,
        optimized_example=optimized_example,
        summary=summary,
    )
