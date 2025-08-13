# llm/tasks.py
from typing import List
import httpx
from llm.factory import get_llm_for
from pydantic import BaseModel, Field

async def analyze_text (
    text: str,
    task: str = "analyze-text",
) -> str:
    """
    Analyze text.
    """
    print(f"[{task}] Analyzing text...")

    # Define structured output
    class AnalyzeTextSchema(BaseModel):
        analysis: str = Field(description="A concise analysis of the text")

    # Built prompt and invoke LLM
    llm = get_llm_for(task).with_structured_output(AnalyzeTextSchema)
    messages = [
        {
            "role": "system",
            "content": "You are an expert in analyzing text. Given a text, return a concise analysis of the text.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Text:\n{text}\n\n Respond with a concise analysis of the text."
                },
            ],
        }
    ]
    result = llm.invoke(messages)
    return result.analysis

async def analyze_webpage (
	webpage_url: str,
    max_chars: int = 12000,
	task: str = "analyze-webpage",
) -> str:    
    """
    Analyze a webpage for information. Webpage text is truncated to max_chars to ensure token limits are not exceeded.
    """
    print(f"[{task}] Analyzing webpage...")

    # Fetch webpage text
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        r = client.get(webpage_url)
        r.raise_for_status()
        text = r.text
        webpage_text = text[:max(0, max_chars)]
    
    # Define structured output
    class AnalyzeWebpageSchema(BaseModel):
        title: str = Field(description="The title of the webpage")
        description: str = Field(description="A clear, concise description of the webpage contents and relationships")
        key_objects: List[str] = Field(default_factory=list, description="A list of notable objects/entities detected in the webpage")

    # Built prompt and invoke LLM
    llm = get_llm_for(task).with_structured_output(AnalyzeWebpageSchema)
    messages = [
        {
            "role": "system",
            "content": "You are an expert web assistant. Analyze webpages and describe key details clearly.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Analyze the webpage text in detail:\n{webpage_text}",
                },
            ],
        }
    ]
    result = llm.invoke(messages)
    return result.title, result.description, result.key_objects

async def analyze_image_url (
    image_url: str,
    task: str = "analyze-image-url",
) -> str:
    """
    Analyze an image given by a public URL using a multimodal chat model.
    """
    print(f"[{task}] Analyzing image via URL...")

    # Define structured output
    class AnalyzeImageSchema(BaseModel):
        description: str = Field(description="A clear, concise description of the image contents and relationships")
        key_objects: List[str] = Field(default_factory=list, description="A list of notable objects/entities detected in the image")

    # Built prompt and invoke LLM
    llm = get_llm_for(task).with_structured_output(AnalyzeImageSchema)
    messages = [
        {
            "role": "system",
            "content": "You are an expert vision assistant. Analyze images and describe key details clearly.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe the image in detail:",
                },
                {
                    "type": "image",
                    "source_type": "url",
                    "url": image_url,
                },
            ],
        }
    ]
    result = llm.invoke(messages)
    return result.description, result.key_objects

async def analyze_image_base64 (
	image_base64: str,
	mime_type: str, # e.g., "image/jpeg"
	task: str = "analyze-image-base64",
) -> str:
	"""
	Analyze an image given by a base64 string using a multimodal chat model.
	"""
	print(f"[{task}] Analyzing image via base64...")

	# Define structured output
	class AnalyzeImageSchema(BaseModel):
		description: str = Field(description="A clear, concise description of the image contents and relationships")
		key_objects: List[str] = Field(default_factory=list, description="A list of notable objects/entities detected in the image")

	# Built prompt and invoke LLM
	llm = get_llm_for(task).with_structured_output(AnalyzeImageSchema)
	messages = [
		{
			"role": "system",
			"content": "You are an expert vision assistant. Analyze images and describe key details clearly.",
		},
		{
			"role": "user",
			"content": [
				{
					"type": "text",
					"text": "Describe the image in detail:",
				},
				{
					"type": "image",
					"source_type": "base64",
					"data": image_base64,
					"mime_type": mime_type,
				}
			],
		}
	]
	result = llm.invoke(messages)
	return result.description, result.key_objects

async def analyze_pdf_base64 (
	pdf_base64: str,
	task: str = "analyze-pdf-base64",
) -> str:
	"""
	Analyze a PDF given by a base64 string using a multimodal chat model.
	"""
	print(f"[{task}] Analyzing PDF via base64...")

	# Define structured output
	class AnalyzePdfSchema(BaseModel):
		description: str = Field(description="A clear, concise description of the PDF contents and relationships")
		key_objects: List[str] = Field(default_factory=list, description="A list of notable objects/entities detected in the PDF")

	# Built prompt and invoke LLM
	llm = get_llm_for(task).with_structured_output(AnalyzePdfSchema)
	messages = [
		{
			"role": "system",
			"content": "You are an expert PDF assistant. Analyze PDFs and describe key details clearly.",
		},
		{
			"role": "user",
			"content": [
				{
					"type": "text",
					"text": "Describe the PDF in detail:",
				},
				{
					"type": "file",
					"source_type": "base64",
                    "mime_type": "application/pdf",
					"data": pdf_base64,
                    "filename": "my-pdf"
				}
			],
		}
	]
	result = llm.invoke(messages)
	return result.description, result.key_objects

