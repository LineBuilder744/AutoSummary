from fastapi import APIRouter
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from services.ai_services.ai_utils.utils import AIResponse, AIRequest
from services.ai_services.ai_utils.openrouter_prompt import openrouter_prompt
from services.ai_services.ai_utils.system_prompts import get_summary_sys_prompt, get_test_sys_prompt
# Создаем роутер для обработки запросов к /generate


router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("/summary", response_model=AIResponse)
async def generate_summary(request: AIRequest):
    
    return await openrouter_prompt(
        system_prompt=get_summary_sys_prompt(request.language),
        contents=request.text)
   
   
@router.post("/test", response_model=AIResponse)
async def generate_test(request: AIRequest):

    return await openrouter_prompt(
        system_prompt=get_test_sys_prompt(language=request.language, num_questions=request.num_questions),
        contents=request.text)
