from src.api.tools.sql_query_tool import sql_query_tool

query = "SELECT * FROM diseases LIMIT 5;"

result = sql_query_tool(query)

print(result)