"""
app/graph.py — Pure LangGraph StateGraph definition (zero FastAPI / HTTP imports).
Exports a single `compiled_graph` instance used by WorkflowService.
"""
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

from app.models.state import AgentState
from app.nodes.entry import entry_node
from app.nodes.research import groq_generate, github_generate, sambanova_generate
from app.nodes.validation import groq_validate, github_validate, sambanova_validate
from app.nodes.consolidation import consolidation_node
from app.nodes.routing import route_groq, route_github, route_sambanova
from app.nodes.excel import excel


def build_graph():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("entry", entry_node)
    workflow.add_node("groq_generate", groq_generate)
    workflow.add_node("github_generate", github_generate)
    workflow.add_node("sambanova_generate", sambanova_generate)
    workflow.add_node("groq_validate", groq_validate)
    workflow.add_node("github_validate", github_validate)
    workflow.add_node("sambanova_validate", sambanova_validate)
    workflow.add_node("consolidate", consolidation_node)
    workflow.add_node("excel", excel)

    # Edges
    workflow.add_edge(START, "entry")

    # Fan-out from entry to 3 parallel generators
    workflow.add_edge("entry", "groq_generate")
    workflow.add_edge("entry", "github_generate")
    workflow.add_edge("entry", "sambanova_generate")

    # Generator → Validator
    workflow.add_edge("groq_generate", "groq_validate")
    workflow.add_edge("github_generate", "github_validate")
    workflow.add_edge("sambanova_generate", "sambanova_validate")

    # Conditional edges: retry or advance to consolidate
    workflow.add_conditional_edges(
        "groq_validate",
        route_groq,
        {"groq_generate": "groq_generate", "consolidate": "consolidate"},
    )
    workflow.add_conditional_edges(
        "github_validate",
        route_github,
        {"github_generate": "github_generate", "consolidate": "consolidate"},
    )
    workflow.add_conditional_edges(
        "sambanova_validate",
        route_sambanova,
        {"sambanova_generate": "sambanova_generate", "consolidate": "consolidate"},
    )

    workflow.add_edge("consolidate", "excel")
    workflow.add_edge("excel", END)

    return workflow.compile()


compiled_graph = build_graph()
