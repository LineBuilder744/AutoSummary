from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Form
import httpx
import json
import sys
import base64
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ai_prompts.config import config

class AIRequest(BaseModel):
    text: str
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    num_questions: int = 5
    language: str = "auto"


class AIResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]

async def make_prompt(payload: dict):
    api_url = config['api_url']
    api_token = config['api_token']

    # Составляем URL с API-ключом
    full_url = f"{api_url}?key={api_token}"
    
    # Настройка заголовков
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Python version: {sys.version}")
    print(f"HTTPX version: {httpx.__version__}")
    
    try:
        # Более надежная конфигурация клиента с увеличенными таймаутами
        async with httpx.AsyncClient(
            timeout=60.0,
            verify=True,
            follow_redirects=True
        ) as client:
            print(f"Sending request to {api_url}")
            print(f"API Token (first 5 chars): {api_token[:5]}...")
            print(f"Headers: {headers}")
            print(f"Payload type: {type(payload).__name__}")
            
            response = await client.post(full_url, json=payload, headers=headers)
            
            # Логирование статуса и данных ответа для отладки
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            # Извлечение сгенерированного текста из ответа AI
            generated_text = ""
            if "candidates" in result and len(result["candidates"]) > 0:
                for part in result["candidates"][0].get("content", {}).get("parts", []):
                    if "text" in part:
                        generated_text += part["text"]
            
            if not generated_text and "error" in result:
                error_message = result.get("error", {}).get("message", "Unknown error")
                error_code = result.get("error", {}).get("code", 500)
                
                # Handle specific error cases
                if error_code == 400 and "location" in error_message.lower():
                    raise HTTPException(
                        status_code=400,
                        detail="The Gemini API is not available in your current location. Please try using a VPN or check if the API is available in your region."
                    )
                elif error_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid API key. Please check your API key configuration."
                    )
                else:
                    raise HTTPException(
                        status_code=error_code,
                        detail=f"AI API error: {error_message}"
                    )
            
            return AIResponse(response=generated_text, raw_response=result)
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e}")
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
        
        # Try to parse the error response
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", str(e))
            if "location" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="The Gemini API is not available in your current location. Please try using a VPN or check if the API is available in your region."
                )
        except:
            pass
            
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI API error: {e.response.text}"
        )
    except httpx.ConnectError as e:
        print(f"Connection Error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to AI API: {str(e)}"
        )
    except httpx.ConnectTimeout as e:
        print(f"Connection Timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Connection to AI API timed out: {str(e)}"
        )
    except httpx.ReadTimeout as e:
        print(f"Read Timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Reading response from AI API timed out: {str(e)}"
        )
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to AI API: {str(e)}"
        )
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw response: {response.text}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON response from AI API: {str(e)}"
        )
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error: {e}")
        print(traceback_str)
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with AI API: {str(e)}"
        )




def get_generate_payload(system_prompt, prompt):
    payload = {
        "contents": [
        
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt},
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": config['temperature'],
            "topP": config['top_p'],
            "maxOutputTokens": config['max_tokens']
        }
    }
    return payload


def get_pdf_payload(system_prompt, encoded_pdf):
    payload = {
        
        "contents": [
            
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt},
                    {
                        "inline_data": {
                            "mime_type": "application/pdf",
                            "data": encoded_pdf
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Низкая температура для более точного извлечения
            "topP": config['top_p'],
            "maxOutputTokens": config['max_tokens']
        }
    }
    return payload

def get_image_payload(system_prompt, encoded_image):
    payload = {
        
        "contents": [
            {
                "role": "model",
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "parts": [
                    {"text": "Please extract text from this image."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Низкая температура для более точного извлечения
            "topP": config['top_p'],
            "maxOutputTokens": config['max_tokens']
        }
    }
    return payload
