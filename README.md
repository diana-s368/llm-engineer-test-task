# LLM Engineer Technical Assessment

## 1. Project Overview

This project implements a local Python-based document information extraction system. It uses a Large Language Model (LLM) to convert unstructured business documents into structured JSON data.

The application supports three types of documents:

- Invoices
- Commercial offers
- Acts of completed works

The main objective is to extract relevant information while minimizing hallucinations, missing values, and incorrect field extraction.

The system uses a local LLM through Ollama, Pydantic for structured data validation, and Pytest for automated testing.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11.18 | Application logic |
| Ollama | Local LLM inference |
| Qwen3:4b | Document information extraction |
| Pydantic 2 | Schema and data validation |
| Pytest | Automated testing |
| HTTPX | Handling connection-related errors |
| Git / GitHub | Version control |

### Model Selection

The selected model is **Qwen3:4b**, using Q4_K_M quantization. The downloaded model size is approximately 2.5 GB.

Model selection was an important part of the initial development process. The available hardware was limited to approximately 16 GB of RAM and an NVIDIA GeForce GTX 1650 Ti. Therefore, larger models were not the preferred option for local experimentation.

Qwen3:4b was selected as a compromise between model size, inference speed, and multilingual capabilities. This was particularly relevant because the target documents contain Russian, Kazakh, English, and mixed-language text.

The model runs locally, so the application does not require a paid external LLM API.

## 3. Development Environment and Initial Setup

The project was developed incrementally using:

- Python 3.11.18
- Conda (Miniconda3)
- An isolated environment named `.venv`
- Visual Studio Code
- Windows PowerShell 5.1
- pip for dependency management

One of the initial challenges was configuring a reproducible development environment. This involved creating an isolated Python environment, selecting the correct interpreter in VS Code, installing dependencies, and configuring the integrated terminal.

The original project directory also contained spaces in its name. It was renamed to `llm-engineer-test-task` to simplify paths and avoid potential environment and tooling issues.

The dependencies are declared in `requirements.txt`.

## 4. Output Schema

The application uses two Pydantic models: `DocumentExtraction` and `LineItem`.

The extraction schema contains:

| Field | Description |
|---|---|
| `doc_type` | invoice, commercial_offer, act, or unknown |
| `supplier_name` | Supplier name |
| `supplier_bin` | 12-digit business identification number |
| `doc_number` | Document number |
| `doc_date` | Document date in YYYY-MM-DD format |
| `currency` | KZT, USD, EUR, or null |
| `total_amount` | Explicitly stated final amount |
| `vat_amount` | Explicitly stated VAT amount |
| `line_items` | Items containing name, quantity, and unit price |
| `field_confidence` | Model-generated confidence scores |
| `warnings` | Extraction issues and document inconsistencies |

The schema uses strict type validation and rejects unexpected fields. Additional validation rules check BIN formatting, calendar dates, and confidence score boundaries.

Missing information is represented as `null`. The application does not intentionally calculate missing VAT or invent document totals.

## 5. Application Architecture

The application follows a straightforward extraction pipeline:

```text
Input document (.txt)
        |
        v
System Prompt + Document Text
        |
        v
Ollama + Qwen3:4b
        |
        v
Structured JSON Output
        |
        v
Pydantic Validation
        |
        v
Business Validation
        |
        v
Validated DocumentExtraction
        |
        v
JSON Output
```

The main components are separated into individual modules.

**`src/prompts.py`**

Contains the multilingual system prompt defining extraction rules, supported document types, missing-value handling, date and currency normalization, VAT rules, line-item extraction, contradiction handling, and JSON output requirements.

**`src/extractor.py`**

Implements `extract_document()`. It sends the document text and system prompt to Ollama, uses the Pydantic JSON Schema as the structured output format, and validates the model response.

**`src/schemas.py`**

Defines the Pydantic models and field-level constraints.

**`src/validator.py`**

Implements additional business validation checks, including negative monetary values, quantities, prices, and low-confidence fields.

## 6. Prompt Engineering and Extraction Rules

The system prompt was developed and refined through experiments with Russian, Kazakh, English, and mixed-language documents.

Several important rules were introduced:

- Missing values must be returned as `null`.
- The model must not invent supplier identifiers or document dates.
- VAT must only be extracted when a numeric amount is explicitly stated.
- VAT exemption or missing VAT information must not be interpreted as a numeric zero.
- `total_amount` must represent an explicitly stated final amount, not a sum calculated from individual line items.
- Conflicting totals must be reported through `warnings`.
- Document classification should rely on the document's title and content rather than only its number or reference.

An important distinction in the implementation is between ground truth and model confidence. Ground truth is manually prepared reference data, whereas confidence scores are generated by the LLM itself. These scores are not calibrated probabilities and do not guarantee extraction correctness.

## 7. Dataset Creation

A small evaluation dataset containing **10 business documents** was prepared.

It consists of three initial example documents and seven additional fictional business documents created to cover different extraction challenges.

Each input document has a corresponding manually prepared ground-truth JSON file. Ground truth was prepared independently of model predictions.

| Document | Type | Main test case |
|---|---|---|
| 001 | Invoice | Russian invoice with explicit VAT and total |
| 002 | Commercial offer | Separate service prices without an explicit total |
| 003 | Invoice | Mixed Kazakh/Russian text and Kazakh date |
| 004 | Invoice | Missing supplier BIN |
| 005 | Invoice | VAT information not provided |
| 006 | Invoice | Kazakh document with multiple line items |
| 007 | Act | Completed works and service period |
| 008 | Commercial offer | Incomplete metadata and monthly service pricing |
| 009 | Invoice | Contradictory invoice totals |
| 010 | Invoice | OCR character substitutions and mixed-language text |

The dataset covers missing fields, different document types, VAT-present and VAT-absent cases, multiple line items, multilingual text, OCR noise, and contradictory information.

All 10 ground-truth JSON files passed Pydantic validation.

## 8. Batch Extraction

The `run_batch_extraction.py` script processes all documents in `data/input/`.

For each document, it:

1. Reads the original text.
2. Calls `extract_document()`.
3. Receives a validated Pydantic object.
4. Saves the extracted result as JSON in `data/predictions/`.

Predictions are stored separately from ground truth to ensure that evaluation uses independent reference data.

**Initial batch extraction result: 10/10 documents processed successfully, with no execution failures.**

## 9. Error Handling and Testing

Basic application-level error handling was implemented to make the extraction pipeline more predictable.

The application handles:

- Empty input documents.
- Ollama connection errors.
- Ollama API errors, including model-related errors.
- Invalid JSON responses.
- Responses that do not match the expected Pydantic schema.

Original exceptions are preserved through exception chaining to support debugging.

Automated tests cover schema validation, business validation, and extraction error handling. The error-handling tests use mocking to simulate failures without requiring actual LLM calls.

**Test result: 23 tests passed.**

## 10. Evaluation

A simple evaluation script is implemented in `eval/evaluate.py`.

It compares model predictions against the manually prepared ground truth and reports field-level accuracy, hallucinations, and omissions.

- **Field accuracy:** percentage of exact matches for each field.
- **Hallucinations:** fields populated by the model when the expected value is `null`.
- **Omissions:** fields returned as `null` when the expected value exists.

For numeric values, integer and floating-point representations are normalized. Text comparisons ignore differences in capitalization and extra whitespace.

### Initial Evaluation Results

The following results were obtained using Qwen3:4b on the 10-document dataset.

| Field | Accuracy |
|---|---:|
| Document type | 60% |
| Supplier name | 100% |
| Supplier BIN | 100% |
| Document number | 100% |
| Document date | 90% |
| Currency | 100% |
| Total amount | 90% |
| VAT amount | 100% |
| Line items | 80% |

**Hallucinations:** 1 incorrect non-null total amount.

**Omissions:** 0 according to the current field-level metric.

The results show that the model performs well on several structured fields but has difficulties with document classification, multilingual date normalization, and incomplete or contradictory information.

Line items are evaluated using strict comparison of the complete list, including item names, quantities, and prices.

## 11. Challenges and Limitations

Several challenges appeared during development.

**Development environment and model selection.** Setting up the local Python environment, configuring VS Code, and selecting a model compatible with the available hardware required initial experimentation.

**Multilingual date extraction.** The model incorrectly interpreted the Kazakh month name `қазан` (October) in one document, returning September instead. This demonstrates that multilingual support does not guarantee correct normalization.

**Document classification and contradictions.** In the evaluation dataset, the model misclassified an invoice as a commercial offer and selected one of two conflicting totals instead of returning `null`.

**Line-item extraction.** Some bilingual descriptions were partially extracted, and one item name was incomplete.

**Confidence scores.** The model can report high confidence even when its extracted value is incorrect. Therefore, confidence scores should not be treated as objective probabilities.

The evaluation dataset is intentionally small and is suitable for demonstrating the pipeline rather than establishing production-level reliability. The current evaluation also uses exact field comparison and does not perform semantic matching of equivalent names or descriptions.

### Limitations and Incomplete Requirements

The project implements the core document extraction pipeline, batch processing, JSON output generation, Pydantic validation, and automated tests.

However, the user-facing CLI is not fully implemented. The current solution relies on Python scripts (`run_extraction_demo.py` and `run_batch_extraction.py`) rather than a dedicated command-line interface that accepts an arbitrary input file and an output path.

Therefore, the extraction pipeline is functional, but the user interaction requirement is only partially completed. Implementing a dedicated CLI with configurable input and output paths would be a necessary next step.


## 12. What I Learned

During this project, I gained practical experience in building an end-to-end LLM application rather than using a language model as a standalone tool.

I learned how to:

- Configure an isolated Python development environment and manage project dependencies.
- Select and run a local language model using Ollama.
- Design system prompts for multilingual structured information extraction.
- Define data contracts and validation rules using Pydantic.
- Use JSON Schema to constrain LLM output.
- Integrate a local LLM into a Python application.
- Handle connection errors, API errors, and invalid model responses.
- Write automated tests using Pytest and mocking.
- Create a small manually annotated dataset with ground truth.
- Implement batch processing and evaluate model predictions.
- Use Git and GitHub to manage incremental development.

An important lesson was that valid JSON does not necessarily contain correct information. Schema validation ensures structural correctness, while evaluation against ground truth is necessary to measure extraction quality.

## 13. Installation and Usage

### Prerequisites

- Python 3.11
- Ollama installed and running
- Git

### Setup

Clone the repository:

```bash
git clone https://github.com/diana-s368/llm-engineer-test-task.git
cd llm-engineer-test-task
```

Create and activate a Conda environment:

```bash
conda create -n llm-extraction python=3.11
conda activate llm-extraction
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the model:

```bash
ollama pull qwen3:4b
```

### Run the application

Run the batch extraction:

```bash
python run_batch_extraction.py
```

Run the evaluation:

```bash
python eval/evaluate.py
```

Run automated tests:

```bash
python -m pytest -v
```

A single-document demonstration is also available through `run_extraction_demo.py`.

## 14. Project Structure

```text
llm-engineer-test-task/
│
├── data/
│   ├── input/
│   ├── expected/
│   └── predictions/
│
├── eval/
│   └── evaluate.py
│
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── extractor.py
│   └── validator.py
│
├── tests/
│   ├── test_schemas.py
│   ├── test_validator.py
│   └── test_extractor.py
│
├── create_dataset.py
├── run_extraction_demo.py
├── run_batch_extraction.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 15. Final Development Status

The project implements a complete basic pipeline for local business document extraction, including structured output generation, Pydantic validation, business validation, error handling, batch processing, automated tests, and a small evaluation workflow.

The current results are a baseline for the selected model and dataset. The project prioritizes a clear, reproducible implementation and an honest assessment of model limitations rather than attempting to achieve perfect extraction accuracy.