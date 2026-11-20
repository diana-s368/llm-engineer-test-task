
import httpx
import ollama
import pytest

from src.extractor import extract_document


def test_empty_document():
    with pytest.raises(ValueError, match="Document text cannot be empty"):
        extract_document("   ")


def test_ollama_connection_error(monkeypatch):
    def mock_chat(**kwargs):
        raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr("src.extractor.ollama.chat", mock_chat)

    with pytest.raises(RuntimeError, match="Could not connect to Ollama"):
        extract_document("Test document")


def test_ollama_api_error(monkeypatch):
    def mock_chat(**kwargs):
        raise ollama.ResponseError("model not found", status_code=404)

    monkeypatch.setattr("src.extractor.ollama.chat", mock_chat)

    with pytest.raises(RuntimeError, match="Ollama API error"):
        extract_document("Test document")


def test_invalid_json_response(monkeypatch):
    def mock_chat(**kwargs):
        return type(
            "Response",
            (),
            {
                "message": type(
                    "Message",
                    (),
                    {"content": "This is not valid JSON"},
                )()
            },
        )()

    monkeypatch.setattr("src.extractor.ollama.chat", mock_chat)

    with pytest.raises(RuntimeError, match="invalid JSON"):
        extract_document("Test document")


def test_invalid_schema_response(monkeypatch):
    def mock_chat(**kwargs):
        return type(
            "Response",
            (),
            {
                "message": type(
                    "Message",
                    (),
                    {"content": "{}"},
                )()
            },
        )()

    monkeypatch.setattr("src.extractor.ollama.chat", mock_chat)

    with pytest.raises(RuntimeError, match="does not match"):
        extract_document("Test document")
