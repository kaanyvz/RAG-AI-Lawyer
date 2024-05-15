import pytest
from unittest import mock
from fastapi.testclient import TestClient
from backend.routes.routes import app
from backend.src.data_uploader import main as data_uploader_main
from backend.app_streamlit import get_response, load_chat_history, save_chat_history, generate_chat_history_file, \
    get_chat_history_files, delete_chat_history
import warnings

# Suppress deprecation warnings
warnings.simplefilter("ignore", category=DeprecationWarning)


client = TestClient(app)


def test_set_api_key():
    response = client.post("/set_api_key", json={"openai_api_key": "ENTER YOUR API KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "API key set successfully"}
