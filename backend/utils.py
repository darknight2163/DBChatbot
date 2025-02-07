# utils.py
import sqlite3
import os
import pandas as pd
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from fastapi import FastAPI, HTTPException
from typing import List, Dict
import re

def setup_database():
  db_name = "ProductsSuppliers.db"
  # Step 1: Check if the database file already exists
  if os.path.exists(db_name):
      print("Database already exists. Skipping setup.")
  else:
      # Step 2: Create and connect to the database
      con = sqlite3.connect(db_name)
      cur = con.cursor()
      # Step 3: Create tables if they don't exist
      cur.execute('''CREATE TABLE IF NOT EXISTS suppliers (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          contactinfo TEXT,
          productcategories TEXT
      );''')
      cur.execute('''CREATE TABLE IF NOT EXISTS products (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          brand TEXT,
          price REAL,
          category TEXT,
          description TEXT,
          supplierid INTEGER,
          FOREIGN KEY (supplierid) REFERENCES suppliers(id)
      );''')
      # Step 4: Insert sample data
      cur.executemany('''INSERT INTO suppliers (id, name, contactinfo, productcategories) VALUES (?, ?, ?, ?)''', [
          (1, 'a', 'contactA@example.com', 'electronics, home appliances'),
          (2, 'b', 'contactB@example.com', 'furniture, decor'),
          (3, 'c', 'contactC@example.com', 'groceries, beverages')
      ])
      cur.executemany('''INSERT INTO products (id, name, brand, price, category, description, supplierid) VALUES (?, ?, ?, ?, ?, ?, ?)''', [
          (1, 'smartphone', 'x', 699.99, 'electronics', 'latest model with AI camera', 1),
          (2, 'refrigerator', 'y', 1199.99, 'home appliances', 'energy-efficient cooling', 1),
          (3, 'sofa set', 'z', 499.99, 'furniture', 'comfortable 3-seater', 2),
          (4, 'dining table', 'z', 899.99, 'furniture', 'solid wood with six chairs', 2),
          (5, 'organic juice', 'w', 5.99, 'groceries', 'freshly squeezed organic fruit juice', 3)
      ])
      # Step 5: Commit changes and close the connection
      con.commit()
      print("Database created and data inserted.")

def get_all_tables():
    DB_NAME = "ProductsSuppliers.db"
    """Fetch the names of all tables in the database."""
    try:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Query to fetch all table names
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        return tables
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"error": str(e)}
    finally:
      pass

def fetch_table_data(table_name: str):
    DB_NAME = "ProductsSuppliers.db"
    """Fetch all data from a given table in the database."""
    try:
        con = sqlite3.connect(DB_NAME)
        con.row_factory = sqlite3.Row  # Enables dictionary-like row access
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"error": str(e)}
    finally:
      pass

def get_db_tools(groq_api_key):
    """Initialize and return the necessary tools for interacting with the database."""
    db = SQLDatabase.from_uri("sqlite:///ProductsSuppliers.db")
    toolkit = SQLDatabaseToolkit(db=db, llm=ChatGroq(groq_api_key=groq_api_key, model_name="gemma2-9b-it", temperature=0))
    tools = toolkit.get_tools()
    # Extract the specific tools for list, schema, and query
    list_tables_tool = next(tool for tool in toolkit.get_tools() if tool.name == "sql_db_list_tables")
    get_schema_tool = next(tool for tool in toolkit.get_tools() if tool.name == "sql_db_schema")
    db_query_tool = next(tool for tool in toolkit.get_tools() if tool.name == "sql_db_query")
    return tools

def test_sql_tools(groq_api_key):
    """Function to invoke SQL tools and return the results."""
    list_tables_tool, get_schema_tool, db_query_tool = get_db_tools(groq_api_key)
    # Test List Tables Tool
    tables = list_tables_tool.invoke("")
    # Test Get Schema Tool (for the 'products' table)
    schema = get_schema_tool.invoke("products")
    # Test DB Query Tool (select all from 'products')
    query_result = db_query_tool.invoke("SELECT * FROM products")
    return tables, schema, query_result

def setup_sql_assistant(groq_api_key, llm):
    """Setup and return the query graph for SQL assistant."""
    # Initialize the state graph
    tools = get_db_tools(groq_api_key)
    builder = StateGraph(MessagesState)
    # Define the assistant node
    def sql_assistant(state: MessagesState):
        return {'messages': llm.bind_tools(tools).invoke(state['messages'])}
    # Add nodes and edges to the graph
    builder.add_node('sql_assistant', sql_assistant)
    builder.add_node('tools', ToolNode(tools))
    # Create edges to link the nodes
    builder.add_edge(START, 'sql_assistant')
    builder.add_conditional_edges('sql_assistant', tools_condition)
    builder.add_edge('tools', 'sql_assistant')
    # Compile the graph
    graph = builder.compile()
    return graph

def execute_direct_query(query: str, tools: List) -> str:
    """Executes a direct SQL query."""
    try:
        db_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
        result = db_query_tool.invoke(query)
        return result
    except StopIteration: # If the tool is not found
        raise ValueError("sql_db_query tool not found")
    except Exception as e:
        raise Exception(f"SQL query execution error: {e}") # Re-raise the exception for FastAPI to handle


chat_history: List[Dict[str, str]] = []
def process_chat_query(graph: StateGraph, input_message: str) -> dict:
    """Processes a query using the chat model."""
    chat_history.append({"role": "user", "content": input_message})

    output_string = None
    for event in graph.stream({"messages": [input_message]}, stream_mode="values"):
        output_string = event.get("messages", [])[-1]  # Safer extraction

    if not output_string:
        return {"result": "", "relevant_answer": "", "chat_history": chat_history}

    try:
        # Extract the content value
        match = re.search(r"content=(['\"])(.*?)\1 additional_kwargs", str(output_string))
        relevant_answer = match.group(2) if match else ""

        # Append assistant response only if there's a valid output
        chat_history.append({"role": "assistant", "content": relevant_answer})

        return {
            "result": str(output_string),
            "relevant_answer": relevant_answer,
            "chat_history": chat_history
        }
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


  
