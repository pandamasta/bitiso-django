from django.core.exceptions import ValidationError

def validate_query(query, min_length=2, max_length=50):
    """
    Validates a query string for minimum and maximum length.
    :param query: The query string to validate.
    :param min_length: Minimum allowed length for the query.
    :param max_length: Maximum allowed length for the query.
    :return: The cleaned query if valid.
    :raises: ValidationError if the query is invalid.
    """
    if len(query) < min_length:
        raise ValidationError(f"Query must be at least {min_length} characters long.")
    if len(query) > max_length:
        raise ValidationError(f"Query must not exceed {max_length} characters.")
    return query.strip()
