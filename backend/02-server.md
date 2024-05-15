# README for the Backend Folder

This backend folder is part of a larger project that uses Python and the FastAPI framework to create a conversational AI application. The application uses OpenAI's GPT-3 model for generating responses and Pinecone for storing and retrieving document embeddings.

## Folder Structure

The backend folder is organized into several sub-folders and files:

- `routes`: This folder contains the `routes.py` file which defines the API endpoints for the application. It includes endpoints for setting the OpenAI API key, getting chat history files, selecting a chat history, creating a new chat, and getting a response from the AI.

- `src`: This folder contains the source code for the application. It includes the `data_uploader.py` file which is responsible for processing PDF files, generating document embeddings, and upserting documents into the Pinecone index.

- `app_streamlit.py`: This is the main application file. It uses the Streamlit library to create a web-based user interface for interacting with the conversational AI. It includes functions for generating and saving chat history files, initializing the Pinecone client, and getting a response from the AI.

## How It Works

The application works by first setting the OpenAI API key, which is used to authenticate requests to the OpenAI API. The user can then create a new chat or select an existing chat history. When the user asks a question, the application retrieves relevant documents from the Pinecone index, generates a response using the GPT-3 model, and saves the response to the chat history.

The `data_uploader.py` script is used to process PDF files and upload them to the Pinecone index. It splits each PDF into chunks, generates embeddings for each chunk using the GPT-3 model, and upserts the chunks and their embeddings into the Pinecone index.

## Getting Started

To run the application, you will need to install the required Python packages, and run the 
`app_streamlit.py` script using the following command:

```
streamlit run ./backend/app_streamlit.py
```

Please note that this is a high-level overview of the backend folder. For more detailed information,
please refer to the comments and documentation in the individual files.