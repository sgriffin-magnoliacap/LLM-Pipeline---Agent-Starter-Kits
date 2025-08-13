# llm/settings.py
import os
import yaml

# Load the model configuration
_here = os.path.dirname(__file__)
_config_path = os.path.join(_here, "models.yaml")
with open(_config_path, "r") as f:
    LLM_CONFIG = yaml.safe_load(f)
