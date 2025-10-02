# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from .rag import rag_query

#Change your title here
app = FastAPI(title="My totally awesome local LLM API")


"""
n_results controls how many top chunks Chroma returns from your vector DB.

Example:
    n_results=2 → only the top 2 most relevant docs are passed into the LLM.
    n_results=10 → top 10 chunks are passed in.

Impact:
    (positive) More context, the model has more material to pull from
    (positive) MAY produce richer results or more accurate answers if extra docs are relevant
    (negative) Higher number = Higher token usage = Higher latency
    (negative) Potential use of irrelevant chunks which may lead to bad responses

"""

class QueryRequest(BaseModel):
    prompt: str
    n_results: int = 3

@app.post("/chat")
def chat(req: QueryRequest):
    response = rag_query(req.prompt, n_results=req.n_results)
    return {"response": response}
