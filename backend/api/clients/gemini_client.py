import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Any
import asyncio

load_dotenv(override=True)  # Load environment variables from .env file overriding OS env variables
# Load API key from environment
api_key = os.getenv("GROQ_API_KEY")

async def stream_explanation(drug_a: str, drug_b: str, events: List[Any], enhancement: str = ""):
    """
    Expert clinical analysis using the Groq API.
    """
    if not api_key:
        yield "ERROR: GROQ_API_KEY is not set in .env"
        return

    # Prepare context
    summary = []
    for e in events[:5]:
        summary.append({
            "seriousness": e.get('seriousness', 'Unknown'),
            "reactions": ", ".join(e.get('reactions', [])[:3])
        })
        
    prompt = f"Act as a pharmacist. Analyze interactions between {drug_a} and {drug_b} given these reports: {str(summary)}. \n{enhancement}\n Provide mechanism, severity, and advice in Markdown."

    client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    try:
        response_stream = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        async for chunk in response_stream:
            # chunk.choices[0].delta.content returns the streaming word
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                await asyncio.sleep(0.01)

    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        yield f"AI Error: {str(e)}"