import os

def sanitize_collection_name(name: str) -> str:
    """
    ChromaDB collection name rules:
    - Must be string
    - Can only contain letters, numbers, underscores
    - Must start with letter
    - Length between 3-63 characters
    """
    # Remove all non-alphanumeric characters except underscores and hyphens
    sanitized = ''.join(char if char.isalnum() or char in ['_', '-'] else '_' for char in name)
    # Ensure starts with a letter
    if not sanitized[0].isalpha():
        sanitized = 'col_' + sanitized
    # Truncate if too long
    if len(sanitized) > 63:
        sanitized = sanitized[:63]
    # Ensure minimum length
    if len(sanitized) < 3:
        sanitized = sanitized + '_collection'
    return sanitized

def extract_filename(filepath: str) -> str:
    """
    Extracts the filename without extension from a given filepath
    Args:
        filepath (str): Full path to the file
    Returns:
        str: Filename without extension
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def extract_extension(filepath: str) -> str:
    """
    Extracts the file extension from a given filepath
    Args:
        filepath (str): Full path to the file
    Returns:
        str: File extension including the dot (e.g. '.pdf')
    """
    return os.path.splitext(filepath)[1]