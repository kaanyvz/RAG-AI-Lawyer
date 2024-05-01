import uuid
import os
import json
import streamlit as st
from typing import Dict, Optional
from langchain_community.vectorstores.pinecone import Pinecone as LangChainPinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from pinecone import Pinecone
from langchain.chains import ConversationalRetrievalChain
import time

INDEX_NAME = "langchain-doc-index-1"
PROMPT_TEMPLATE = """
Question:
"""
NUM_RETRIEVED_DOCS = 5
TEMPERATURE = 0.3
CONVERSATION_MEMORY_SIZE = 5

CHAT_HISTORY_FILE_TEMPLATE = "chat_history_{}_{}.json"

openai_api_key = None
chat_history_files = []


def generate_chat_history_file(openai_api_key: str) -> str:
    uuid_str = str(uuid.uuid4())
    return CHAT_HISTORY_FILE_TEMPLATE.format(openai_api_key, uuid_str)


def load_chat_history(chat_history_file):
    if os.path.exists(chat_history_file):
        with open(chat_history_file, "r") as file:
            return json.load(file)
    else:
        return []


def save_chat_history(chat_history, chat_history_file):
    with open(chat_history_file, "w") as file:
        json.dump(chat_history, file)


def get_chat_history_files(openai_api_key: str):
    chat_history_files = []
    for file in os.listdir():
        if file.startswith(f"chat_history_{openai_api_key}_"):
            chat_history_files.append(file)
    return chat_history_files


def initialize_pinecone_client(api_key: str) -> Pinecone:
    return Pinecone(api_key=st.secrets["pinecone_api_key"])


def get_response(user_query: str, openai_api_key: str, chat_history: list) -> Dict[str, Optional[str]]:
    try:
        full_query = PROMPT_TEMPLATE + user_query
        pc_client = initialize_pinecone_client(api_key=st.secrets["pinecone_api_key"])

        embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=openai_api_key)
        index = pc_client.Index(INDEX_NAME)

        time.sleep(1)

        index.describe_index_stats()
        conversation_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        vectorstore = LangChainPinecone(index=index, embedding=embedding_model, text_key="context")
        llm = OpenAI(temperature=TEMPERATURE, openai_api_key=openai_api_key)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": NUM_RETRIEVED_DOCS})

        qa_chain = ConversationalRetrievalChain.from_llm(llm=llm,
                                                         retriever=retriever,
                                                         memory=conversation_memory)

        result = qa_chain({'question': full_query, 'chat_history': chat_history})

        response = result['answer']
        chat_history.append((full_query, response))

        return {'result': result, 'chat_history': chat_history}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"answer": "An error occurred while processing your request. Please try again later.", "sources": None}


st.title("Conversational AI")

openai_api_key_input = st.text_input("Enter your OpenAI API key:")

if openai_api_key_input:
    openai_api_key = openai_api_key_input
    chat_history_files = get_chat_history_files(openai_api_key)

    if not chat_history_files:
        st.write("No chat history found. Create a new chat.")
    else:
        st.write("Chat Histories:")
        for i, chat_history_file in enumerate(chat_history_files):
            st.write(f"Chat History {i + 1}: {chat_history_file}")

    if st.button("Create New Chat"):
        chat_history_file = generate_chat_history_file(openai_api_key)
        chat_history_files.append(chat_history_file)
        chat_history = []
        save_chat_history(chat_history, chat_history_file)
        st.write("New chat created successfully!")

    if chat_history_files:
        selected_chat_history = st.selectbox("Select a chat history:", chat_history_files)

        if selected_chat_history:
            chat_history_file = selected_chat_history
            chat_history = load_chat_history(chat_history_file)

            user_query = st.text_area("Enter your question here:")

            if st.button("Get Response"):
                response = get_response(user_query, openai_api_key, chat_history)
                st.write("Answer:", response['result'].get("answer", "No answer found."))
                sources = response['result'].get("sources")
                if sources:
                    st.write("Source:", os.path.basename(sources))
                else:
                    st.write("No specific source cited.")

                st.write("Chat History:")
                for i, (question, answer) in enumerate(response['chat_history']):
                    st.write(f"Turn {i + 1}:")
                    st.write(f"Q: {question}")
                    st.write(f"A: {answer}")
                    st.write("---")

                # Save updated chat history
                save_chat_history(response['chat_history'], chat_history_file)
    else:
        st.error("Please enter a question.")
