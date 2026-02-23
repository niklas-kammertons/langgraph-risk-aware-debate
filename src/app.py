import streamlit as st
import os
import time
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path to resolve ModuleNotFoundError in some environments
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Agentic Debate | VIP Escort",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run immediately to load credentials for security gate
load_dotenv(override=True)

# --- SECURITY GATE ---
def check_password():
    """Returns `True` if the user had the correct password or is already authenticated."""
    
    # Check if already authenticated in this session
    if st.session_state.get("password_correct", False):
        return True

    # Injection of premium Security UI CSS
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        .stApp {
            background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        }

        /* Target the vertical block in the middle column to create the card effect */
        [data-testid="stVerticalBlock"] > div:has(div.stMarkdown span.lock-icon) {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 3rem;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-top: 10vh;
        }

        .lock-icon {
            font-size: 3.5rem;
            background: linear-gradient(135deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            display: block;
        }

        .login-title {
            font-family: 'Outfit', sans-serif;
            color: #f8fafc;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }

        .login-subtitle {
            font-family: 'Outfit', sans-serif;
            color: #94a3b8;
            font-size: 1rem;
            margin-bottom: 2.5rem;
            font-weight: 300;
        }

        /* Hide Streamlit elements during login */
        [data-testid="stSidebar"], [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Premium Button styling */
        .stButton button {
            width: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
            border: none !important;
            padding: 0.6rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    def password_entered():
        if st.session_state["password_input"] == os.environ.get("APP_PASSWORD", "demo123"):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False
            st.session_state["login_error"] = True

    # Check for authentication
    if not st.session_state.get("password_correct", False):
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.markdown('<span class="lock-icon">🛡️</span>', unsafe_allow_html=True)
            st.markdown('<div class="login-title">Security Gate</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Agentic Debate | VIP Escort Framework</div>', unsafe_allow_html=True)
            
            st.text_input(
                "Access Password", 
                type="password", 
                on_change=password_entered, 
                key="password_input",
                placeholder="Enter password..."
            )
            
            if st.session_state.get("login_error"):
                st.error("Invalid access credentials.")
        return False
    return True

if not check_password():
    st.stop()

# Dark, Premium Aesthetic CSS overrides
st.markdown("""
<style>
    /* Global Typography & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19; /* Deep Space Slate */
        color: #e2e8f0;
    }
    
    /* Header Gradient */
    .sd-header {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0rem;
    }
    .sd-subheader {
        color: #94a3b8;
        font-weight: 400;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }

    /* Expanding Cards Customization */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
    }
    .streamlit-expanderContent {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid #334155 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Input Area Styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Button explicitly prevent text wrapping */
    .stButton button {
        white-space: nowrap !important;
        min-width: fit-content !important;
    }
    
    /* Custom Alert for Human Escalation */
    .sd-alert-human {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.2) 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #f8fafc;
        font-weight: 600;
    }
    
    /* Custom Verdict tags */
    .verdict-pass { color: #10b981; font-weight: bold; }
    .verdict-fail { color: #ef4444; font-weight: bold; }
    .verdict-ambiguous { color: #f59e0b; font-weight: bold; }
    
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# UI Layout
# ---------------------------------------------------------

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")
    os.environ["LLM_MODEL_NAME"] = st.selectbox(
        "Primary LLM", 
        ["gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-1.5-pro"],
        index=0
    )
    os.environ["LLM_FALLBACK_MODEL_NAME"] = st.selectbox(
        "Fallback LLM",
        ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-pro"],
        index=0
    )
    os.environ["MAX_DEBATE_TURNS"] = str(st.slider("Max Debate Turns", min_value=1, max_value=5, value=1))
    
    st.markdown("---")
    st.markdown("**Observability**")
    st.success("✅ Langfuse Tracing Active")
    st.markdown("Session ID: `vip_ticket_luxury_001`")
    trace_link_container = st.empty()
    if "trace_url" in st.session_state:
        trace_link_container.markdown(f"[🔗 View Trace in Langfuse]({st.session_state.trace_url})")




# --- INITIALIZE GRAPH DYNAMICALLY ---
# Note: load_dotenv() already called at top for security gate
from langfuse.langchain import CallbackHandler

# Force reload graph module so it catches the new updated os.environ vars set by the UI
if "src.graph" in sys.modules:
    importlib.reload(sys.modules["src.graph"])
from src.graph import graph, load_prompt
langfuse_handler = CallbackHandler()
# ------------------------------------

# Main Stage
st.markdown('<h1 class="sd-header">Agentic Debate Validator</h1>', unsafe_allow_html=True)
st.markdown('<div class="sd-subheader">VIP E-commerce Escort Framework</div>', unsafe_allow_html=True)

# Load the exact customer input used in demo.ipynb
default_input = load_prompt("input_client.txt")

st.markdown("### 📥 Customer Signal Input")
query = st.text_area("High-Value Ticket Content:", value=default_input, height=180)

run_button = st.button("🚀 Execute Engine", type="primary", use_container_width=False)

# ---------------------------------------------------------
# Execution Logic
# ---------------------------------------------------------
if run_button:
    st.divider()
    st.markdown("### 🧠 Execution Trace")
    
    # State tracking setup
    config = {
        "configurable": {"thread_id": "vip_ticket_luxury_001"}, 
        "callbacks": [langfuse_handler]
    }
    
    # Pre-capture the trace URL (if possible) or wait for first event
    # For Langfuse CallbackHandler, trace ID might only be assigned after a run starts.
    # We will try to fetch it, but gracefully fallback if the trace doesn't exist yet.
    try:
        # In newer Langfuse versions, get_trace_url is on the client instance
        trace_url = langfuse_handler.client.get_trace_url()
        if trace_url:
            st.session_state.trace_url = trace_url
            trace_link_container.markdown(f"[🔗 View Trace in Langfuse]({trace_url})")
    except Exception as e:
        print(f"Wait for trace URL: {e}")



    
    # Progress visualization containers
    status_container = st.empty()
    trace_container = st.container()
    
    with status_container.status("Initializing State Graph...", expanded=True) as status:
        
        try:
            for event in graph.stream({"query": query}, config=config):
                # Once the graph starts, the trace is guaranteed to be created
                if "trace_url" not in st.session_state or not st.session_state.trace_url:
                    try:
                        trace_id = getattr(langfuse_handler, "last_trace_id", None)
                        if trace_id:
                            trace_url = langfuse_handler.client.get_trace_url(trace_id=trace_id)
                            st.session_state.trace_url = trace_url
                            trace_link_container.markdown(f"[🔗 View Trace in Langfuse]({trace_url})")
                    except Exception:
                        pass

                for node_name, node_state in event.items():
                    
                    # Handle interrupted states (Human-in-the-Loop Edge cases)
                    if not isinstance(node_state, dict):
                        status.update(label="⚠️ MANAGER ESCALATION REQUIRED", state="error", expanded=True)
                        with trace_container:
                            st.markdown(f'<div class="sd-alert-human">⏸️ Graph Suspended: Paused at <b>{node_name}</b> node for human review.</div>', unsafe_allow_html=True)
                        continue
                    
                    # Live update the spinner status
                    status.update(label=f"Executing Node: {node_name.upper()}...")
                    
                    with trace_container:
                        if node_name == 'draft':
                            with st.expander("📝 DRAFT NODE", expanded=False):
                                st.markdown("**Resolution Draft**")
                                st.write(node_state.get('draft', ''))
                                st.markdown("**Assumed Policies (Sources Cited)**")
                                st.write(", ".join(node_state.get('sources_cited', [])))
                                
                        elif node_name == 'attacker':
                            with st.expander("🛡️ ATTACKER NODE (Critique)", expanded=False):
                                st.markdown("*(Adversarial Evaluation)*")
                                st.markdown(node_state.get('critique', ''))
                                if node_state.get('identified_ambiguities'):
                                    st.warning("🚨 Ambiguities Identified: " + ", ".join(node_state.get('identified_ambiguities', [])))
                                    
                        elif node_name == 'defender':
                            with st.expander("⚔️ DEFENDER NODE (Rebuttal)", expanded=False):
                                st.markdown("*(Logical Defense)*")
                                st.markdown(node_state.get('defense', ''))
                                if node_state.get('concessions'):
                                    st.info("💡 Concessions: " + ", ".join(node_state.get('concessions', [])))
                                    
                        elif node_name == 'judge':
                            status.update(label="✅ Evaluation Complete", state="complete", expanded=False)
                            colA, colB = st.columns([1, 1])
                            
                            with colA:
                                with st.expander("⚖️ JUDGE SYNTHESIS", expanded=True):
                                    st.write(node_state.get('debate_synthesis', ''))
                                    
                            with colB:
                                st.markdown("#### Final Ruling")
                                verdict = node_state.get('verdict', 'UNKNOWN')
                                verdict_class = f"verdict-{verdict.lower()}"
                                st.markdown(f'<h3>Verdict: <span class="{verdict_class}">{verdict}</span></h3>', unsafe_allow_html=True)
                                
                                if node_state.get('escape_hatch_triggered', False):
                                    st.markdown('<div class="sd-alert-human">⚠️ ESCAPE HATCH TRIGGERED: High Uncertainty</div>', unsafe_allow_html=True)
                                    
                        elif node_name == 'human_escalation':
                            status.update(label="⚠️ ESCALATED TO HUMAN", state="error", expanded=True)
                            with st.expander("👤 MANAGER ESCALATION (Ramp Pattern)", expanded=True):
                                st.error(node_state.get('draft', ''))

        except Exception as e:
            status.update(label=f"❌ Graph Execution Failed", state="error", expanded=True)
            st.error(f"Error executing LangGraph nodes: {str(e)}")
            
    # Add a success toast when stream completes
    if not status_container.text == "⚠️ MANAGER ESCALATION REQUIRED":
        st.toast("Debate Framework Execution Complete!", icon="🎉")
