from fastapi import APIRouter
from prompts.config import *
from .generate_patterns import get_summary_sys_prompt, get_test_sys_prompt
from prompts.utils import AIRequest, AIResponse
# Создаем роутер для обработки запросов к /generate

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("/summary", response_model=AIResponse)
async def generate_summary(request: AIRequest):
    
    return await make_prompt(
        system_prompt=get_summary_sys_prompt(request.language),
        contents=request.text)
   
   
@router.post("/test", response_model=AIResponse)
async def generate_test(request: AIRequest):

    return await make_prompt(
        system_prompt=get_test_sys_prompt(language=request.language, num_questions=request.num_questions),
        contents=request.text)
