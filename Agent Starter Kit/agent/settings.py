import os
import yaml

_here = os.path.dirname(__file__)
_config_path = os.path.join(_here, "models.yaml")

with open(_config_path, "r") as f:
	AGENT_CONFIG = yaml.safe_load(f)


