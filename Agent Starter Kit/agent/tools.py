from typing import Optional
import os
import base64
import mimetypes
import httpx
from langchain.tools import tool
from langchain_tavily import TavilySearch

from agent.factory import get_llm_for


# Helpers
def _default_headers() -> dict:
	return {
		"User-Agent": (
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
			"(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
		),
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.9",
	}


def _jina_reader_url(url: str) -> str:
	# Transform any http/https url into Jina Reader endpoint
	stripped = url.split("://", 1)[-1]
	return f"https://r.jina.ai/http://{stripped}"


def _fetch_webpage_text_with_fallback(url: str, max_chars: int) -> tuple[str, str]:
	"""
	Try fetching the webpage HTML directly with robust headers.
	On failure (401/403/network), fall back to Jina Reader to get readable text.
	Returns (text, source), where source is "direct" or "jina".
	"""
	# First attempt: direct
	try:
		headers = _default_headers()
		with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
			r = client.get(url)
			r.raise_for_status()
			text = r.text[: max(0, max_chars)]
			if text.strip():
				return text, "direct"
	except Exception:
		pass

	# Fallback: Jina Reader
	try:
		jr_url = _jina_reader_url(url)
		with httpx.Client(timeout=20.0, follow_redirects=True) as client:
			r = client.get(jr_url)
			r.raise_for_status()
			text = r.text[: max(0, max_chars)]
			return text, "jina"
	except Exception:
		return "", "error"


def _fetch_bytes_and_mime_from_url(url: str) -> tuple[bytes, Optional[str]]:
	headers = {
		"User-Agent": (
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
			"(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
		)
	}
	with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
		r = client.get(url)
		r.raise_for_status()
		content_type = r.headers.get("content-type")
		return r.content, content_type


def _load_bytes_and_mime_from_source(source: str) -> tuple[bytes, Optional[str]]:
	"""If source is URL, fetch; otherwise treat as local path and read."""
	if source.lower().startswith("http://") or source.lower().startswith("https://"):
		return _fetch_bytes_and_mime_from_url(source)
	# local file
	with open(source, "rb") as f:
		data = f.read()
	mime, _ = mimetypes.guess_type(source)
	return data, mime


@tool
def read_webpage(url: str, instruction: str, max_chars: int = 12000) -> str:
	"""
	Read a webpage and extract information per the provided instruction.
	"""
	webpage_text, source = _fetch_webpage_text_with_fallback(url, max_chars)
	if not webpage_text:
		return f"Failed to fetch webpage. URL: {url}"

	llm = get_llm_for("tool-read-webpage")
	messages = [
		{"role": "system", "content": "You are an expert web assistant. Follow the user's instruction precisely."},
		{"role": "user", "content": [{"type": "text", "text": f"Instruction:\n{instruction}\n\nSource: {source}\nURL: {url}\n\nWebpage contents:\n{webpage_text}"}]},
	]
	result = llm.invoke(messages)
	try:
		return result.content  # AIMessage
	except AttributeError:
		return str(result)


@tool
def text_summary(text: str, instruction: str) -> str:
	"""
	Summarize or transform text according to the provided instruction.
	"""
	llm = get_llm_for("tool-text-summary")
	messages = [
		{"role": "system", "content": "You are a helpful text assistant. Follow the user's instruction precisely."},
		{"role": "user", "content": [{"type": "text", "text": f"Instruction:\n{instruction}\n\nText:\n{text}"}]},
	]
	result = llm.invoke(messages)
	try:
		return result.content
	except AttributeError:
		return str(result)

@tool
def analyze_image(source: str, instruction: str) -> str:
	"""
	Analyze an image from a local path or URL (auto-converted to base64) following the given instruction.
	"""
	data, mime = _load_bytes_and_mime_from_source(source)
	if not mime:
		# Best-effort default
		mime = "image/jpeg"
	image_base64 = base64.b64encode(data).decode("ascii")
	llm = get_llm_for("tool-analyze-image")
	messages = [
		{"role": "system", "content": "You are an expert vision assistant. Follow the user's instruction precisely."},
		{
			"role": "user",
			"content": [
				{"type": "text", "text": f"Instruction:\n{instruction}"},
				{"type": "image", "source_type": "base64", "data": image_base64, "mime_type": mime},
			],
		},
	]
	result = llm.invoke(messages)
	try:
		return result.content
	except AttributeError:
		return str(result)

@tool
def analyze_pdf(source: str, instruction: str) -> str:
	"""
	Analyze a PDF from a local path or URL (auto-converted to base64) following the given instruction.
	"""
	data, mime = _load_bytes_and_mime_from_source(source)
	if not mime:
		mime = "application/pdf"
	pdf_base64 = base64.b64encode(data).decode("utf-8")
	llm = get_llm_for("tool-analyze-pdf")
	messages = [
		{"role": "system", "content": "You are an expert PDF assistant. Follow the user's instruction precisely."},
		{
			"role": "user",
			"content": [
				{"type": "text", "text": f"Instruction:\n{instruction}"},
				{"type": "file", "source_type": "base64", "mime_type": mime, "data": pdf_base64, "filename": os.path.basename(source) or "document.pdf"},
			],
		},
	]
	result = llm.invoke(messages)
	try:
		return result.content
	except AttributeError:
		return str(result)


@tool
def safe_calculate(expression: str) -> str:
	"""
	Safely evaluate a basic arithmetic expression. Supports +, -, *, /, and parentheses.
	"""
	import ast
	import operator as op

	allowed_operators = {
		ast.Add: op.add,
		ast.Sub: op.sub,
		ast.Mult: op.mul,
		ast.Div: op.truediv,
		ast.Pow: op.pow,
		ast.USub: op.neg,
	}

	def eval_node(node):
		if isinstance(node, ast.Num):
			return node.n
		if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
			return allowed_operators[type(node.op)](eval_node(node.left), eval_node(node.right))
		if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
			return allowed_operators[type(node.op)](eval_node(node.operand))
		raise ValueError("Unsupported expression")

	tree = ast.parse(expression, mode="eval")
	result = eval_node(tree.body)
	return str(result)


@tool
def internet_search(query: str, max_results: int = 5) -> str:
	"""
	Search the internet using Tavily and return top results with URLs and snippets.
	Requires TAVILY_API_KEY in the environment.
	"""
	search = TavilySearch(k=max_results)
	results = search.invoke(query)
	return results


