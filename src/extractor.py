
import httpx
import ollama
from pydantic import ValidationError

from src.prompts import SYSTEM_PROMPT
from src.schemas import DocumentExtraction

MODEL_NAME = "qwen3:4b"


def extract_document(document_text: str) -> DocumentExtraction:
    """
    Extract structured information from a business document
    using a local Ollama model.

    Args:
        document_text: Raw text of the document.

    Returns:
        A validated DocumentExtraction object.

    Raises:
        ValueError: If the input document is empty.
        RuntimeError: If Ollama is unavailable or returns an API error.
        RuntimeError: If the model returns invalid JSON or data
                      that does not match the expected schema.
    """

    # 1. Validate input
    if not document_text.strip():
        raise ValueError("Document text cannot be empty")

    # 2. Send document to Ollama
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Extract information from this document:\n\n{document_text}",
                },
            ],
            format=DocumentExtraction.model_json_schema(),
            think=False,
            options={
                "temperature": 0,
            },
        )

    except httpx.RequestError as error:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from error

    except ollama.ResponseError as error:
        raise RuntimeError(
            f"Ollama API error: {error.error}"
        ) from error

    # 3. Get the generated JSON
    response_content = response.message.content

    # 4. Parse JSON and validate it against the Pydantic schema
    try:
        document = DocumentExtraction.model_validate_json(response_content)

    except ValidationError as error:
        error_details = error.errors()

        # Check whether the response contains invalid JSON
        if any(item["type"] == "json_invalid" for item in error_details):
            raise RuntimeError(
                "The model returned invalid JSON."
            ) from error

        # JSON is valid, but its structure or values are incorrect
        raise RuntimeError(
            "The model response does not match the expected document schema."
        ) from error

    return document
