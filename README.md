# LLM Engineer Technical Assessment

## 1. Project Overview

A Python-based document information extraction system that processes unstructured business documents and converts them into structured JSON.

The system is designed to extract information from:
- Invoices
- Commercial offers
- Acts

The main objective is to produce reliable structured data while minimizing hallucinations, missing values, and incorrect field extraction.

## 2. Task Requirements

The application must:

- Accept document text as input.
- Extract information according to a fixed JSON schema.
- Return `null` for information that is not explicitly available in the document.
- Never invent missing values or calculate unspecified taxes.
- Detect conflicting information and report it in `warnings`.
- Validate the generated JSON programmatically.
- Provide field-level confidence scores.
- Support local LLM inference without requiring a paid API.

## 3. Output Schema

The expected JSON structure:

- `doc_type`: invoice, commercial_offer, act, or unknown.
- `supplier_name`: string or null.
- `supplier_bin`: 12-digit string or null.
- `doc_number`: string or null.
- `doc_date`: YYYY-MM-DD or null.
- `currency`: KZT, USD, EUR, or null.
- `total_amount`: number or null.
- `vat_amount`: number or null.
- `line_items`: array of items containing name, qty, and price.
- `field_confidence`: confidence scores for extracted fields.
- `warnings`: array of strings describing inconsistencies or extraction issues.

## 4. Planned Technology Stack

- Python — application logic.
- Pydantic — structured output validation.
- Ollama — local LLM inference (planned).
- Pytest — automated testing.
- Git / GitHub — version control.

The final implementation and model selection will be documented as development progresses.

## 5. Dataset

The evaluation dataset will contain at least 10 documents:

- 3 documents provided in the original assessment.
- At least 7 additional documents created for testing.

The dataset will include challenging cases such as:
- Missing fields.
- Conflicting dates and amounts.
- Mixed Kazakh-Russian text.
- OCR errors.
- Documents without VAT information.
- Multiple line items.

Each document will have a corresponding expected JSON output (ground truth).

## 6. Validation and Evaluation

The system will include:

- Programmatic JSON schema validation.
- Field-level accuracy measurement.
- Hallucination counting: fields populated when the expected value is null.
- Omission counting: fields returned as null when the expected value exists.

A separate evaluation command will process the complete dataset and generate a report.

## 7. Project Structure

The project will be organized into separate modules for extraction, validation, prompts, evaluation, and testing.

## 8. Installation and Usage

Installation and execution instructions will be added after implementation.

## 9. Limitations and Development Status

This project is being developed as a time-limited technical assessment.

Implementation decisions, known limitations, trade-offs, and unfinished features will be documented here as development progresses.



## Development Progress: Initial LLM Integration

### 1. Local LLM Setup

Installed Ollama and configured a local language model.

- Model: Qwen3:4b
- Quantization: Q4_K_M
- Model size: approximately 2.5 GB
- Inference: local execution through Ollama
- Python client: ollama 0.6.3

The model was selected as a compromise between multilingual
capabilities, inference speed, and available hardware resources.

The target document languages are Russian, Kazakh, English,
and mixed-language documents.

### 2. Prompt Engineering

Created `src/prompts.py` containing the initial multilingual
system prompt.

The prompt defines:

- Supported document types.
- Required extraction fields.
- Missing-value handling.
- BIN extraction rules.
- Date normalization.
- Currency normalization.
- Line item extraction.
- VAT handling.
- Contradiction detection.
- Confidence scores and warnings.
- Strict JSON output requirements.

Additional rules were introduced after initial experiments
to prevent the model from calculating missing total amounts,
misclassifying documents, and confusing Kazakh month names.

### 3. LLM Integration

Created `src/extractor.py`.

The `extract_document()` function:

1. Accepts raw document text.
2. Sends the system prompt and document text to Ollama.
3. Uses Qwen3:4b for extraction.
4. Passes the Pydantic JSON Schema as the structured output format.
5. Disables thinking mode.
6. Uses temperature 0.
7. Validates the generated JSON using Pydantic.
8. Returns a `DocumentExtraction` object.

### 4. Initial Extraction Experiments

Created `test_extractor.py` to manually evaluate the model
on three different documents.

Test cases:

- Document 1: Russian invoice with two line items,
  explicit total amount, and numeric VAT.
- Document 2: Russian commercial offer with separate
  service prices, no explicitly stated total, and no VAT amount.
- Document 3: Mixed Kazakh/Russian invoice with a Kazakh
  month name, amount written in words, and VAT not applicable.

### 5. Observed Results

Document 1:
- Correct document classification.
- Correct supplier information and BIN.
- Correct date normalization.
- Correct line item extraction.
- Correct total amount and VAT.

Document 2:
- Correct commercial offer classification.
- Correct extraction of both services.
- Correct handling of missing BIN and document number.
- Correctly returns null for total_amount.
- Does not calculate a total by adding individual service prices.

Document 3:
- Correct invoice classification after prompt refinement.
- Correct supplier information and BIN.
- Correct extraction of document number.
- Correct extraction of the amount written in words.
- Correct handling of VAT not applicable.
- Incorrect normalization of the Kazakh month name "қазан".

### 6. Known Limitations and Technical Decisions

The current model still incorrectly interprets the Kazakh
month name "қазан" (October) as September.

This issue is intentionally documented rather than treated
as a completed fix.

We decided not to keep expanding the prompt indefinitely.
A more reliable solution may be to implement deterministic
date normalization in Python, using explicit language-specific
month mappings.

Other known limitations:

- Confidence scores are generated by the LLM and are not
  calibrated probabilities.
- Extraction quality has only been evaluated on three documents.
- Repeated inference can produce slightly different warnings.
- Pydantic validates structure and types, but cannot guarantee
  that extracted values are factually correct.
- Error handling and automated extraction tests are not yet
  implemented.

### 7. Next Development Steps

1. Implement deterministic normalization for Kazakh dates.
2. Add error handling for Ollama and Pydantic validation.
3. Create a dataset containing at least 10 documents.
4. Prepare ground-truth JSON files.
5. Implement evaluation metrics:
   - Field accuracy
   - Hallucination rate
   - Omission rate
6. Add automated unit and integration tests.
7. Implement a command-line interface.
8. Complete project documentation and architecture reflection.
