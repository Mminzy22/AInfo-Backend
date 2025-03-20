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


def fetch_from_api(endpoint, params):
    """
    API에서 데이터를 가져오는 함수
    """
    url = f"{GOV24_BASE_URL}/{endpoint}"
    params["serviceKey"] = GOV24_API_KEY
    try:
        response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return response.json()
        else:
            tqdm.write(f"API 요청 실패: {endpoint}, 상태 코드 {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        tqdm.write(f"API 요청 오류: {endpoint}, {e}")
        return None


def fetch_service_list(page=1, per_page=PAGE_SIZE):
    """
    서비스 목록 API 호출
    """
    return fetch_from_api(
        "serviceList", {"page": page, "perPage": per_page, "returnType": "json"}
    )


def fetch_service_detail(service_id):
    """
    서비스 상세정보 API 호출
    """
    time.sleep(API_RATE_LIMIT_DELAY)
    return fetch_from_api(
        "serviceDetail", {"cond[서비스ID::EQ]": service_id, "returnType": "json"}
    )


def build_service_list_doc(service):
    """
    서비스 목록 Document 객체 생성
    """
    page_content = f"""
    서비스명: {service.get('서비스명', '정보 없음')}
    서비스목적요약: {service.get('서비스목적요약', '정보 없음')}
    서비스분야: {service.get('서비스분야', '정보 없음')}
    지원대상: {service.get('지원대상', '정보 없음')}
    지원내용: {service.get('지원내용', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "서비스ID": service.get("서비스ID", ""),
            "서비스명": service.get("서비스명", ""),
            "서비스목적요약": service.get("서비스목적요약", ""),
            "상세조회URL": service.get("상세조회URL", ""),
            "서비스분야": service.get("서비스분야", ""),
        }
    )

    return Document(page_content=page_content, metadata=metadata)
