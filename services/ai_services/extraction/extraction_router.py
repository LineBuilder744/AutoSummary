from fastapi import APIRouter
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

router = APIRouter(prefix="/extract", tags=["extract"])

# Импортируем модули с маршрутами, чтобы они зарегистрировались
from services.ai_services.extraction.formats import extract_png, extract_pdf, extract_doc
# Здесь также нужно будет импортировать extract_pdf, когда он будет создан
# from services.extraction.formats import extract_pdf
