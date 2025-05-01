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
SERVICE_NAME = "VwSmpBizInfo"
DATA_TYPE = "json"
PAGE_SIZE = 500
MAX_PAGES = 4
API_RATE_LIMIT_DELAY = 1


def fetch_mongddang_api(start_index, end_index):
    """ "
    서울시 공공데이터 중 몽땅정보 만능키 API 호출 (최대 3회 재시도)
    몽땅정보는 임신·출산·육아 사업 정보를 제공합니다.
    """
    url = f"{SEOUL_BASE_URL}/{SEOUL_API_KEY}/{DATA_TYPE}/{SERVICE_NAME}/{start_index}/{end_index}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_mongddang_data(json_data):
    """
    JSON 데이터에서 지원 사업 항목 리스트 추출
    """
    return json_data.get(SERVICE_NAME, {}).get("row", [])


def build_mongddang_doc(item):
    """
    단일 항목을 Document로 변환
    """
    # 사업명: {item.get('BIZ_NM', '정보 없음')}
    # 사업대분류: {item.get('BIZ_LCLSF_NM', '정보 없음')}
    # 사업중분류: {item.get('BIZ_MCLSF_NM', '정보 없음')}
    # 사업소분류: {item.get('BIZ_SCLSF_NM', '정보 없음')}
    # 사업내용: {item.get('BIZ_CN', '정보 없음')}
    # 이용대상: {item.get('UTZTN_TRPR_CN', '정보 없음')}
    # 대상지역: {item.get('TRGT_RGN', '정보 없음')}
    # 자세히보기: {item.get('DEVIW_SITE_ADDR', '정보 없음')}
    # 신청주소: {item.get('APLY_SITE_ADDR', '정보 없음')}
    page_content = f"""
    정책명/강좌명: {item.get('BIZ_NM', '정보 없음')}
    정책/강좌 내용: {item.get('BIZ_CN', '정보 없음')}
    지원 대상: {item.get('UTZTN_TRPR_CN', '정보 없음')}
    카테고리/분야: {item.get('BIZ_LCLSF_NM', '정보 없음')}
    지역: {item.get('TRGT_RGN', '정보 없음')}
    시작일: 정보 없음
    종료일: 정보 없음
    접수방법: {item.get('APLY_SITE_ADDR', '정보 없음')}
    문의처: {item.get('AREF_CN', '정보 없음')}
    상세보기 링크: {item.get('DEVIW_SITE_ADDR', '정보 없음')}
    구비서류: 정보 없음
    """.strip()

    metadata = sanitize_metadata(
        {
            "name": item.get("BIZ_NM", ""),
            "subject": item.get("UTZTN_TRPR_CN", ""),
            "detail": item.get("BIZ_CN", ""),
            "link": item.get("DEVIW_SITE_ADDR", ""),
            "region": item.get("TRGT_RGN", ""),
            "source": "몽땅정보",
        }
    )

    return Document(page_content=page_content, metadata=metadata)


def process_and_store_mongddang_data():
    """
    몽땅정보 데이터를 수집하고 저장
    """
    try:
        tqdm.write("--- 몽땅정보 데이터 로딩 시장 ---")
        start_time = time.time()

        embeddings = get_embeddings()
        mongddang_collection = get_chroma_collection("mongddang_data", embeddings)
        unified_collection = get_chroma_collection("unified_data", embeddings)

        # 기존 데이터 초기화
        clear_collection(mongddang_collection, "mongddang_data")

        all_docs = []

        # 총 건수를 파악하기 위해 1페이지만 호출해서 list_total_count 확인
        initial_json = fetch_mongddang_api(1, 1)
        total_count = initial_json.get(SERVICE_NAME, {}).get("list_total_count", 0)
        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE
        tqdm.write(f"총 데이터 수: {total_count}건, 총 페이지 수 {total_pages}페이지")

        for page in tqdm(range(total_pages), desc="데이터 수집 중"):
            start = page * PAGE_SIZE + 1
            end = (page + 1) * PAGE_SIZE
            try:
                json_data = fetch_mongddang_api(start, end)
                items = parse_mongddang_data(json_data)
                docs = [build_mongddang_doc(item) for item in items]
                all_docs.extend(docs)
            except Exception as e:
                tqdm.write(f"[ERROR] 페이지 {page + 1} 수집 실패: {e}")
            time.sleep(API_RATE_LIMIT_DELAY)

        # 개별 컬렉션 저장
        save_documents_with_progress(
            mongddang_collection, prepare_metadata_for_chroma(all_docs)
        )

        # 개별 컬렉션 저장
        save_documents_with_progress(
            unified_collection, prepare_metadata_for_chroma(all_docs)
        )

        elapsed = time.time() - start_time
        tqdm.write(f"\n총 {len(all_docs)}건 저장 완료. 소요 시간: {elapsed:.2f}초")

    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_mongddang_data()
