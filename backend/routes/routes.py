from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app_streamlit import get_response

app = FastAPI()


class User(BaseModel):
    openai_api_key: str


class Query(BaseModel):
    question: str


openai_api_key = None


@app.post("/set_api_key")
async def set_api_key(user: User):
    global openai_api_key
    openai_api_key = user.openai_api_key
    return {"message": "API key set successfully"}


@app.post("/ask_question")
async def ask_question(query: Query):
    global openai_api_key
    if openai_api_key is None:
        raise HTTPException(status_code=400, detail="API key not set")
    response = get_response(query.question, openai_api_key)
    return response
