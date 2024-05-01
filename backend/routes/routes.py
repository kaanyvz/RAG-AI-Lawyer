from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app_streamlit import get_response, load_chat_history, save_chat_history, generate_chat_history_file, \
    get_chat_history_files

app = FastAPI()


class User(BaseModel):
    openai_api_key: str


class Query(BaseModel):
    question: str


class ChatHistory(BaseModel):
    chat_history_file: str


openai_api_key = None
chat_history_files = []


@app.post("/set_api_key")
async def set_api_key(user: User):
    global openai_api_key
    global chat_history_files
    openai_api_key = user.openai_api_key
    chat_history_files = get_chat_history_files(openai_api_key)
    return {"message": "API key set successfully"}


@app.get("/get_chat_history_files")
async def get_chat_history_files_endpoint():
    return {"chat_history_files": chat_history_files}


@app.post("/select_chat_history")
async def select_chat_history(chat_history: ChatHistory):
    global chat_history_file
    chat_history_file = chat_history.chat_history_file
    return {"message": "Chat history selected successfully"}


@app.post("/create_new_chat")
async def create_new_chat():
    global chat_history_file
    chat_history_file = generate_chat_history_file(openai_api_key)
    chat_history_files.append(chat_history_file)
    chat_history = []
    save_chat_history(chat_history, chat_history_file)
    return {"message": "New chat created successfully"}


@app.post("/get_response")
async def handle_get_response(user_query: Query):
    global chat_history_file
    chat_history = load_chat_history(chat_history_file)
    response = get_response(user_query.question, openai_api_key, chat_history)
    save_chat_history(response["chat_history"], chat_history_file)
    return response