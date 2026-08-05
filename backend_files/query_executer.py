import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from backend_files.Database import get_connection


def execute_query(query):

    connection = get_connection()

    try:
        df = pd.read_sql(query, connection)

        return {
            "success": True,
            "data": df
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "query": query
        }

    finally:
        connection.close()

def upload_dataframe(df):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        column_definitions = []

        for column in df.columns:

            if pd.api.types.is_integer_dtype(df[column]):
                mysql_type = "BIGINT"

            elif pd.api.types.is_float_dtype(df[column]):
                mysql_type = "DOUBLE"

            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                mysql_type = "DATETIME"

            else:
                mysql_type = "TEXT"

            safe_column = str(column).replace("`", "")

            column_definitions.append(
                f"`{safe_column}` {mysql_type}"
            )

        cursor.execute("DROP TABLE IF EXISTS uploaded_data")

        create_query = f"""
        CREATE TABLE uploaded_data (
            {", ".join(column_definitions)}
        )
        """

        cursor.execute(create_query)

        column_names = [
            f"`{str(column).replace('`', '')}`"
            for column in df.columns
        ]

        placeholders = ", ".join(["?"] * len(df.columns))

        insert_query = f"""
        INSERT INTO uploaded_data
        ({", ".join(column_names)})
        VALUES ({placeholders})
        """

        rows = []

        for row in df.itertuples(index=False, name=None):

            cleaned_row = tuple(
                None if pd.isna(value) else value
                for value in row
            )

            rows.append(cleaned_row)

        cursor.executemany(insert_query, rows)

        connection.commit()

        return {
            "success": True,
            "table_name": "uploaded_data"
        }

    except Exception as e:

        connection.rollback()

        return {
            "success": False,
            "error": str(e)
        }

    finally:
        cursor.close()
        connection.close()