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
        "serviceList",
        {"page": page, "perPage": per_page, "returnType": "json"},
        base_url=GOV24_LIST_BASE_URL,
    )


def fetch_service_detail(service_id):
    """
    서비스 상세정보 API 호출
    """
    time.sleep(API_RATE_LIMIT_DELAY)
    return fetch_from_api(
        "serviceDetail",
        {"cond[서비스ID::EQ]": service_id, "returnType": "json"},
        base_url=GOV24_DETAIL_BASE_URL,
    )


def build_combined_doc(service_list_item, service_detail_item):
    """
    서비스 목록 Document 객체 생성
    """
    page_content = f"""
    서비스명: {service_list_item.get('서비스명', '정보 없음')}
    서비스목적요약: {service_list_item.get('서비스목적요약', '정보 없음')}
    서비스분야: {service_list_item.get('서비스분야', '정보 없음')}
    지원대상: {service_list_item.get('지원대상', '정보 없음')}
    지원내용: {service_list_item.get('지원내용', '정보 없음')}
    구비서류: {service_detail_item.get('구비서류', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "name": service_list_item.get("서비스명", ""),
            "subject": service_list_item.get("지원대상", ""),
            "detail": service_list_item.get("지원내용", ""),
            "link": service_list_item.get("상세조회URL", ""),
            "region": service_list_item.get("서비스분야", ""),
            "source": "정부24",
        }
    )

    return Document(page_content=page_content, metadata=metadata)


def process_and_store_combined_gov24():
    try:
        tqdm.write("=== 정부24 통합 데이터 로딩 시작 ===")

        embeddings = get_embeddings()
        collection = get_chroma_collection("gov24_services", embeddings)
        clear_collection(collection, "gov24_services")

        combined_documents = []
        page = 1
        with tqdm(desc="서비스 목록 수집", unit="건", dynamic_ncols=True) as pbar:
            while True:
                list_data = fetch_service_list(page=page, per_page=PAGE_SIZE)
                if not list_data or "data" not in list_data or not list_data["data"]:
                    break

                for service in list_data["data"]:
                    service_id = service.get("서비스ID", "")
                    if not service_id:
                        tqdm.write(
                            f"[SKIP] 서비스ID 없음 → {service.get('서비스명', '알 수 없음')}"
                        )
                        continue

                    detail_response = fetch_service_detail(service_id)
                    if (
                        detail_response
                        and "data" in detail_response
                        and detail_response["data"]
                    ):
                        detail = detail_response["data"][0]
                        combined_doc = build_combined_doc(service, detail)
                        combined_documents.append(combined_doc)

                pbar.update(len(list_data["data"]))
                page += 1
                time.sleep(API_RATE_LIMIT_DELAY)

        save_documents_with_progress(collection, combined_documents)
        tqdm.write(f"총 {len(combined_documents)}건 저장 완료")

    except Exception as e:
        tqdm.write(f"데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_combined_gov24()
