from typing import Literal

from langchain.messages import AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from prompt import check_query_system_prompt, generate_query_system_prompt
from model import model
from tools import tools

get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
get_schema_node = ToolNode([get_schema_tool], name = "get_scema")

run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
run_query_node = ToolNode([run_query_tool],name="run_qeury")


def list_tables(state:MessagesState):
    tool_call = {
        "name" : "sql_db_list_tables",
        "args" : {},
        "id" : "abc123",
        "type": "tool_call"
    }
    tool_call_message = AIMessage(content="", tool_calls = [tool_call])

    list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available tables{tool_message.content}")

    return {"messages": [tool_call_message, tool_call_message, response]}


def call_get_schema (state : MessagesState):
    llm_with_tools = model.bind_tools([get_schema_tool], tool_choice = "any")
    response = llm_with_tools.invoke(state["messages"])

    return {"messages":[response]}


def generate_query(state: MessagesState):
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt
    }

    llm_with_tools = model.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message]+state["messages"])

    return {"messages": [response]}

def check_query(state:MessagesState):
    system_message = {
        "role": "system",
        "content" : check_query_system_prompt
    }

    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {
        "role":"user",
        "content": tool_call["args"]["query"]
    }
    llm_with_tools = model.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message,user_message])

    return {"messages":[response]}