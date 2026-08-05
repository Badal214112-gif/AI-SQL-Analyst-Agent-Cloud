import pandas as pd
import sys
import os
import traceback
import streamlit as st

st.set_page_config(
    page_title="AI SQL Analyst Agent",
    #page_icon="🤖",
    layout="wide"
)

backend_path = os.path.join(os.path.dirname(__file__), "backend_files")
sys.path.append(backend_path)

from backend_files.query_executer import execute_query, upload_dataframe
from backend_files.llm import (
    validate_question,
    generate_sql,
    explain_result
)


st.title("AI SQL Analyst Agent")

st.write("Welcome to your AI SQL Analyst!")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    uploaded_df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data Preview")
    st.dataframe(
        uploaded_df.head(),
        width="stretch"
    )
    if st.button("Upload to Database"):

        upload_result = upload_dataframe(uploaded_df)

        if upload_result["success"]:
            st.success("File uploaded successfully and saved to MySQL.")

        else:
            st.error(
                "The file could not be uploaded to MySQL. "
                "Please check the file and try again."
            )


user_question = st.text_input(
    "Ask your question:",
    placeholder="Example: Show total sales of Samsung"
)

ask = st.button("Ask AI")


if ask:

    if not user_question.strip():
        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner("Analyzing your question..."):

                table_name = "uploaded_data" if uploaded_file is not None else "sales_data"

                status = validate_question(user_question, table_name)

                if status.startswith("CHAT:"):
                    st.success(status.replace("CHAT:", "").strip())

                elif status.startswith("INVALID:"):
                    st.error(status.replace("INVALID:", "").strip())

                else:


                    sql_query = generate_sql(user_question, table_name)
                    print("=" * 80)
                    print("TABLE NAME:", table_name)
                    print("GENERATED SQL:")
                    print(repr(sql_query))
                    print("=" * 80)
                   

                    with st.expander("View Generated SQL"):
                        st.code(sql_query, language="sql")
                        st.write(sql_query)

                    result = execute_query(sql_query)

                   
                    if not result["success"]:
                        st.error(result["error"])
                        st.stop()

                    if result["success"]:

                        st.subheader("Query Result")
                        st.dataframe(
                        result["data"],
                        width="stretch"
                    )

                        insight = explain_result(
                            user_question,
                            result["data"]
                        )

                        st.subheader("AI Insight")
                        st.markdown(insight)

                    else:
                        st.error(result["error"])


        except Exception as e:
            st.error("Full Error Traceback")
            st.code(traceback.format_exc())

