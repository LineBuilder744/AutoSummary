from fastapi import FastAPI, HTTPException, Depends, Header
import httpx
import os
import json
import sys
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from utils.xml_utils import get_raw_test_xml, get_raw_summary_xml

app = FastAPI(title="DeepSeek AI API", description="API for interacting with DeepSeek AI")

# Path to configuration file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Function to load API key from config file
def load_api_token():
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Warning: Config file not found at {CONFIG_FILE_PATH}")
        return None
    
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
            print(f"Config loaded: {json.dumps({k: '***' if k == 'api_token' else v for k, v in config.items()})}")
            api_token = config.get('api_token')
            if not api_token:
                print("Warning: API token not found in config file")
                # Check for legacy key name
                api_token = config.get('api_key')
                if api_token:
                    print("Found token in legacy 'api_key' field - please update your config")
            return api_token
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

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

class XMLParseRequest(BaseModel):
    text: str
    tag_type: str = "test"  # Can be "test" or "summary"

class XMLParseResponse(BaseModel):
    original_text: str
    parsed_text: str

class CreateXMLRequest(BaseModel):
    content: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class XMLResponse(BaseModel):
    xml_content: str

# Old method to get API token from header - kept for backward compatibility
async def get_api_token(x_api_token: Optional[str] = Header(None)) -> str:
    # Try to get token from header first
    if x_api_token:
        print("Using API token from request header")
        return x_api_token
        
    # Otherwise load from config file
    print("No token in header, loading from config file")
    api_token = load_api_token()
    if not api_token:
        raise HTTPException(status_code=401, detail="API token not found in header or config file")
    print(f"Using API token from config file (length: {len(api_token)})")
    return api_token

@app.post("/parse_xml", response_model=XMLParseResponse)
async def parse_xml(request: XMLParseRequest):
    """
    Parse XML content by extracting text after a specified tag
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    if request.tag_type.lower() == "test":
        parsed_text = get_raw_test_xml(request.text)
    elif request.tag_type.lower() == "summary":
        parsed_text = get_raw_summary_xml(request.text)
    else:
        raise HTTPException(status_code=400, detail="Tag type must be 'test' or 'summary'")
    
    return XMLParseResponse(
        original_text=request.text,
        parsed_text=parsed_text
    )

@app.post("/generate", response_model=DeepSeekResponse)
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

@app.post("/create_summary_xml", response_model=XMLResponse)
async def create_summary_xml(request: CreateXMLRequest):
    """
    Create a summary XML structure from the provided content
    """
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    title = request.title or "Summary"
    metadata_str = ""
    if request.metadata:
        metadata_str = "".join([f'<meta name="{k}">{v}</meta>' for k, v in request.metadata.items()])
    
    xml_content = f"""
    <summary>
        <title>{title}</title>
        {metadata_str}
        <content>{request.content}</content>
    </summary>
    """
    
    return XMLResponse(xml_content=xml_content.strip())

@app.post("/create_test_xml", response_model=XMLResponse)
async def create_test_xml(request: CreateXMLRequest):
    """
    Create a test XML structure from the provided content
    """
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    title = request.title or "Test"
    metadata_str = ""
    if request.metadata:
        metadata_str = "".join([f'<meta name="{k}">{v}</meta>' for k, v in request.metadata.items()])
    
    xml_content = f"""
    <test>
        <title>{title}</title>
        {metadata_str}
        <content>{request.content}</content>
    </test>
    """
    
    return XMLResponse(xml_content=xml_content.strip())

@app.get("/")
async def root():
    return {"message": "DeepSeek AI API is running. Use /generate endpoint to interact with DeepSeek AI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 