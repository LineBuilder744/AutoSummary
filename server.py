from fastapi import FastAPI, HTTPException, Depends, Header
import httpx
import os
import json
import sys
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from utils.xml_utils import get_raw_test_xml, get_raw_summary_xml
import uvicorn

# Импортируем созданные нами модули с роутерами
from generate import router as generate_router
from xml_routes import router as xml_router

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


@app.get("/")
async def root():
    return {"message": "DeepSeek AI API is running. Available endpoints: /generate, /parse_xml, /create_summary_xml, /create_test_xml"}

# Подключаем роутеры к приложению
app.include_router(generate_router)
app.include_router(xml_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 