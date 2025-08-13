## LLM Pipeline & Agent Starter Kits

Per Anthropic, **workflows** are systems where LLMs and tools are orchestrated through predefined code paths, while **agents** are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.

This repo includes simple, batteries‑included starters to:
- call LLMs directly for common tasks (Workflow Starter Kit)
- build an agent that can use tools (Agent Starter Kit)

Both kits use a shared, YAML‑driven model configuration and environment‑based API keys. You can use OpenAI by default, optionally X.ai (Grok) models, and optionally Tavily for internet search.

## Repository layout

```
LLM Pipeline & Agent Starter Kits/
  ├─ Agent Starter Kit/
  │  ├─ agent/
  │  │  ├─ agent.py          # Builds a tool-calling agent with LangChain
  │  │  ├─ tools.py          # Tool implementations (web, image, pdf, summarize, search, calculator)
  │  │  ├─ factory.py        # Constructs chat models from YAML config
  │  │  ├─ settings.py       # Loads YAML into AGENT_CONFIG
  │  │  ├─ models.yaml       # Available models + task → model mapping
  │  │  └─ __init__.py
  │  ├─ example_assets/      # Sample files (image/pdf)
  │  └─ example_usage.py     # End-to-end agent demo
  │
  └─ Workflow Starter Kit/
     ├─ llm/
     │  ├─ tasks.py          # Async functions: analyze_text/webpage/image/pdf
     │  ├─ factory.py        # Constructs chat models from YAML config
     │  ├─ settings.py       # Loads YAML into LLM_CONFIG
     │  ├─ models.yaml       # Available models + task → model mapping
     │  └─ __init__.py
     ├─ example_assets/      # Sample files (image/pdf)
     └─ example_usage.py     # End-to-end pipeline demo
```


## Prerequisites

- Python 3.10+ recommended
- A terminal (PowerShell on Windows is fine)
- API keys (see .env below)


## Environment variables (.env)

Create a file named `.env` at the repository root with the following variables:

```
# Required for OpenAI models
OPENAI_API_KEY=your-openai-key

# Optional: only if you want to use X.ai (Grok) models
XAI_API_KEY=your-xai-key

# Optional: only if you want the agent's internet_search tool
TAVILY_API_KEY=your-tavily-key
```

Notes:
- OpenAI is used by default in both kits.
- If you switch any task to an X.ai model in `models.yaml`, set `XAI_API_KEY`.
- The `internet_search` tool in the Agent kit requires `TAVILY_API_KEY`.


## Install

From the repository root:

PowerShell (Windows):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install langchain langchain-tavily httpx pydantic python-dotenv pyyaml openai xai-sdk
```

macOS/Linux (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install langchain langchain-tavily httpx pydantic python-dotenv pyyaml openai xai-sdk
```


## How models are configured

Both kits load a YAML file to decide which model/provider to use for each task.

- Agent kit: `Agent Starter Kit/agent/models.yaml`
- Workflow kit: `Workflow Starter Kit/llm/models.yaml`

Each YAML contains:
- `available_models`: model metadata, including `provider` (e.g., `openai`, `xai`) and optional `temperature` and `reasoning_effort`.
- task sections (e.g., `agent-core`, `tool-read-webpage`, `analyze-text`) mapping each task to a `model_name` from `available_models`.

At runtime, both kits call a factory (`factory.py`) that reads the YAML and constructs a chat model via `init_chat_model(model_name, model_provider=provider, ...)`.


## Run the examples

Make sure your virtual environment is activated and `.env` is set.

- Agent demo (tool-using agent):
```powershell
python "Agent Starter Kit/example_usage.py"
```

- LLM pipeline demo (direct task calls):
```powershell
python "Workflow Starter Kit/example_usage.py"
```

What the demos do:
- Ask a simple question using the configured core model.
- Read and summarize a public webpage.
- Analyze an image (URL) and a PDF (URL and local file in the pipeline demo).
- Use internet search (Agent kit; requires `TAVILY_API_KEY`).
- Summarize text and perform a safe calculator operation (Agent kit).


## Customizing

- Change models per task: edit the relevant `models.yaml` and update the `model_name` under each task. Ensure you have the corresponding API key in `.env`.
- Add or modify tools (Agent kit): edit `Agent Starter Kit/agent/tools.py`. Tools are defined with `@tool` and can call `get_llm_for("tool-<name>")` for separate model settings.
- Add new pipeline tasks: add async functions to `Workflow Starter Kit/llm/tasks.py` and wire them to a task name in `models.yaml`.

