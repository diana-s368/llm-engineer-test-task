import pytest 

from pydantic import ValidationError
from src.schemas import DocumentExtraction


# tests for the DocumentExtraction model

# creates a single example of a valid document, which we will use in several tests

# first we create correct document and then we replace some fields with invalid values to test the validation rules
# If there are five errors in a document at the same time, we won't always be able to tell which specific condition caused the problem.

def valid_document():
    return {
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
        },
        "warnings": []
    }


# first test checks that a valid document is accepted by the model
def test_valid_document(): 
    # valid_document() creates a dictionary containing our data.
    # documentExtraction.model_validate() takes this dictionary and validates it against the DocumentExtraction model.
    document = DocumentExtraction.model_validate(valid_document())

    # assert statements check that the values in the validated document match what we expect. 
    # If any of these assertions fail, the test will fail, indicating that something is wrong with our model or our data.
    assert document.doc_type == "invoice"
    assert document.supplier_bin == "123456789012"


def test_missing_fields_are_rejected(): 
    data = valid_document()
    del data["supplier_bin"]

    # expects that the model will raise a ValidationError when we try to validate a document that is missing required fields
    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data) # try to validate the document with missing fields, expecting a ValidationError to be raised


# test that fields that can be None are correctly handled by the model
def test_null_values_are_allowed(): 
    data = valid_document()

    # we check that None is allowed for string, date, and numeric fields that are defined as optional in the model
    data["supplier_bin"] = None
    data["doc_date"] = None
    data["vat_amount"] = None

    # But that doesn't mean that all the other nullable fields have already been tested individually. 
    # This is one area where there is room for improvement.
    document = DocumentExtraction.model_validate(data)
    # check that the fields that we set to None are indeed None in the validated document, not "None" as a string or some other value
    assert document.supplier_bin is None
    assert document.doc_date is None
    assert document.vat_amount is None


# To make sure that your own BIN business validation actually works 
def test_invalid_bin_is_rejected(): 
    data = valid_document()
    data["supplier_bin"] = "12345"  # Invalid BIN

    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)

# we're not checking our own function, but rather the built-in Literal type check.
def test_invalid_currency_is_rejected(): 
    data = valid_document()
    data["currency"] = "RUB"  # Invalid currency

    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)


# checking the range of the confidence score, which should be between 0 and 1.
def test_invalid_confidence_is_rejected(): 
    data = valid_document()
    data["field_confidence"]["supplier_bin"] = 1.5  # Invalid confidence score
    
    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)


# checking that the date is in a valid format. The model expects a date in the format "YYYY-MM-DD", 
# so we provide an invalid date to see if the model correctly raises a ValidationError.
def test_invalid_date_is_rejected(): 
    data = valid_document()
    data["doc_date"] = "2026-15-40"  # Invalid date format

    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)

# checking that the model correctly rejects a string value for a field that expects a numeric value.
def test_string_amount_is_rejected(): 
    data = valid_document()
    data["total_amount"] = "186180"  # Invalid amount type

    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)

# checking that the model correctly rejects extra fields that are not defined in the model.
def test_extra_fields_are_rejected():
    data = valid_document()
    data["unknown_field"] = "This should not be here"  # Extra field

    with pytest.raises(ValidationError):
        DocumentExtraction.model_validate(data)