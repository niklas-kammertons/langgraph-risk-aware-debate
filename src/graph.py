import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path

# Load settings
MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gemini-3-flash-preview")
FALLBACK_MODEL_NAME = os.environ.get("LLM_FALLBACK_MODEL_NAME", "gemini-2.5-flash")
MAX_DEBATE_TURNS = int(os.environ.get("MAX_DEBATE_TURNS", 1))
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def get_llm(schema):
    """Initializes LLM with structured outputs and an automatic fallback model for rate limits."""
    primary_llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0, max_retries=3).with_structured_output(schema)
    fallback_llm = ChatGoogleGenerativeAI(model=FALLBACK_MODEL_NAME, temperature=0, max_retries=3).with_structured_output(schema)
    return primary_llm.with_fallbacks([fallback_llm])


def load_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r") as f:
        return f.read().strip()

# Pydantic Output Schemas
class DraftResponse(BaseModel):
    draft: str = Field(description="The polite, professional resolution drafted for the customer.")
    sources_cited: list[str] = Field(description="List of assumed policies or best-practices relied upon to create this draft.")

class CritiqueResponse(BaseModel):
    critique: str = Field(description="Adversarial evaluation finding policy policy violations, promise gaps, or tone issues.")
    identified_ambiguities: list[str] = Field(description="Any vague, subjective, or unclear points in the draft that create brand or financial risk.")

class DefenseResponse(BaseModel):
    defense: str = Field(description="Point-by-point rebuttal defending the draft using logic and customer-experience principles.")
    concessions: list[str] = Field(description="Valid points from the critique that the defense acknowledges as true weaknesses.")

class JudgeResponse(BaseModel):
    debate_synthesis: str = Field(description="Step-by-step synthesis of the debate, weighing the severe risks against the defense's logic.")
    escape_hatch_triggered: bool = Field(description="True ONLY if the debate reveals high uncertainty, unresolved ambiguity, or requires a manager's subjective judgment.")
    verdict: Literal["PASS", "FAIL", "AMBIGUOUS"] = Field(description="The final categorical verdict.")

def concat_strings(left: str, right: str) -> str:
    """Reducer function to accumulate strings in the state."""
    if not left:
        return right
    if not right:
        return left
    return left + right


class TicketState(TypedDict):
    query: str
    draft: str
    sources_cited: list[str]
    critique: Annotated[str, concat_strings]
    identified_ambiguities: list[str]
    defense: Annotated[str, concat_strings]
    concessions: list[str]
    debate_synthesis: str
    escape_hatch_triggered: bool
    verdict: str  # "PASS", "FAIL", "AMBIGUOUS"
    turn_count: int


# The Nodes (The Instacart LACE Debate)
def draft_node(state: TicketState):
    llm = get_llm(DraftResponse)
    sys_msg = SystemMessage(content=load_prompt("draft_prompt.md"))
    response = llm.invoke([sys_msg, HumanMessage(content=state.get("query", ""))])
    return {
        "draft": response.draft,
        "sources_cited": response.sources_cited,
        "critique": "",             # Wipe constraints on new draft
        "identified_ambiguities": [],
        "defense": "",
        "concessions": [],
        "turn_count": 0             # Reset multi-turn counter
    }

def attacker_node(state: TicketState):
    """Instacart Principle: The Skeptic"""
    llm = get_llm(CritiqueResponse)
    sys_msg = SystemMessage(content=load_prompt("attacker_prompt.md"))
    
    # Allow Auditor to see previous rounds if multi-turn
    turn = state.get("turn_count", 0) + 1
    recent_defense = state.get("defense", "")
    
    prompt_content = f"Draft to Attack: {state.get('draft', '')}"
    if turn > 1 and recent_defense:
       prompt_content += f"\n\nPrevious round's Defense to rebut: {recent_defense}"
        
    response = llm.invoke([sys_msg, HumanMessage(content=prompt_content)])
    
    # Accumulate history by returning just the new chunk (LangGraph operator.add handles the appending)
    new_critique_text = f"--- Round {turn} Critique ---\n{response.critique}\n\n"
    historical_ambiguities = state.get("identified_ambiguities", []) + response.identified_ambiguities
    
    return {
        "critique": new_critique_text,
        "identified_ambiguities": historical_ambiguities
    }

def defender_node(state: TicketState):
    """Instacart Principle: The Supporter"""
    llm = get_llm(DefenseResponse)
    sys_msg = SystemMessage(content=load_prompt("defender_prompt.md"))
    turn = state.get("turn_count", 0) + 1
    
    # We only feed the FULL accumulated critique history so the defender knows what to answer
    response = llm.invoke([sys_msg, HumanMessage(content=f"Draft: {state.get('draft', '')}\nCritique History: {state.get('critique', '')}")])
    
    # Accumulate history by returning just the new chunk (LangGraph operator.add handles the appending)
    new_defense_text = f"--- Round {turn} Defense ---\n{response.defense}\n\n"
    historical_concessions = state.get("concessions", []) + response.concessions
    
    return {
        "defense": new_defense_text,
        "concessions": historical_concessions,
        "turn_count": turn
    }

def judge_node(state: TicketState):
    """The Final Arbiter + Ramp Uncertainty Principle"""
    llm = get_llm(JudgeResponse)
    sys_msg = SystemMessage(content=load_prompt("judge_prompt.md"))
    debate_text = (
        f"Draft: {state.get('draft', '')}\n"
        f"Sources Cited: {state.get('sources_cited', [])}\n\n"
        f"Critique: {state.get('critique', '')}\n"
        f"Identified Ambiguities: {state.get('identified_ambiguities', [])}\n\n"
        f"Defense: {state.get('defense', '')}\n"
        f"Concessions: {state.get('concessions', [])}"
    )
    response = llm.invoke([sys_msg, HumanMessage(content=debate_text)])
    return {
        "debate_synthesis": response.debate_synthesis,
        "escape_hatch_triggered": response.escape_hatch_triggered,
        "verdict": response.verdict
    }

def human_escalation_node(state: TicketState):
    """Ramp Principle: Safe Escape Hatch"""
    return {"draft": "[SYSTEM: Escalated to Human Manager due to ambiguity.]"}

# Routing Logic
def route_verdict(state: TicketState):
    if state.get("verdict") == "PASS":
        return END
    elif state.get("verdict") == "FAIL":
        return "draft" # Loop back and try again
    else:  # AMBIGUOUS
        return "human_escalation"

def route_debate(state: TicketState):
    """Multi-turn loop router"""
    if state.get("turn_count", 0) < MAX_DEBATE_TURNS:
        return "attacker"
    return "judge"

# Build the Graph
builder = StateGraph(TicketState)
builder.add_node("draft", draft_node)
builder.add_node("attacker", attacker_node)
builder.add_node("defender", defender_node)
builder.add_node("judge", judge_node)
builder.add_node("human_escalation", human_escalation_node)

# Flow
builder.set_entry_point("draft")
builder.add_edge("draft", "attacker")
builder.add_edge("attacker", "defender")
builder.add_conditional_edges(
    "defender",
    route_debate,
    {"attacker": "attacker", "judge": "judge"}
)
builder.add_conditional_edges(
    "judge", 
    route_verdict, 
    {END: END, "draft": "draft", "human_escalation": "human_escalation"}
)
builder.add_edge("human_escalation", END)

# Compile with Checkpointer for Human-in-the-Loop
memory = InMemorySaver()
# interrupt_before pauses the graph right before the human escalation node
graph = builder.compile(checkpointer=memory, interrupt_before=["human_escalation"])
