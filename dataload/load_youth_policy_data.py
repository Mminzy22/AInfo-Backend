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
    sanitize_metadata,
    save_documents_with_progress,
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


def clear_collection():
    """
    기존 youth_policy_list 컬렉션 데이터 삭제
    """
    embeddings = get_embeddings()
    collection_name = "youth_policy_list"
    list_db = get_chroma_collection(collection_name, embeddings)

    result = list_db.get()
    if result and "ids" in result and result["ids"]:
        list_db.delete(ids=result["ids"])
        tqdm.write(f"'{collection_name}' 컬렉션의 모든 문서를 삭제했습니다.")
    return list_db


def fetch_and_convert(page_num, existing_data=None):
    """
    API 데이터 페이지를 Document 객체로 변환
    """
    if existing_data is None:
        params = {
            "pageType": "1",
            "rtnType": "json",
            "apiKeyNm": YOUTH_POLICY_API_KEY,
            "pageSize": PAGE_SIZE,
            "pageNum": page_num,
        }
        json_data = fetch_api(params)
        if not json_data:
            return []
        page_policies = json_data.get("result", {}).get("youthPolicyList", [])
    else:
        page_policies = existing_data.get("result", {}).get("youthPolicyList", [])

    list_docs = []
    for policy in page_policies:
        list_docs.append(build_list_doc(policy))
    return list_docs


def build_list_doc(policy):
    """
    단일 정책 데이터를 Document로 변환
    """
    page_content = f"""
    정책명: {policy.get('plcyNm', '정보 없음')}
    정책지원내용: {policy.get('plcySprtCn', '정보 없음')}
    심사방법내용: {policy.get('srngMthdCn', '정보 없음')}
    상세설명URL주소: {policy.get('refUrlAddr1', '정보 없음')}
    등록기관명: {policy.get('rgtrInstCdNm', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "name": policy.get("plcyNm", ""),
            "subject": policy.get("srngMthdCn", ""),
            "detail": policy.get("plcySprtCn", ""),
            "link": policy.get("refUrlAddr1", ""),
            "region": policy.get("rgtrInstCdNm", ""),
            "source": "청년정책",
        }
    )

    return Document(page_content=page_content, metadata=metadata)


def process_and_store_youth_policy_data():
    """
    청년정책 데이터 전체 수집 및 저장 파이프라인
    """
    try:
        tqdm.write("=== 청년정책 데이터 로딩 시작 ===")
        start_time = time.time()

        list_db = clear_collection()
        all_list_docs = []

        params = {
            "pageType": "1",
            "rtnType": "json",
            "apiKeyNm": YOUTH_POLICY_API_KEY,
            "pageSize": PAGE_SIZE,
            "pageNum": 1,
        }
        first_page_data = fetch_api(params)
        if not first_page_data:
            tqdm.write("첫 페이지 API 호출 실패")
            return

        pagging = first_page_data.get("result", {}).get("pagging", {})
        total_count = pagging.get("totCount", 0)
        if total_count == 0:
            tqdm.write("수집할 데이터가 없습니다.")
            return
        total_pages = math.ceil(total_count / PAGE_SIZE)
        tqdm.write(f"총 {total_count}건 / {total_pages}페이지 데이터 수집 예정")

        for page in tqdm(range(1, total_pages + 1), desc="수집 진행중"):
            if page == 1:
                list_docs = fetch_and_convert(page, existing_data=first_page_data)
            else:
                list_docs = fetch_and_convert(page)
            all_list_docs.extend(list_docs)
            time.sleep(API_RATE_LIMIT_DELAY)

        save_documents_with_progress(
            list_db, prepare_metadata_for_chroma(all_list_docs)
        )

        elapsed = time.time() - start_time
        tqdm.write(f"\n총 {len(all_list_docs)}건 저장 완료. 소요 시간: {elapsed:.2f}초")

    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_youth_policy_data()
