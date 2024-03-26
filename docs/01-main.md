# AI Legal Assistant

### Project Overview

This project is a Python-based application designed to assist legal professionals by providing precise information about documents. 
It uses RAG(Retrieval Augmented Generation) Technique to generate embeddings for documents and store them in a Pinecone index. 
The application then uses these embeddings to retrieve relevant documents based on user queries.  

### Usage
To use this application, you need to have the necessary API keys for Pinecone and OpenAI. 
The application processes PDF files, generates embeddings for the documents in the PDF files, and stores these embeddings in a Pinecone index. 
You can then use the Streamlit application to query the index and get responses based on the content of the documents.  

### Dependencies
- This project is written in Python and uses several libraries, including:
- Pinecone for vector indexing and search
- OpenAI for generating document embeddings
- Streamlit for the web application interface(for now)
- Langchain for retrieval and question-answering

### Note
This project is specifically designed to assist with queries related to the Turkish Penal Code.

