import ollama 

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
    """

    if not document_text.strip():
        raise ValueError("Document text cannot be empty")

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

    # Get the generated JSON from the model response
    response_content = response.message.content

    # Parse JSON and validate it against our Pydantic schema
    document = DocumentExtraction.model_validate_json(response_content)

    return document
