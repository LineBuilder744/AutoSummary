from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.openrouter_prompt import openrouter_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_text_png_sys_prompt, get_extract_png_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import convert_pdf_to_images, get_png_payload
from services.ai_services.extraction.formats.format_utils.validators import validate_file, handle_extraction_error
from services.ai_services.extraction.extraction_router import router

logger = logging.getLogger(__name__)

@router.post("/pdf", response_model=AIResponse)
async def extract_pdf(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    first_page: Optional[int] = Form(None),
    last_page: Optional[int] = Form(None),
    summarize: Optional[bool] = Form(False)
):
    try:
        validate_file(file, "pdf")
        
        if first_page is not None and last_page is not None and first_page > last_page:
            logger.warning(f"Invalid page range: first_page ({first_page}) > last_page ({last_page})")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid page range: first_page ({first_page}) cannot be greater than last_page ({last_page})"
            )
            
        # Use ternary operator for system prompt selection
        system_prompt = get_extract_png_summary_sys_prompt(language) if summarize else get_extract_text_png_sys_prompt(language)
            
        pdf_bytes = await file.read()
        images = convert_pdf_to_images(pdf_bytes=pdf_bytes, first_page=first_page, last_page=last_page)
        logger.info(f"Processing PDF with {len(images)} extracted images")
        
        return await openrouter_prompt(
            system_prompt=system_prompt,
            contents=get_png_payload(prompt="Please extract text from these pictures.", images=images),
        )
    except Exception as e:
        # Let HTTPException propagate naturally
        if isinstance(e, HTTPException):
            raise
        handle_extraction_error(e, "pdf")

