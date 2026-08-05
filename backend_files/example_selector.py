from backend_files.prompt_examples import (
    WINDOW_FUNCTION_EXAMPLES,
    CTE_EXAMPLES,
    COMPLEX_SQL_EXAMPLES,
    BUSINESS_QUERY_EXAMPLES,
)


def get_examples(user_prompt, table_name):
    question = user_prompt.lower()
    examples = []

    # Window Functions
    if any(word in question for word in [
        "rank", "top", "running", "lag", "lead",
        "dense_rank", "row_number", "previous", "next"
    ]):
        examples.append(WINDOW_FUNCTION_EXAMPLES)

    # CTE
    if any(word in question for word in [
        "cte", "with"
    ]):
        examples.append(CTE_EXAMPLES)

    # Complex SQL
    if any(word in question for word in [
        "average", "growth", "compare",
        "above", "below"
    ]):
        examples.append(COMPLEX_SQL_EXAMPLES)

    # Business Queries
    if any(word in question for word in [
        "revenue", "sales", "brand",
        "city", "payment", "rating"
    ]):
        examples.append(BUSINESS_QUERY_EXAMPLES)

    examples = "\n".join(examples)

    examples = examples.replace("sales_data", table_name)
    examples = examples.replace("your_table_name", table_name)

    return examples
