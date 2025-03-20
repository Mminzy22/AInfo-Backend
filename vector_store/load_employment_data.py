"""
고용정보 API 데이터 로더
고용24 구직자취업역량강화프로그램 API에서 데이터를 로드하여 ChromaDB에 저장
"""

import os
import time
import traceback
import xml.etree.ElementTree as ET

import django
import requests
from django.conf import settings
from langchain.schema import Document
from tqdm import tqdm

from .common import (
    clear_collection,
    get_chroma_collection,
    get_embeddings,
    prepare_metadata_for_chroma,
    save_documents_with_progress,
    sanitize_metadata,
)

# Django 설정 로드
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# API 설정
EMPLOYMENT_API_URL = (
    "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo217L01.do"
)
EMPLOYMENT_API_KEY = settings.EMPLOYMENT_API_KEY
MAX_PAGES = 10000
PAGE_SIZE = 10
API_RATE_LIMIT_DELAY = 1
