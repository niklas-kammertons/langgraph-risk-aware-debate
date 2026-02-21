# Agentic Debate & Defer Framework

A production-grade LangGraph architecture designed for high-risk customer support and compliance scenarios. 

This repository implements advanced cognitive architecture patterns, specifically an **Online Agentic Debate** (inspired by Instacart's LACE) and **Epistemic Humility/Human-in-the-Loop routing** (inspired by Ramp).

## 🚀 Features
* **Agentic Debate:** A multi-node StateGraph that generates drafts, critiques them (Attacker), defends them (Defender), and judges the outcome.
* **Structured Outputs:** Strict enforcement of LLM outputs using Pydantic models mapped to a LangGraph `TypedDict` state.
* **Safe Execution:** Utilizes LangGraph's Checkpointer (`interrupt_before`) to pause execution and route to a human manager if the Judge detects high ambiguity or policy risk.
* **Full Observability:** Deeply integrated with Langfuse to trace every token, cost, and sub-graph execution.
* **Cost Optimized:** Configured for `gemini-3-flash-preview` to run high-speed, low-cost internal debate loops, protecting unit economics.

## 🛠️ Quickstart

1. **Clone and setup environment:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   conda env create -f environment.yml
   conda activate langgraph-demo
   ```

2. **Configure API Keys:**
   Copy the example environment file and add your Google Gemini and Langfuse keys.
   ```bash
   cp .env.example .env
   ```

3. **Run the Interactive Demo:**
   Launch Jupyter Lab and open `demo.ipynb`. The notebook is heavily documented and designed to be a "one-click run" to watch the debate unfold in real-time.
   ```bash
   jupyter lab
   ```

## 📁 Repository Structure
* `prompts/`: Contains the modular, role-based Markdown instructions for the Agent, Attacker, Defender, and Judge.
* `src/graph.py`: The core LangGraph state machine, Pydantic schemas, and LLM node definitions.
* `demo.ipynb`: The interactive execution environment and graph visualization.
