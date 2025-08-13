from llm.tasks import analyze_text, analyze_image_url, analyze_image_base64, analyze_webpage, analyze_pdf_base64
import base64
import httpx

async def main():
    
    # Analyze text
    analysis = await analyze_text("Hello, world!")
    print("Analysis:", analysis)

    # Analyze webpage
    example_webpage_url = "https://www.fox32chicago.com/sports/cubs-lose-blue-jays-5-1"
    title, description, key_objects = await analyze_webpage(example_webpage_url)
    print("Title:", title)
    print("Description:", description)
    print("Key objects:", key_objects)

    # Analyze image from URL
    example_image_url = "https://catinaflat.blog/wp-content/uploads/2024/03/happy-cat.jpg"
    description, key_objects = await analyze_image_url(example_image_url)
    print("Description:", description)
    print("Key objects:", key_objects)

    # Analyze image from local file
    example_image_file = "LLM Pipeline Starter Kit\example_assets\happy-cat.jpg"
    with open(example_image_file, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("ascii")
    description, key_objects = await analyze_image_base64(image_base64, "image/jpeg")
    print("Description:", description)
    print("Key objects:", key_objects)

    # Analyze PDF from local file
    example_pdf_file = "LLM Pipeline Starter Kit\example_assets\declaration-of-independence.pdf"
    with open(example_pdf_file, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
    description, key_objects = await analyze_pdf_base64(pdf_base64)
    print("Description:", description)
    print("Key objects:", key_objects)

    # Analyze PDF from URL
    example_pdf_url = "https://docs.house.gov/meetings/GO/GO00/20220929/115171/HHRG-117-GO00-20220929-SD010.pdf"
    pdf_base64 = base64.b64encode(httpx.get(example_pdf_url).content).decode("utf-8")
    description, key_objects = await analyze_pdf_base64(pdf_base64)
    print("Description:", description)
    print("Key objects:", key_objects)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())