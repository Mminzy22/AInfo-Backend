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
    prepare_metadata_for_chroma,
    sanitize_metadata,
    save_documents_with_progress,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

SEOUL_API_KEY = settings.SEOUL_API_KEY
SEOUL_BASE_URL = "http://openapi.seoul.go.kr:8088"
SERVICE_NAME = "FiftyPotalEduInfo"
DATA_TYPE = "json"
PAGE_SIZE = 500
MAX_PAGES = 4
API_RATE_LIMIT_DELAY = 1


def fetch_fifty_portal_edu_data(start_index, end_index):
    """
    서울시 열린데이터 중 50플러스포털 교육정보 API 호출 (최대 3회 재시도)
    """
    url = f"{SEOUL_BASE_URL}/{SEOUL_API_KEY}/{DATA_TYPE}/{SERVICE_NAME}/{start_index}/{end_index}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_fifty_portal_edu_data(json_data):
    """
    JSON 데이터에서 지원 사업 항목 리스트 추출
    """
    return json_data.get(SERVICE_NAME, {}).get("row", [])


def build_fifty_portal_edu_doc(item):
    """
    단일 강좌 항목을 Document로 변환
    """
    content = f"""
    강좌명: {item.get('LCT_NM', '정보 없음')}
    등록 시작일: {item.get('REG_STDE', '정보 없음')}
    등록 종료일: {item.get('REG_EDDE', '정보 없음')}
    강좌 시작일: {item.get('CR_STDE', '정보 없음')}
    강좌 종료일: {item.get('CR_EDDE', '정보 없음')}
    정원: {item.get('CR_PPL_STAT', '정보 없음')}
    강좌상태: {item.get('LCT_STAT', '정보 없음')}
    수강비용: {item.get('LCT_COST', '정보 없음')}
    상세보기: {item.get('CR_URL', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "name": item.get("LCT_NM", ""),
            "link": item.get("CR_URL", ""),
            "region": "서울시",
            "source": "50플러스포털",
        }
    )

    return Document(page_content=content, metadata=metadata)


def process_and_store_fifty_portal_edu_data():
    """
    50플러스포털 교육정보 데이터를 수집하고 저장
    """
    try:
        tqdm.write("--- 50플러스포털 교육정보 데이터 로딩 시작 ---")
        start_time = time.time()

        embeddings = get_embeddings()
        collection = get_chroma_collection("fifty_portal_edu_data", embeddings)
        clear_collection(collection, "fifty_portal_edu_data")

        all_docs = []

        # 총 건수를 파악하기 위해 1페이지만 호출해서 list_total_count 확인
        initial_json = fetch_fifty_portal_edu_data(1, 1)
        total_count = initial_json.get(SERVICE_NAME, {}).get("list_total_count", 0)
        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE
        tqdm.write(f"총 데이터 수: {total_count}건, 총 페이지 수 {total_pages}페이지")

        for page in tqdm(range(total_pages), desc="데이터 수집 중"):
            start = page * PAGE_SIZE + 1
            end = (page + 1) * PAGE_SIZE
            try:
                json_data = fetch_fifty_portal_edu_data(start, end)
                items = parse_fifty_portal_edu_data(json_data)
                docs = [build_fifty_portal_edu_doc(item) for item in items]
                all_docs.extend(docs)
            except Exception as e:
                tqdm.write(f"[ERROR] 페이지 {page + 1} 수집 실패: {e}")
            time.sleep(API_RATE_LIMIT_DELAY)

        save_documents_with_progress(collection, prepare_metadata_for_chroma(all_docs))

        elapsed = time.time() - start_time
        tqdm.write(f"\n총 {len(all_docs)}건 저장 완료. 소요 시간: {elapsed:.2f}초")

    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_fifty_portal_edu_data()
