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
GOV24_LIST_BASE_URL = "https://api.odcloud.kr/api/gov24/v3"
GOV24_DETAIL_BASE_URL = "https://api.odcloud.kr/api/gov24/v3"
GOV24_API_KEY = settings.GOV24_API_KEY
PAGE_SIZE = 10
API_RATE_LIMIT_DELAY = 0.5
TIMEOUT_SECONDS = 30
session = requests.Session()


def fetch_from_api(endpoint, params, base_url):
    """
    API에서 데이터를 가져오는 함수
    """
    url = f"{base_url}/{endpoint}"
    params["serviceKey"] = GOV24_API_KEY
    for attempt in range(2):  # 1회 재시도 포함 (총 2회 시도)
        try:
            response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                return response.json()
            else:
                tqdm.write(
                    f"API 요청 실패: {endpoint}, 상태 코드 {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            tqdm.write(f"API 요청 오류: {endpoint}, {e}")
        time.sleep(1)  # 재시도 전 대기
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


def build_service_detail_doc(service):
    """
    서비스 상세정보 Document 객체 생성
    """
    page_content = f"""
    서비스명: {service.get('서비스명', '정보 없음')}
    서비스목적: {service.get('서비스목적', '정보 없음')}
    서비스분야: {service.get('서비스분야', '정보 없음')}
    지원대상: {service.get('지원대상', '정보 없음')}
    지원내용: {service.get('지원내용', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "서비스ID": service.get("서비스ID", ""),
            "서비스명": service.get("서비스명", ""),
            "신청기한": service.get("신청기한", ""),
            "선정기준": service.get("선정기준", ""),
            "온라인신청사이트URL": service.get("온라인신청사이트URL", ""),
        }
    )

    return Document(page_content=page_content, metadata=metadata)


def process_and_store_gov24_data():
    """
    전체 데이터 수집 및 저장 파이프라인
    """
    try:
        tqdm.write("=== 정부24 데이터 로딩 시작 ===")

        embeddings = get_embeddings()
        service_list_db = get_chroma_collection("gov24_service_list", embeddings)
        service_detail_db = get_chroma_collection("gov24_service_detail", embeddings)
        clear_collection(service_list_db, "gov24_service_list")
        clear_collection(service_detail_db, "gov24_service_detail")

        list_documents = []
        page = 1
        with tqdm(desc="서비스 목록 수집 진행", unit="건", dynamic_ncols=True) as pbar:
            while True:
                page_data = fetch_service_list(page=page, per_page=PAGE_SIZE)
                if not page_data or "data" not in page_data or not page_data["data"]:
                    break
                for service in page_data["data"]:
                    list_documents.append(build_service_list_doc(service))
                pbar.update(len(page_data["data"]))
                page += 1
                time.sleep(API_RATE_LIMIT_DELAY)

        detail_documents = []
        for doc in tqdm(
            list_documents, desc="상세 정보 수집 진행", unit="건", dynamic_ncols=True
        ):
            service_id = doc.metadata.get("서비스ID", "")
            detail_data = fetch_service_detail(service_id)
            if detail_data and "data" in detail_data and detail_data["data"]:
                service_detail = detail_data["data"][0]
                detail_documents.append(build_service_detail_doc(service_detail))

        save_documents_with_progress(service_list_db, list_documents)
        save_documents_with_progress(service_detail_db, detail_documents)

        tqdm.write("총 데이터 저장 완료")
    except Exception as e:
        tqdm.write(f"데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_gov24_data()
