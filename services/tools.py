from langchain.tools import tool
from services.config import Config
from sqlalchemy import create_engine, inspect, exc, text
from sqlalchemy.orm import Session

config = Config()

@tool
def sql_db_list_tables() -> str:
    """Input is an empty string, output is a comma-separated list of tables in the database."""
    try:
        engine = create_engine(config.db_url)

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        return tables
    except exc.ArgumentError as e:
        return f"ERROR: {e}"

@tool
def sql_db_schema(tables_name:str) -> str:
    """Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.
    Be sure that the tables actually exist by calling sql_db_list_tables first!
    Example Input: table1, table2, table3"""

    results = []

    try:
        engine = create_engine(config.db_url)

        inspector = inspect(engine)

        valid_tables = inspector.get_table_names()

        for table in tables_name.split(","):
            table = table.strip()
            if table not in valid_tables:
                results.append(
                    f"Error: table_names {{{table!r}}} not found in database"
                )
            else:
                with Session(engine) as session:
                    stmn = text(f"SELECT * FROM {table} LIMIT 3;")
                    result = session.execute(stmn)
                    rows = result.fetchall()
                    results.append(
                        f"/*\n3 rowns from {table} table:\n"
                        + "\t".join(result.keys())
                        + "\n"
                        + "\n".join("\t".join(str(x) for x in row) for row in rows) 
                        + "\n*/"
                    )
        return results
    except exc.ArgumentError as e:
        return f"ERROR: {e}"

@tool
def sql_db_query(query: str)-> str:
    """Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_db_schema to query the correct table fields."""
     
    try:
        engine = create_engine(config.db_url)
        with Session(engine) as session:
            result = session.execute(text(query))

            rows = result.fetchall()

            answer = "result :" \
            "\t".join(result.keys()) + \
            "\n" \
            "\n".join("\t".join(str(x) for x in row) for row in rows) 

        return answer 
    except exc.ArgumentError as e:
        return f"ERROR: {e}"

tools = [sql_db_list_tables, sql_db_schema, sql_db_query]

