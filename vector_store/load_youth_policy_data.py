"""
청년정책 API 데이터 로더
API에서 청년정책 데이터를 로드하여 ChromaDB에 저장
"""

import math
import os
import time
import traceback

import django
import requests
from django.conf import settings
from langchain.schema import Document
from tqdm import tqdm

from .common import (
    get_chroma_collection,
    get_embeddings,
    prepare_metadata_for_chroma,
    save_documents_with_progress,
    sanitize_metadata,
)

# Django 환경설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# API 설정
YOUTH_API_BASE_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
YOUTH_POLICY_API_KEY = settings.YOUTH_POLICY_API_KEY
PAGE_SIZE = 10
API_RATE_LIMIT_DELAY = 1


def fetch_api(params, url=YOUTH_API_BASE_URL):
    """
    청년정책 API 호출 (최대 3회 재시도)
    """
    for _ in range(3):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            tqdm.write(f"API 요청 오류: {e}")
        time.sleep(2)
    return None
