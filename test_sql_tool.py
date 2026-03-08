import os

from dotenv import load_dotenv

# Load .env and use localhost when running this script on the host (outside Docker)
load_dotenv()
if os.getenv("SQL_HOST") == "db_sql":
    os.environ["SQL_HOST"] = "localhost"

from src.api.tools.sql_query_tool import sql_query_tool

query = "SELECT * FROM diseases LIMIT 5;"

result = sql_query_tool(query)

print(result)