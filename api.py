# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from rag import rag_query

app = FastAPI(title="RedTeam LLM API")

class QueryRequest(BaseModel):
    prompt: str
    n_results: int = 3

@app.post("/chat")
def chat(req: QueryRequest):
    response = rag_query(req.prompt, n_results=req.n_results)
    return {"response": response}
