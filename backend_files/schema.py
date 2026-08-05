import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from backend_files.Database import get_connection


def get_schema(table_name, include_sample=False):

    connection = get_connection()

    try:
        schema_df = pd.read_sql(
            f"PRAGMA table_info({table_name})",
            connection
        )   

        schema_text = "Schema:\n\n"

        for _, row in schema_df.iterrows():
            schema_text += f"{row['name']} ({row['type']})\n"

        if not include_sample:
            return schema_text

        sample_query = f"""
            SELECT *
            FROM `{table_name}`
            LIMIT 3
        """

        sample_df = pd.read_sql(sample_query, connection)

        return f"""
{schema_text}

Sample Data:
{sample_df.to_string(index=False)}
"""

    finally:
        connection.close()

        