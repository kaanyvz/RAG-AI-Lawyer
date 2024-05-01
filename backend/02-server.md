# Server Side

## Overview

This is the backend of the AI Legal Assistant application. 
It is responsible for processing PDF files, split them into chunks ,generating embeddings from the chunks for the documents in the PDF files, 
and storing these embeddings in a Pinecone index.

## Structure

The backend is structured into several directories and files:

- `src/`: This directory contains the source code for the backend.
- `src/consts/`: This directory contains constant values used throughout the backend like logger and directories.
- `log.py`: This file defines the format for logging messages.
- `directory.py`: This file defines several important directories used in the backend.

## Dependencies

The backend is written in Python and uses several libraries, including:

- Pinecone for vector indexing and search
- OpenAI for generating document embeddings

## Usage

- To use the backend, you need to have the necessary API keys for Pinecone and OpenAI. The backend processes PDF files, 
generates embeddings for the documents in the PDF files, and stores these embeddings in a Pinecone index.

- After you enter your OpenAI api key and Pinecone Api key into the `secrets.toml` file, 
you can run the application, by executing the following command `streamlit run src/app-streamlit` in the terminal. (`for now`)


## Note

This backend is specifically designed to assist with queries related to the Turkish Penal Code.
Your questions should be about the Turkish Penal Code.
