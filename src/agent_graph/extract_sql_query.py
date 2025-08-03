import re

def extract_sql_query(text: str) -> str:
    """
    Extract a clean SQL query from a possibly formatted or prefixed LLM output.
    Handles code blocks, 'SQLQuery:' prefix, and various SQL command types.
    """

    """
    Extract a clean SQL query from a formatted or prefixed LLM-generated string.

    This function is useful for parsing LLM outputs that may include:
    - Markdown code blocks (``` or ```sql)
    - Prefixed text like 'SQLQuery:' or 'Query:'
    - Extra formatting that is not part of the actual SQL

    The function attempts to:
    1. Remove code block markers.
    2. Strip known prefixes (e.g., "SQLQuery:").
    3. Extract the main SQL command (SELECT, INSERT, etc.).
    4. Clean up trailing characters like semicolons or backticks.

    Args:
        text (str): Raw output text from the LLM containing an SQL query.

    Returns:
        str: Cleaned SQL query string.
    """
    text = text.strip()

    # Step 1: Remove code block markers
    if text.startswith("```"):
        lines = text.splitlines()
        # Remove first/last lines if they're ``` or ```sql
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    # Step 2: Remove known prefixes like "SQLQuery:"
    text = re.sub(r"^(SQLQuery:|Query:|SQL:|sql:)\s*", "", text, flags=re.IGNORECASE)

    # Step 3: Extract only the actual SQL statement (any type)
    match = re.search(
        r"(SELECT|INSERT|UPDATE|DELETE|PRAGMA|CREATE|DROP|ALTER|DESCRIBE|SHOW)\s.+",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        query = match.group(0).strip()
        # Remove trailing backticks or semicolons
        return query.rstrip(";`").strip()

    # Step 4: If nothing matched, return original (but cleaned)
    return text
