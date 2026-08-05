from user_input import get_query
from sql_validator import validate_sql
from llm import generate_sql, fix_sql, verify_sql, explain_result, validate_question, rewrite_followup_question
from query_executer import execute_query

while True:
    user_prompt = get_query()

    if user_prompt.lower() in ["exit", "quit", "bye","ok thanks","good work","got it","done"]:
        print("Goodbye!")
        break

    validation = validate_question(user_prompt)

    if validation.startswith("CHAT:"):
        print("\nAI:", validation.replace("CHAT:", "").strip())
        exit()

    if validation != "VALID":
        print(validation)
        exit()

    user_prompt = rewrite_followup_question(user_prompt)
    
    # Generate SQL
    sql_query = generate_sql(user_prompt)

    # Validate SQL
    sql_query = validate_sql(sql_query)

    # Verify only if generate_sql actually returned SQL
    if sql_query.strip().upper().startswith(("SELECT", "WITH", "SHOW", "DESCRIBE")):
        verification = verify_sql(user_prompt, sql_query)

        if verification != "VALID":
            sql_query = validate_sql(verification)


    print("\nGenerated SQL:")
    print(sql_query)

    # Execute SQL
    result = execute_query(sql_query)

    if result["success"]:
        print("\nResult:")
        print(result["data"])

        explanation = explain_result(
            user_prompt,
            result["data"].head(20).to_string(index=False)
        )

        print("\nAI Insight:")
        print(explanation)

    else:
        print("\nDatabase Error:")
        print(result["error"])

        print("\nTrying to fix SQL...")

        corrected_sql = fix_sql(
            user_prompt,
            result["query"],
            result["error"]
        )

        print("\nCorrected SQL:")
        print(corrected_sql)

        result = execute_query(corrected_sql)

        if result["success"]:
            print("\nCorrected Result:")
            print(result["data"])

            explanation = explain_result(
                user_prompt,
                result["data"].head(20).to_string(index=False)
            )

            print("\nAI Insight:")
            print(explanation)
        else:
            print("\nStill Failed:")
            print(result["error"])
