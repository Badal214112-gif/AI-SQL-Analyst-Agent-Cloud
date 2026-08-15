from backend_files.example_selector import get_examples
from backend_files.prompt_examples import (WINDOW_FUNCTION_EXAMPLES,CTE_EXAMPLES,COMPLEX_SQL_EXAMPLES,BUSINESS_QUERY_EXAMPLES)
from backend_files.schema import get_schema
from dotenv import load_dotenv
from groq import Groq
import os
import streamlit as st

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    api_key = st.secrets["GROQ_API_KEY"]

client = Groq(
    api_key=api_key
)

def validate_question(user_prompt, table_name):

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a MySQL database assistant.

Current Table:
{table_name}

Database Schema:
{get_schema(table_name, include_sample=False)}

Your job is to check whether the user's question can be answered using ONLY the available schema.

Rules:

Your ONLY job is classification.

Reply with EXACTLY ONE of the following:

VALID

CHAT: <short friendly reply>

INVALID: <reason>

Rules:

- Reply VALID if the user asks to retrieve, filter, summarize, aggregate, sort, rank, count, list, preview, inspect, or display data from the available table.

Examples:
- Show top 10 rows
- Show all rows
- Preview the data
- List all columns
- Total sales
- Highest revenue
- Average rating
- Top 5 cities
- Distinct payment methods
- Count records

Reply ONLY:
VALID

- If the user sends a greeting or general conversation (Hi, Hello, Hey, How are you?, What's your name?, Thank you, Bye, etc.), reply ONLY:
CHAT: <friendly reply ending with a short reminder that you can also help analyze uploaded data or answer questions about the connected database. Do not mention any specific database or table name.>

- If the question cannot be answered using the provided schema, reply ONLY:
INVALID: <reason>

Do NOT answer database questions.
Do NOT list columns.
Do NOT generate SQL.
Do NOT explain anything.

"""
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()


def generate_sql(user_prompt, table_name):


    examples = get_examples(user_prompt, table_name)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
                        {
                "role": "system",
                "content": f"""
                You are a Senior MySQL Database Engineer.

                Your task is to convert natural language into valid MySQL 8.0 SQL queries.

                Current Table:
                {table_name}

                Available Schema:
                {get_schema(table_name, include_sample=True)}

                Rules:

                Reasoning Rules:

                - Understand the user's business intent, not just keywords.
                - Strictly understand the question first.
                - Choose the simplest correct SQL whenever possible.
                - Use only tables and columns available in the schema.
                - Never invent new tables or column names.
                - If multiple SQL solutions are possible, choose the most efficient and readable one.
                - Use Previous Conversation only when the current question is a follow-up.
                - Words like "now", "only", "also", "same", "it", "them", "those", or "instead" usually indicate a follow-up question.
                - For follow-up questions, preserve all relevant filters, metrics, grouping, and context from the latest previous query.
                - Apply only the new change requested by the user.
                - Do not remove previous conditions unless the user explicitly asks to replace or reset them.

                You must understand the user's intent instead of matching exact words.

                The user may use casual English, business language, or synonyms.

                Map similar words to the closest available column whenever possible.

                Examples of mapping:

                - phone, phones, mobile, mobiles, handset, smartphone -> `Mobile Model`
                - company, manufacturer -> `Brand`
                - price, cost, amount -> `Price Per Unit`
                - sales, revenue, earnings, income -> `Total_Sale`
                - quantity, units, units sold -> `Units Sold`
                - rating, review, stars -> `Customer Ratings`
                - payment, payment type, payment mode -> `Payment Method`
                - customer, buyer -> `Customer Name`
                - place, location -> `City`
                - day, date -> `DATE`
                - profit, gain -> Total_Sale (if profit column doesn't exist)
                - transaction, order -> rows in {table_name}
                - revenue generated -> Total_Sale
                - best selling -> Units Sold
                - highest rated -> Customer Ratings

                SQL Decision Rules:

                - Use WHERE to filter rows before aggregation.
                - Use HAVING to filter aggregated results.
                - Use GROUP BY whenever the user asks for totals, counts, averages, minimums, maximums, or summaries by category.
                - Use ORDER BY with LIMIT for highest, lowest, top, bottom, first, or last results.
                - Use DISTINCT only when unique values are requested.
                - Use aggregate functions (SUM, AVG, COUNT, MIN, MAX) only when the question requires aggregation.
                - Prefer window functions for ranking, running totals, cumulative calculations, and previous/next comparisons.
                - Prefer CTEs when the query becomes easier to read or requires multiple calculation steps.
                - Never use SELECT * unless the user explicitly asks for all columns.
                - Return only the columns needed to answer the question.
                - Use meaningful aliases like total_sales, total_units, avg_rating, total_revenue, sales_rank, etc.
                - If the user asks for "best", "highest", "top", "maximum", use ORDER BY DESC with LIMIT 1 unless stated otherwise.
                - If the user asks for "worst", "lowest", "least", "minimum", use ORDER BY ASC with LIMIT 1.
                - Interpret "sales" as `Total_Sale` unless the user explicitly refers to quantity (`Units Sold`).
                - Interpret "performance" using the most relevant business metric (usually revenue, otherwise units sold or ratings based on context).

                Important:

                Schema Query Rules:

                If the user asks for:

                - column names
                - schema
                - table structure
                - available fields

                prefer:

                SHOW COLUMNS FROM {table_name};

                Use DESCRIBE {table_name}; only if the user explicitly asks to describe the table.

                Never answer with plain text.

                - For schema-related questions, generate a SQL query using only the provided schema and available tables.
                
                - Use ONLY tables and columns present in the schema.
                - Never create new column names.
                - Never replace spaces with underscores.
                - Always wrap column names containing spaces with backticks (`).
                - Use MySQL 8.0 syntax.
                - Use window functions whenever appropriate.
                - If the request is ambiguous, choose the most reasonable interpretation.
                - Return ONLY one SQL query.
                - Do not explain anything.
                - Do not use markdown.
                - End the SQL with a semicolon.

                Output Rules:

                - Always generate executable MySQL 8.0 SQL.
                - Do not include explanations, comments, markdown, or code fences.
                - If multiple SQL queries could answer the question, return the most efficient one.
                - Prefer readable SQL with proper formatting and aliases.
                - Avoid unnecessary subqueries when a simpler solution exists.
                - Prefer window functions over subqueries whenever they produce the same result more clearly.

                Return INVALID only if the user's request genuinely cannot be answered using the available schema.

                Examples:

                User: Show top 5 phones
                SQL:
                SELECT DISTINCT `Mobile Model`
                FROM {table_name}
                LIMIT 5;

                User: Show phones under 25000
                SQL:
                SELECT DISTINCT `Mobile Model`, `Price Per Unit`
                FROM {table_name}
                WHERE `Price Per Unit` < 25000;

                User: Which company earned the highest revenue?
                SQL:
                SELECT `Brand`, SUM(`Total_Sale`) AS total_sales
                FROM {table_name}
                GROUP BY `Brand`
                ORDER BY total_sales DESC
                LIMIT 1;

                User: Which payment mode is most used?
                SQL:
                SELECT `Payment Method`, COUNT(*) AS total_transactions
                FROM {table_name}
                GROUP BY `Payment Method`
                ORDER BY total_transactions DESC
                LIMIT 1;

                User: Show me column names

                SQL:
                SHOW COLUMNS FROM {table_name};

                User: Describe the table

                SQL:
                DESCRIBE {table_name};
                
                {examples}


                For ranking, top N, previous/next values, running totals, comparisons within groups, cumulative calculations, or row-wise analysis
                always prefer MySQL 8.0 window functions instead of subqueries whenever possible.

                Use MySQL 8.0 features whenever appropriate, including CTEs, subqueries, CASE, window functions, EXISTS, IN, UNION, and UNION ALL.
                """
            },
            {
                    "role": "user",
                    "content": f"""
                Current Question:
                {user_prompt}
                """
            }
        ]
    )

    sql = response.choices[0].message.content

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    return sql.strip()



def verify_sql(user_prompt, sql_query, table_name):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a Senior MySQL reviewer.

Database Schema:
{get_schema(table_name, include_sample=False)}

Your job is to review the generated SQL.

Rules:

- Check whether the generated SQL correctly answers the user's question.
- Verify table names, column names, syntax, and business logic.
- If the SQL is already correct, reply exactly:
VALID

- Do not rewrite SQL unnecessarily.

- If the SQL is incorrect, reply ONLY with the corrected SQL.
- Never return markdown or code fences.
- Do not explain anything.
"""
            },
            {
                "role": "user",
                "content": f"""
User Question:
{user_prompt}

Generated SQL:
{sql_query}
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()



def fix_sql(user_prompt, wrong_sql, error_message, table_name):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a Senior MySQL Database Engineer.

                Current Table:
                {table_name}

                Available Schema:
                {get_schema(table_name, include_sample=False)}

                IMPORTANT:
                
                - The table to query is: {table_name}
                - Always use {table_name} in the FROM clause.
                - Never use mobile_sales_db in the FROM clause because it is the database name, not a table.

                A SQL query has failed.

                Your job is to fix it.

                Rules:
                - Return ONLY one corrected MySQL query.
                - Do not explain anything.
                - Do not use markdown.
                - Preserve the original business intent.
                - Use exact table and column names.
                - If a column contains spaces, use backticks (`).
                - End the query with a semicolon.
                """
            },
            {
                "role": "user",
                "content": f"""
                User Question:
                {user_prompt}

                Wrong SQL:
                {wrong_sql}

                Database Error:
                {error_message}
                """
            }
        ]
    )

    sql = response.choices[0].message.content

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    return sql.strip()



def explain_result(user_prompt, result):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
You are a Senior Business Analyst.

Your job is to explain SQL query results in simple business language.

Rules:
- Keep the explanation within 3-5 lines.
- Strictly check and think about question for calculations.
- Use simple English.
- Mention important numbers.
- Don't mention any sign of currency.
- Do not mention SQL.
- Do not explain how the query works.
- Give only the business insight.
- If the result is empty, clearly state that no matching records were found.
"""
            },
            {
                "role": "user",
                "content": f"""
User Question:
{user_prompt}

Query Result:
{result}
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()




