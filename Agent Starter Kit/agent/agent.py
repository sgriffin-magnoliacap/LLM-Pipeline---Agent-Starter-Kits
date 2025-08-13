from typing import List, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.factory import get_llm_for
from agent.tools import (
	read_webpage,
	analyze_image,
	analyze_pdf,
	text_summary,
	internet_search,
	safe_calculate,
)


def get_agent_tools():
	return [
		read_webpage,
		analyze_image,
		analyze_pdf,
		text_summary,
		internet_search,
		safe_calculate,
	]


def build_agent(system_prompt: Optional[str] = None) -> AgentExecutor:
	"""
	Create a tool-calling agent with the configured central model and the toolkit from this package.
	"""
	tools = get_agent_tools()
	llm = get_llm_for("agent-core")

	prompt = ChatPromptTemplate.from_messages([
		("system", system_prompt or (
			"You are a capable AI assistant. Use tools when helpful. "
			"When invoking any tool that uses an LLM (e.g., read_webpage, text_summary, analyze_image, analyze_pdf), "
			"always include an 'instruction' argument that clearly describes what to extract or produce. "
			"Think step-by-step. Be concise and cite sources when browsing URLs."
		)),
		("human", "{input}"),
		MessagesPlaceholder(variable_name="agent_scratchpad"),
	])

	agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
	return AgentExecutor(agent=agent, tools=tools, verbose=True)


