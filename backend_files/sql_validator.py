def validate_sql(sql):

    sql = sql.strip()

    if not sql.endswith(";"):
        sql += ";"

    forbidden_words = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "UPDATE",
        "INSERT"
        "SHOW"
        "DESCRIBE"
    ]

    for word in forbidden_words:
        if word in sql.upper():
            raise Exception(f"{word} queries are not allowed.")

    return sql

