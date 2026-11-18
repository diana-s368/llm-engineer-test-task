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