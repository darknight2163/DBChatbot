from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils import setup_database, get_all_tables, fetch_table_data, test_sql_tools, get_db_tools, setup_sql_assistant, execute_direct_query, process_chat_query

# from pyngrok import ngrok
from fastapi import FastAPI
from langchain_groq import ChatGroq
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5173/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set Ngrok Auth Token
# ngrok.set_auth_token("2ojvUrZMjlMAEkaa3lR6sK4DHev_3UWvtqrw6JSZth9JDu3Ep")

# Initialize database and insert sample data
setup_database()

# Setup Langchain with DB
groq_api_key = "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"
llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma2-9b-it", temperature=0)
# tools, llm = setup_langchain(groq_api_key, llm)
tools = get_db_tools(groq_api_key)
# Create an Assistant with a query graph
graph = setup_sql_assistant(groq_api_key, llm)

# Define request model  
class ChatQueryRequest(BaseModel):
    input_message: str

class DirectQueryRequest(BaseModel):
    query: str

@app.get("/tables")
def get_tables():
    """API to return all table names in the database."""
    tables = get_all_tables()
    if "error" in tables:
        return {"status": "error", "message": tables["error"]}
    
    return {"status": "success", "tables": tables}

@app.get("/tables/data/{table_name}")
def get_table_data(table_name: str):
    """API to return data from a given table."""
    data = fetch_table_data(table_name)
    if "error" in data:
        return {"status": "error", "message": data["error"]}
    return {"status": "success", "data": data}

@app.get("/test_sql_tools")
async def test_sql():
    groq_api_key = "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"  # Use your Groq API key
    tables, schema, query_result = test_sql_tools(groq_api_key)

    # Return the results of invoking the tools
    return {
        "tables": tables,
        "schema": schema,
        "query_result": query_result
    }

@app.post("/chat_query")
async def chat_query_endpoint(request: ChatQueryRequest):
    if not request.input_message:
        raise HTTPException(status_code=400, detail="No query provided")
    try:
        result = process_chat_query(graph, request.input_message)
        return result
    except Exception as e: # Catch any exceptions during query processing
        raise HTTPException(status_code=500, detail=f"Chat query processing error: {e}")

@app.post("/direct_query")
async def direct_query_endpoint(request: DirectQueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="No query provided")
    try:
        result = execute_direct_query(request.query, tools)
        return {"result": result}
    except Exception as e: # Catch exceptions from the direct query execution
        raise HTTPException(status_code=500, detail=f"Direct query execution error: {e}")

if __name__ == "__main__":
    # public_url = ngrok.connect(8000)  # Expose port 8000
    # print(f"Ngrok tunnel URL: {public_url}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
