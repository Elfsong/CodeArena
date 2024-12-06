# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)

import utils
from pydantic import BaseModel
from pymongo import MongoClient
from bson.json_util import dumps
from fastapi import FastAPI, Response, status


class Solution(BaseModel):
    q_id: str
    u_id: str
    language: str
    content: str

class TestCase(BaseModel):
    q_id: str
    u_id: str
    input: str
    output: str

class Question(BaseModel):
    q_id: str
    slug_name: str
    difficult: str
    content: str
    prompt: str


app = FastAPI(title="CodeArena", description="Arena for Code LLMs (of course human can use it too)")
db_username, db_password = utils.get_auth()
db_name, db_port = utils.get_db_info()
db_client = MongoClient(f"mongodb://{db_username}:{db_password}@localhost:{db_port}/?authSource={db_name}")

db = db_client["code_arena"]
question_collection = db["questions"]
solution_collection = db["solutions"]
testcase_collection = db["testcases"]

@app.get("/question/{q_id}")
async def get_question(q_id: str, response: Response):
    try:
        hint = question_collection.count_documents({"q_id": q_id})
        if hint:
            question = dumps(question_collection.find({"q_id": q_id})[0])
            response.status_code = status.HTTP_200_OK
            return {"status": "success", "content": question}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"status": "fail", "content": f"Question [{q_id}] doesn't exist in the [question] collection."}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "fail", "content": f"Question [{q_id}] Error: {e}"}

@app.get("/solution/{s_id}")
async def get_solution(s_id: str, response: Response):
    try:
        hint = solution_collection.count_documents({"s_id": s_id})
        if hint:
            solution = dumps(solution_collection.find({"s_id": s_id})[0])
            response.status_code = status.HTTP_200_OK
            return {"status": "success", "content": solution}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"status": "fail", "content": f"Solution [{s_id}] doesn't exist in the [solution] collection."}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "fail", "content": f"solution [{s_id}] Error: {e}"}

@app.post("/submit_solution")
def submit_solution(solution: Solution, response: Response):
    try:
        content_hash = utils.get_hash(f"{solution.q_id}_{solution.language}_{solution.u_id}_{solution.content}")

        #TODO: sandbox
        time_usage = None
        memory_usage = None

        solution_dict = {
            "q_id": solution.q_id,
            "u_id": solution.u_id,
            "s_id": content_hash,
            "language": solution.language,
            "content": solution.content,
            "time_usage": time_usage,
            "memory_usage": memory_usage,
        }

        result = solution_collection.insert_one(solution_dict) 
        solution_dict.pop('_id', None)
        if not result.acknowledged:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "fail", "content": f"Error: Solution insertion is not acknowledged."}

        result = question_collection.update_one({'q_id': solution.q_id}, {'$push': {'solutions': content_hash}})
        if not result.acknowledged:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "fail", "content": f"Error: Question update is not acknowledged."}

        response.status_code = status.HTTP_200_OK
        return {"status": "success", "content": solution_dict}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "fail", "content": f"Error: {e}"}

@app.post("/submit_testcase")
def submit_testcase(testcase: TestCase, response: Response):
    try:
        instance_input = utils.get_json(testcase.input)
        instance_output = utils.get_json(testcase.output)
        content_hash = utils.get_hash(f"{testcase.q_id}_{testcase.input}")

        testcase_dict = {
            "q_id": testcase.q_id,
            "u_id": testcase.u_id,
            "t_id": content_hash,
            "input": instance_input,
            "output": instance_output,
        }

        result = testcase_collection.insert_one(testcase_dict) 
        testcase_dict.pop('_id', None)
        if not result.acknowledged:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "fail", "content": f"Error: Testcase insertion is not acknowledged."}

        result = question_collection.update_one({'q_id': testcase.q_id}, {'$push': {'testcases': content_hash}})
        if not result.acknowledged:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "fail", "content": f"Error: Testcase update is not acknowledged."}

        response.status_code = status.HTTP_200_OK
        return {"status": "success", "content": testcase_dict}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "fail", "content": f"Error: {e}"}