import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from agent.settings import AGENT_CONFIG

load_dotenv()

def get_llm_for(task: str = "default", **overrides):
	"""
	Return a configured LangChain chat model for a given task using the agent's model config.
	"""
	max_retries = AGENT_CONFIG.get("max_retries", 3)

	# Resolve task config, allowing overrides
	task_cfg = AGENT_CONFIG.get(task, AGENT_CONFIG["default"]).copy()
	task_cfg.update(overrides)
	model_name = task_cfg["model_name"]

	# Lookup provider parameters for the model
	provider = (
		AGENT_CONFIG
			.get("available_models", {})
			.get(model_name, {})
			.get("provider")
	)
	temperature = (
		AGENT_CONFIG
			.get("available_models", {})
			.get(model_name, {})
			.get("temperature")
	)
	reasoning_effort = (
		AGENT_CONFIG
			.get("available_models", {})
			.get(model_name, {})
			.get("reasoning_effort")
	)
	assert provider is not None, f"No provider configured for model '{model_name}'"

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


