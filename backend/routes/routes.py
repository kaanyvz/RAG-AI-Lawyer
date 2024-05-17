from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.app_streamlit import get_response, load_chat_history, save_chat_history, generate_chat_history_file, \
    get_chat_history_files, delete_chat_history, get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or "*" for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    openai_api_key: str


class Query(BaseModel):
    question: str


class ChatHistory(BaseModel):
    chat_history_file: str


openai_api_key = None
pinecone_index_number = None
chat_history_files = []


@app.post("/set_api_key")
async def set_api_key(user: User):
    """
    This endpoint is responsible for setting the OpenAI API key.
    It takes in the OpenAI API key as a query parameter.
    """
    global openai_api_key
    global chat_history_files
    openai_api_key = user.openai_api_key
    chat_history_files = get_chat_history_files(openai_api_key)
    return {"message": "API key set successfully"}


@app.post("/set_pinecone_index")
async def set_pinecone_index_number(index_number: int):
    """
    This endpoint is responsible for setting the Pinecone index number dynamically.
    It takes in the Pinecone index number as a query parameter.
    """
    global pinecone_index_number
    pinecone_index_number = index_number
    return {"message": "Pinecone index number set successfully"}


@app.get("/get_chat_history_files")
async def get_chat_history_files_endpoint():
    """
    This endpoint is responsible for getting the chat history files.
    It takes in the OpenAI API key as a query parameter and returns the chat history files associated with that key.
    """
    return {"chat_history_files": chat_history_files}


@app.post("/create_new_chat")
async def create_new_chat():
    """
    This endpoint is responsible for creating a new chat history file.
    It takes in the OpenAI API key as a query parameter and returns the newly created chat history file.
    """
    global chat_history_file
    chat_history_file = generate_chat_history_file(openai_api_key)
    chat_history_files.append(chat_history_file["_id"])
    chat_history = []
    save_chat_history(chat_history, chat_history_file["_id"], chat_history_file["chat_title"])
    return {"message": "New chat created successfully", "chat_title": chat_history_file["chat_title"]}

@app.post("/select_chat_history")
async def select_chat_history(chat_history_id: str):
    """
    This endpoint is responsible for selecting a chat history file.
    It takes in the chat history ID as a query parameter and returns the selected chat history.
    """
    global chat_history_file
    chat_history_file = chat_history_id
    chat_history_content = load_chat_history(chat_history_file)
    print(chat_history_content)
    return {"chat_history": chat_history_content["chat_history"], "chat_title": chat_history_content["chat_title"]}


@app.post("/get_response")
async def handle_get_response(user_query: Query):
    """
    This endpoint is responsible for getting a response from the AI model.
    It takes in the user's query, the OpenAI API key, and the chat history as input.
    It returns a response from the AI model and appends the response to the chat history.
    """
    global chat_history_file
    chat_history = load_chat_history(chat_history_file)
    response = get_response(user_query.question, chat_history["chat_history"], pinecone_index_number)
    save_chat_history(response.get("chat_history", chat_history["chat_history"]), chat_history_file,
                      chat_history["chat_title"])
    return response

@app.delete("/delete_chat_history/{chat_history_id}")
async def delete_chat_history_endpoint(chat_history_id: str):
    """
    This endpoint is responsible for deleting a chat history from MongoDB.
    It takes in the chat history ID as a path parameter and deletes the corresponding chat history.
    """
    try:
        delete_chat_history(chat_history_id)
        global chat_history_files
        chat_history_files = [file for file in chat_history_files if file != chat_history_id]
        return {"message": "Chat history deleted successfully"}
    except HTTPException as e:
        return e.detail


@app.post("/update_chat_title")
async def update_chat_title(chat_history_id: str, chat_title: str):
    """
    This endpoint is responsible for updating the chat title of a chat history.
    It takes in the chat history ID and the new chat title as query parameters.
    """
    db = get_db()
    chat_histories = db["chat_histories"]
    chat_histories.update_one({"_id": chat_history_id}, {"$set": {"chat_title": chat_title}}, upsert=True)
    updated_chat_history = chat_histories.find_one({"_id": chat_history_id})

    return {
        "message": "Chat title updated successfully",
        "chat_title": updated_chat_history.get("chat_title")  # Return the updated chat title
    }