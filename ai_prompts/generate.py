from fastapi import APIRouter
from ai_prompts.config import *
from ai_prompts.make_prompt import *
from ai_prompts.utils import *
from db.db_manager import *
# Создаем роутер для обработки запросов к /generate

router = APIRouter()


@router.post("/generate_summary", response_model=AIResponse)
async def generate_summary(request: AIRequest):
    return await make_prompt(system_prompt=get_summaty_sys_prompt(request.language), contents=request.text)
   
   
@router.post("/generate_test", response_model=AIResponse)
async def generate_test(request: AIRequest):
    return await make_prompt(system_prompt=get_test_sys_prompt(language=request.language, num_questions=request.num_questions), contents=request.text)
