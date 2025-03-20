"""
정부24 API 데이터 로더
정부24 API에서 데이터를 로드하여 ChromaDB에 저장
"""

import os
import time
import traceback

import django
import requests
from django.conf import settings
from langchain.schema import Document
from tqdm import tqdm

from .common import (
    clear_collection,
    get_chroma_collection,
    get_embeddings,
    sanitize_metadata,
    save_documents_with_progress,
)

# Django 환경설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# API 설정
GOV24_BASE_URL = "https://api.odcloud.kr/api/gov24/v3"
GOV24_API_KEY = settings.GOV24_API_KEY
PAGE_SIZE = 10
API_RATE_LIMIT_DELAY = 0.5
TIMEOUT_SECONDS = 30
session = requests.Session()
