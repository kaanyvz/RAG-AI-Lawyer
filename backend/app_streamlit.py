import uuid
import os
import json
from dotenv import load_dotenv
import time
from typing import Dict, Optional
from pymongo import MongoClient
from pinecone import Pinecone
import streamlit as st
from langchain_community.vectorstores.pinecone import Pinecone as LangChainPinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from fastapi import HTTPException
import requests

load_dotenv()

INDEX_NAME_TEMPLATE = "langchain-doc-index-{}"
PROMPT_TEMPLATE = """
Soru: Sahip olduğun dökümana göre, 
"""
NUM_RETRIEVED_DOCS = 5
TEMPERATURE = 0.3
CONVERSATION_MEMORY_SIZE = 5

CHAT_HISTORY_FILE_TEMPLATE = "chat_history_{}_{}.json"

openai_api_key = None
pinecone_index_name = None
namespace = None
chat_history_files = []


def get_db():
    uri = "ENTER YOUR MONGODB URI HERE"
    client = MongoClient(uri)
    db = client["CLIENT"]  # replace with your database name
    return db


def generate_chat_history_file(openai_api_key: str) -> dict[str, str]:
    """
    This function is responsible for generating a new chat history file.
    It takes in the OpenAI API key as input and returns the newly created chat history file.
    """
    uuid_str = str(uuid.uuid4())
    chat_title = f"Chat History {len(get_chat_history_files(openai_api_key)) + 1}"
    return {"_id": CHAT_HISTORY_FILE_TEMPLATE.format(openai_api_key, uuid_str), "chat_title": chat_title}


def load_chat_history(chat_history_id):
    db = get_db()
    chat_histories = db["chat_histories"]
    chat_history = chat_histories.find_one({"_id": chat_history_id})
    return {"chat_history": chat_history["chat_history"], "chat_title": chat_history["chat_title"]}


def save_chat_history(chat_history, chat_history_id, chat_title):
    db = get_db()
    chat_histories = db["chat_histories"]
    chat_histories.update_one({"_id": chat_history_id},
                              {"$set": {"chat_history": chat_history, "chat_title": chat_title}}, upsert=True)


def get_chat_history_files(openai_api_key: str) -> list[dict]:
    """
    This function is responsible for getting the chat history files specific to a user's OpenAI API key.
    :param openai_api_key: The user's OpenAI API key
    :return: A list of chat history files associated with the user's API key
    """
    if not validate_openai_api_key(openai_api_key):
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")

    db = get_db()
    chat_histories = db["chat_histories"]
    chat_history_files = [
        {"id": doc["_id"], "title": doc["chat_title"]}
        for doc in chat_histories.find({"_id": {"$regex": f"chat_history_{openai_api_key}.*"}})
    ]
    return chat_history_files


def delete_chat_history(chat_history_id: str):
    """
    This function deletes the chat history from MongoDB based on the provided chat history ID.
    """
    db = get_db()
    chat_histories = db["chat_histories"]
    result = chat_histories.delete_one({"_id": chat_history_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat history not found")
    else:
        return {"message": "Chat history deleted successfully"}


def initialize_pinecone_client(api_key: str) -> Pinecone:
    return Pinecone(api_key=st.secrets["pinecone_api_key"])


def validate_openai_api_key(openai_api_key: str) -> bool:
    """
    This function is responsible for validating the OpenAI API key.
    It takes in the OpenAI API key as input and returns True if the key is valid, False otherwise.
    """
    url = "https://api.openai.com/v1/engines"
    headers = {"Authorization": f"Bearer {openai_api_key}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def get_response(user_query: str, chat_history: list, pinecone_index_number: str, namespace_str: str) -> Dict[str, Optional[str]]:
    """
    This function is responsible for getting the response from the AI model.
    It takes in the user's query, the chat history, and the Pinecone index number as input.
    It initializes the language model, the retriever, and the conversational retrieval chain.
    It then uses these to get a response from the AI model and appends the response to the chat history.
    If an error occurs during this process, it returns an error message.
    """

    try:
        full_query = PROMPT_TEMPLATE + user_query

        if not pinecone_index_number:
            return {"result": "Pinecone index number is not set", "chat_history": chat_history}

        # Construct Pinecone index name using the incoming Pinecone index number
        index_name = INDEX_NAME_TEMPLATE.format(pinecone_index_number)

        pc_client = Pinecone(api_key=st.secrets["pinecone_api_key"])
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=openai_api_key)
        index = pc_client.Index(index_name)  # Use constructed index name

        time.sleep(1)

        index.describe_index_stats()
        conversation_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        vectorstore = LangChainPinecone(index=index, embedding=embedding_model, text_key="context")
        llm = OpenAI(temperature=TEMPERATURE, openai_api_key=openai_api_key, max_tokens=1024)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": NUM_RETRIEVED_DOCS,
                                                                                      "namespace": namespace_str})

        qa_chain = ConversationalRetrievalChain.from_llm(llm=llm,
                                                         retriever=retriever,
                                                         memory=conversation_memory)

        result = qa_chain({'question': full_query, 'chat_history': chat_history})

        response = result['answer']
        chat_history.append((full_query, response))

        return {'result': result, 'chat_history': chat_history}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"answer": "An error occurred while processing your request. Please try again later.", "sources": None,
                "chat_history": chat_history}

