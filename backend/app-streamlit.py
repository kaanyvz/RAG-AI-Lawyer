# -*- coding: utf-8 -*-
import os
import time
from typing import Dict, Optional

import streamlit as st
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.vectorstores.pinecone import Pinecone as LangChainPinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.llms import OpenAI
from pinecone import Pinecone

INDEX_NAME = "langchain-doc-index"
PROMPT_TEMPLATE = """You are a dedicated chatbot tasked with assisting legal professionals by providing precise 
information about the documents provided. Ensure your answers are: - Directly derived from the document's contents. - 
Clear and concise, facilitating quick comprehension. - Free of personal opinions or external advice.

In instances where the document does not contain the necessary information, or if you're uncertain, clearly state
this to the user, indicating that the response is based on best judgment rather than document specifics.

Question:"""
NUM_RETRIEVED_DOCS = 5
TEMPERATURE = 0.3


def initialize_pinecone_client(api_key: str) -> Pinecone:
    """Initializes and returns a Pinecone client."""
    return Pinecone(api_key=api_key)


def get_response(user_query: str) -> Dict[str, Optional[str]]:

    full_query = PROMPT_TEMPLATE + user_query
    pc_client = initialize_pinecone_client(api_key=st.secrets["pinecone_api_key"])

    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=st.secrets["openai_api_key"])
    index = pc_client.Index(INDEX_NAME)

    # Wait for index connection
    time.sleep(1)

    index.describe_index_stats()

    vectorstore = LangChainPinecone(index=index, embedding=embedding_model, text_key="context")
    llm = OpenAI(temperature=TEMPERATURE, openai_api_key=st.secrets["openai_api_key"])
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": NUM_RETRIEVED_DOCS})

    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=retriever)
    response = qa_chain(full_query)

    return response


st.title("AI Law")
st.write(
    """
This chatbot is designed to assist with queries related to Turkish Penal Code.
Simply enter your question below and receive concise, regulation-based answers.

**Knowledge base**:
[The merged Approved Documents](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5237.pdf)


"""
)

user_query = st.text_area("Enter your question here:")
if st.button("Get Response"):
    if user_query:
        response = get_response(user_query)
        print(response)
        st.write("Answer:", response.get("answer", "No answer found."))
        sources = response.get("sources")
        if sources:
            st.write("Source:", os.path.basename(sources))
        else:
            st.write("No specific source cited.")
    else:
        st.error("Please enter a question.")

