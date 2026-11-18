from typing import Annotated, Literal 

# Annotated - Adds additional constraints to the type
# literal - Allows only specific values

from pydantic import BaseModel, ConfigDict, Field, field_validator

# basemodel - Base class for creating data models
# configdict - Used to configure model behavior
# field - Used to define model fields with additional constraints
# field_validator - Decorator for adding custom validation logic to model fields


# Confidence score must be between 0 and 1 
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]

#Numeric value can be integers or float or null 
NumberOrNull = int | float | None


class LineItem(BaseModel): 
    # Docstring — текстовое описание класса или функции.
    """Represents one product or service in a document."""

    # Запрещаем дополнительные поля
    model_config = ConfigDict(strict=True, extra="forbid") 

    # attributes of a line item
    name: str
    qty: NumberOrNull
    price: NumberOrNull

class DocumentExtraction(BaseModel):
    """Represents the structured information extracted from a document."""
    model_config = ConfigDict(strict=True, extra="forbid") 

    # means LLM can return only one of the specified values for doc_type
    # for example the contract type will be declined
    doc_type: Literal["invoice", "commercial_offer", "act", "unknown"]

    # we do not write None = None because it is not necessary, the default value is None 
    supplier_name: str | None
    supplier_bin: str | None
    doc_number: str | None
    doc_date: str | None

    currency: Literal["KZT", "USD", "EUR"] | None

    total_amount: NumberOrNull
    vat_amount: NumberOrNull

    # list of products or services in the document, can be None if not extracted
    # "LineItem" means that each item in this list must conform to our LineItem model
    line_items: list[LineItem]

    # field_confidence is a dictionary where the keys are strings and the values are ConfidenceScore
    field_confidence: dict[str, ConfidenceScore]

    # list - of warnings generated during the extraction process, can be empty if no warnings
    warnings: list[str]

    # creating our own validation rules for the fields
    @field_validator("supplier_bin") # it says The following function should be used to validate the `supplier_bin` field
    @classmethod
    def validate_supplier_bin(cls, value: str | None) -> str | None:
        """Validates the supplier BIN (Business Identification Number)."""
        if value is not None and (
            len(value) != 12 or not value.isdigit()
        ): 
            raise ValueError("Supplier BIN must be a 12-digit number.")
        return value

    @field_validator("doc_date")
    @classmethod
    def validate_doc_date(cls, value: str | None) -> str | None:
        """Validates the document date format (YYYY-MM-DD)."""
        if value is not None:
            import datetime
            import re

            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("Document date must be in YYYY-MM-DD format")

            try:
                datetime.date.fromisoformat(value)
            except ValueError:
                raise ValueError("Document date is not a valid date.")
        return value