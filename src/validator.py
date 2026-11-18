# Business Validation 
# checking the logical consistency of the extracted data.

from src.schemas import DocumentExtraction

def validate_document(
        document: DocumentExtraction, # The function accepts an object of type DocumentExtraction
        confidence_threshold: float = 0.5 # by default, the confidence threshold is set to 0.5, but it can be adjusted as needed
) -> list[str]: # returns a list of strings, which are the warnings generated during the validation process.
    """
    Perform business-level validation of extracted document data.

    Returns a list of warnings without modifying the original document.    
    """

    warnings = []

    # 1. check negative document amounts
    amount_fields = {
        "total_amount": document.total_amount,
        "vat_amount": document.vat_amount,
    }

    for field_name, value in amount_fields.items():
        if value is not None and value < 0:
            warnings.append(f"{field_name} contains a negative value: {value}")

    # 2. check negative line item quantities and prices 
    for index, item in enumerate(document.line_items):
        # enumerate is used to get both the index and the item itself from the list of line items.
        if item.qty is not None and item.qty < 0:
            warnings.append(
                f"Line item {index} has a negative quantity: {item.qty}"
            )
        if item.price is not None and item.price < 0:
            warnings.append(
                f"Line item {index} has a negative price: {item.price}"
            )

    # 3. check confidence scores
    for field_name, confidence in document.field_confidence.items():
        if confidence < confidence_threshold:
            warnings.append(
                f"Low confidence score for {field_name}: {confidence}"
            )

    return warnings