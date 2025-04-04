from fastapi import APIRouter, HTTPException, Depends, Header
import httpx
import json
import sys
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Создаем роутер для обработки запросов к /generate
router = APIRouter()

class DeepSeekRequest(BaseModel):
    prompt: str
    model: str = "deepseek-chat"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.95
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None

class DeepSeekResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]

async def get_api_token(x_api_token: str = Header(...)) -> str:
    if not x_api_token:
        raise HTTPException(status_code=401, detail="API token is required")
    return x_api_token

@router.post("/generate", response_model=DeepSeekResponse)
async def generate_response(request: DeepSeekRequest, api_token: str = Depends(get_api_token)):
    """
    Generate a response from DeepSeek AI using the provided prompt
    """
    # DeepSeek API endpoint
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    # Prepare the request payload
    payload = {
        "model": request.model,
        "messages": [{"role": "user", "content": request.prompt}],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": request.stream
    }
    
    # Add any additional parameters if provided
    if request.additional_params:
        payload.update(request.additional_params)
    
    # Set up headers with the API token
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Python version: {sys.version}")
    print(f"HTTPX version: {httpx.__version__}")
    
    try:
        # More robust client configuration with increased timeouts
        async with httpx.AsyncClient(
            timeout=60.0,
            verify=True,
            follow_redirects=True
        ) as client:
            print(f"Sending request to {api_url}")
            print(f"API Token (first 5 chars): {api_token[:5]}...")
            print(f"Headers: {headers}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(api_url, json=payload, headers=headers)
            
            # Log the response status and data for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated text from the response
            generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return DeepSeekResponse(response=generated_text, raw_response=result)
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e}")
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, 
                           detail=f"DeepSeek API error: {e.response.text}")
    except httpx.ConnectError as e:
        print(f"Connection Error: {e}")
        raise HTTPException(status_code=503, 
                           detail=f"Unable to connect to DeepSeek API: {str(e)}")
    except httpx.ConnectTimeout as e:
        print(f"Connection Timeout: {e}")
        raise HTTPException(status_code=504, 
                           detail=f"Connection to DeepSeek API timed out: {str(e)}")
    except httpx.ReadTimeout as e:
        print(f"Read Timeout: {e}")
        raise HTTPException(status_code=504, 
                           detail=f"Reading response from DeepSeek API timed out: {str(e)}")
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        raise HTTPException(status_code=500, 
                           detail=f"Error connecting to DeepSeek API: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, 
                           detail=f"Invalid JSON response from DeepSeek API: {str(e)}")
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error: {e}")
        print(traceback_str)
        raise HTTPException(status_code=500, 
                           detail=f"Error communicating with DeepSeek API: {str(e)}") 