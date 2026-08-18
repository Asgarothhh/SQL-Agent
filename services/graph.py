from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph, MessagesState

from services.nodes import list_tables,call_get_schema,get_schema_node ,generate_query,check_query, run_query_node



def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
    message = state["messages"]
    last_message = message[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"


builder = StateGraph(MessagesState)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node("get_schema", get_schema_node)
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node("run_query", run_query_node)

builder.add_edge(START, "list_tables")
builder.add_edge("list_tables","call_get_schema")
builder.add_edge("call_get_schema","get_schema")
builder.add_edge("get_schema", "generate_query")
builder.add_conditional_edges(
    "generate_query",
    should_continue
)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")

agent = builder.compile()
