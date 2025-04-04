from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Импортируем функции для работы с XML
from utils.xml_utils import get_raw_test_xml, get_raw_summary_xml

# Создаем роутер для обработки XML запросов
router = APIRouter()

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

@router.post("/parse_xml", response_model=XMLParseResponse)
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

@router.post("/create_summary_xml", response_model=XMLResponse)
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

@router.post("/create_test_xml", response_model=XMLResponse)
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