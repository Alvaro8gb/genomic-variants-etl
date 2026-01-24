def clean_column_values(column_values):
    """Replace empty strings or '-' with None."""
    return [None if not v or v == "-" else v for v in column_values]
