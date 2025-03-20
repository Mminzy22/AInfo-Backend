"""
Kstartup PDF 데이터 로더
Kstartup PDF에서 데이터를 로드하여 ChromaDB에 저장하는 파이프라인
PDF → 페이지별 추출 → 목차에서 정책명 + 페이지 매핑 → 임베딩 후 ChromaDB 저장
"""

import os
import re
import django
import fitz
from django.conf import settings
from langchain.docstore.document import Document
from tqdm import tqdm

from .common import (
    clear_collection,
    get_chroma_collection,
    get_embeddings,
    save_documents_with_progress,
)

# Django 환경설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

PDF_PATH = settings.PDF_PATH


def extract_pdf_pages(file_path):
    """
    PDF 페이지를 개별적으로 추출하여 텍스트 리스트로 반환
    """
    doc = fitz.open(file_path)
    return [page.get_text() for page in doc]
