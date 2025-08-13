# llm/factory.py
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from llm.settings import LLM_CONFIG

load_dotenv()

def get_llm_for(task: str = "default", **overrides):
    """
    Get langchain chat model for a given task
    """
    # Get max retries
    max_retries = LLM_CONFIG.get("max_retries", 3)
    
    # Get task config
    task_cfg = LLM_CONFIG.get(task, LLM_CONFIG["default"]).copy()    
    task_cfg.update(overrides)
    model_name = task_cfg["model_name"]
    
    # Lookup provider/temperature/reasoning_effort for the task's model
    provider = (
        LLM_CONFIG
        .get("available_models", {})
        .get(model_name, {})
        .get("provider")
    )
    temperature = (
        LLM_CONFIG
        .get("available_models", {})
        .get(model_name, {})
        .get("temperature")
    )
    reasoning_effort = (
        LLM_CONFIG
        .get("available_models", {})
        .get(model_name, {})
        .get("reasoning_effort")
    )
    assert provider is not None, f"No provider configured for model '{model_name}'"

    # Return model with reasoning_effort if provided, otherwise return model without reasoning_effort (and multimodal if provided)
    if reasoning_effort:
        return init_chat_model(
            model_name,
            model_provider=provider,
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_retries=max_retries,
        )
    else:
        return init_chat_model(
            model_name,
            model_provider=provider,
            temperature=temperature,
            max_retries=max_retries,
        )