import os
import httpx
import json
import traceback
from fastapi import HTTPException
from dotenv import load_dotenv
from .utils import AIResponse

load_dotenv()

async def openrouter_prompt(system_prompt: str, contents) -> AIResponse:
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        # Prepare the request payload
        payload = {
            "model": os.getenv("OPENROUTER_MODEL"),  # Default model if not specified
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contents}
            ],
            "temperature": float(os.getenv("TEMPERATURE", 0.7)),
            "max_tokens": int(os.getenv("MAX_TOKENS", 1024)),
            "top_p": float(os.getenv("TOP_P", 0.9))
        }
        
        # Set up headers with API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("SITE_URL", "https://yoursite.com"),  # Required by OpenRouter
            "X-Title": os.getenv("APP_NAME", "AI Service")  # Optional but recommended
        }
        
        # Make the API request
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            # Check if the request was successful
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the response text
            response_text = response_data["choices"][0]["message"]["content"] if "choices" in response_data else ""
            
            return AIResponse(
                response=response_text,
                raw_response=response_data
            )
            
    except ValueError as ve:
        print(f"Configuration error: {ve}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"OpenRouter API configuration error: {str(ve)}"
        )
    except httpx.HTTPStatusError as he:
        print(f"HTTP error from OpenRouter API: {he}")
        traceback.print_exc()
        raise HTTPException(
            status_code=he.response.status_code,
            detail=f"OpenRouter API error: {he.response.text}"
        )
    except Exception as e:
        print(f"Error when requesting OpenRouter API: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error interacting with OpenRouter API: {str(e)}"
        )