import pytest 

from src.schemas import DocumentExtraction
from src.validator import validate_document

# tests for the validate_document function

## The validate_document function performs business-level validation of extracted document data.

# It checks for negative amounts, negative line item quantities and prices, and low confidence scores.

# **overrides** is a dictionary that allows us to override specific fields in the valid document for testing purposes.
def create_document(**overrides): 
    data = {
        "doc_type": "invoice",
        "supplier_name": "Test Company",
        "supplier_bin": "123456789012",
        "doc_number": "1245",
        "doc_date": "2026-11-12",
        "currency": "KZT",
        "total_amount": 186180,
        "vat_amount": 25680,
        "line_items": [
            {
                "name": "Paper A4", 
                "qty": 50,
                "price": 2100
            }, 
            {
                "name": "Printer Ink", 
                "qty": 3,
                "price": 18500
            }
        ],
        "field_confidence": {
            "supplier_bin": 0.99,
            "total_amount": 0.95,
        },
        "warnings": []
    }

    # update - method of the dictionary class that updates the dictionary with the key-value pairs from another dictionary.
    data.update(overrides)

    # we create a DocumentExtraction object from the data dictionary. This will validate the data against the DocumentExtraction model.
    return DocumentExtraction(**data)


# Test that a valid document has no warnings
def test_valid_document_has_no_warnings(): 
    document = create_document()
    warnings = validate_document(document)
    assert warnings == []

# Test that a document with negative total_amount generates a warning
def test_negative_total_amount():
    document = create_document(total_amount=-100)
    warnings = validate_document(document)
    assert any("total_amount" in warning for warning in warnings)

# Test that a document with negative line item quantity generates a warning
def test_negative_qty():
    document = create_document(line_items=[{"name": "Item 1", "qty": -5, "price": 100}])
    warnings = validate_document(document)
    assert any("negative quantity" in warning for warning in warnings)

# Test that a document with low confidence score generates a warning
def test_low_confidence_score():
    document = create_document(field_confidence={"supplier_bin": 0.3})
    warnings = validate_document(document)
    assert any("Low confidence score" in warning for warning in warnings)

# Test that a document with multiple issues generates multiple warnings
def test_custom_confidence_threshold():
    document = create_document(field_confidence={"supplier_bin": 0.7})
    warnings = validate_document(document, confidence_threshold=0.8)
    assert len(warnings) == 1

# Test that a document with None amounts does not generate warnings
def test_null_amounts_are_allowed():
    document = create_document(total_amount=None, vat_amount=None)
    warnings = validate_document(document)
    assert warnings == []

    warnings = validate_document(document)

    assert warnings == []  # No warnings should be generated for None amounts

def test_negative_vat_amount():
    document = create_document(vat_amount=-100)
    warnings = validate_document(document)

    assert any("vat_amount" in warning for warning in warnings)


def test_negative_price():
    document = create_document(
        line_items=[{"name": "Item 1", "qty": 2, "price": -100}]
    )
    warnings = validate_document(document)

    assert any("negative price" in warning for warning in warnings)


def test_multiple_validation_warnings():
    document = create_document(
        total_amount=-100,
        line_items=[{"name": "Item 1", "qty": -2, "price": -100}],
        field_confidence={"supplier_bin": 0.3},
    )
    warnings = validate_document(document)

    assert len(warnings) == 4