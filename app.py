from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

class Solution(BaseModel):
    s_id: str
    language: str
    solution: str

class Case(BaseModel):
    q_id: str
    case: str

app = FastAPI(title="CodeArana", description="Arena for Code LLMs (of course human can use it too)")

@app.get("/question/")
async def get_question(qid: int, language: str):
    #TODO
    return {"qid": qid, "description": "", "solutions": list()}

@app.get("/solution/")
async def get_question(qid: int = 0):
    #TODO
    return {"sid": qid, "content": list()}

@app.post("/submit")
def submit_solution(solution: Solution):
    #TODO
    return {"status": "success"}

@app.post("/submit")
def submit_case(case: Case):
    #TODO
    return {"status": "success"}