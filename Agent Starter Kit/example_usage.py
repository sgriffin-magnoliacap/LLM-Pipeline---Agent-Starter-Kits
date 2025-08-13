import os

from agent import build_agent, get_agent_tools

def main():
	# Build agent, preview tools
	agent = build_agent()
	print("Tools:", [t.name for t in get_agent_tools()])

	# Simple question using core model
	print("Simple question using core model")
	result = agent.invoke({"input": "In one sentence, explain what an agent is in AI."})
	print("Agent reply:", result["output"])
	print("--------------------------------")

	# Use the read webpage tool
	print("Use the read webpage tool")
	query = (
		"Read this article and extract the score, teams, and key players. "
		"Use the read_webpage tool on https://www.fox32chicago.com/sports/cubs-lose-blue-jays-5-1"
	)
	result = agent.invoke({"input": query})
	print("Web summary:\n", result["output"]) 
	print("--------------------------------")

	# Use the analyze image tool
	print("Use the analyze image tool")
	image_path = "https://catinaflat.blog/wp-content/uploads/2024/03/happy-cat.jpg"
	prompt = (
		f"Analyze this image and list notable objects. Use analyze_image with this url: {image_path}"
	)
	result = agent.invoke({"input": prompt})
	print("Image analysis:\n", result["output"]) 
	print("--------------------------------")

	# Use the analyze pdf tool
	print("Use the analyze pdf tool")
	pdf_path = "https://docs.house.gov/meetings/GO/GO00/20220929/115171/HHRG-117-GO00-20220929-SD010.pdf"
	prompt = f"Summarize this PDF and list key objects. Use analyze_pdf with this url: {pdf_path}"
	result = agent.invoke({"input": prompt})
	print("PDF analysis:\n", result["output"]) 
	print("--------------------------------")

	# Use internet search tool
	print("Use internet search tool")
	result = agent.invoke({"input": "Find recent news about the Chicago Cubs using internet_search and give me the top 3 links with one-line summaries."})
	print("Internet search:\n", result["output"]) 
	print("--------------------------------")

	# Use text summary tool
	print("Use text summary tool")
	long_text = (
		"Large language models (LLMs) are a type of AI model trained on vast amounts of text data to understand and generate human-like language. "
		"They can perform tasks such as summarization, translation, question answering, and more by predicting the next token in a sequence."
	)
	result = agent.invoke({"input": f"Summarize the following in 2 bullet points using the text_summary tool:\n\n{long_text}"})
	print("Text summary:\n", result["output"]) 
	print("--------------------------------")

	# Use calculator tool
	print("Use calculator tool")
	result = agent.invoke({"input": "What is (2 + 3) * 4? Use safe_calculate."})
	print("Calculation:", result["output"]) 
	print("--------------------------------")

	# Give it an open-ended task that will use multiple tools
	result = agent.invoke({"input": "Write me an aggregation of the most recent news stories about AI. Include a maximum of three stories, write a summary for each, and include sources. Be sure to read the webpage to generate your summary."})
	print("Weekly recap:\n", result["output"]) 

if __name__ == "__main__":
	main()


