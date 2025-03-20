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
    sanitize_metadata,
    save_documents_with_progress,
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


def clear_collection_for_employment(embeddings):
    """
    고용24 컬렉션 초기화
    """
    collection_name = "employment_programs"
    collection = get_chroma_collection(collection_name, embeddings)
    clear_collection(collection, collection_name)
    return collection


def fetch_employment_programs(start_page=1, display=PAGE_SIZE):
    """
    API에서 고용24 프로그램 목록 조회
    """
    params = {
        "authKey": EMPLOYMENT_API_KEY,
        "returnType": "XML",
        "startPage": start_page,
        "display": display,
    }
    response = requests.get(EMPLOYMENT_API_URL, params=params, timeout=10)
    response.raise_for_status()
    return ET.fromstring(response.text)


def parse_employment_programs(root):
    """
    XML에서 프로그램 데이터 및 총 개수 파싱
    """
    programs = []
    total_count = 0

    total_element = root.find("./total")
    if total_element is not None:
        total_count = int(total_element.text.strip())

    items = root.findall(".//empPgmSchdInvite")
    for item in items:
        program = {
            child.tag: child.text.strip() if child.text else "" for child in item
        }
        programs.append(program)

    return programs, total_count


def prepare_employment_program_document(program):
    """
    프로그램 dict를 Document로 변환
    """
    pgm_nm = program.get("pgmNm", "")
    if not pgm_nm:
        return None

    page_content = f"""
    프로그램명: {program.get('pgmNm', '정보 없음')}
    과정명: {program.get('pgmSubNm', '정보 없음')}
    대상자: {program.get('pgmTarget', '정보 없음')}
    교육기간: {program.get('pgmStdt', '정보 없음')} ~ {program.get('pgmEndt', '정보 없음')}
    운영시간: {program.get('operationTime', '정보 없음')}
    시작시간: {program.get('openTimeClcd', '정보 없음')} {program.get('openTime', '정보 없음')}
    개최장소: {program.get('openPlcCont', '정보 없음')}
    고용센터명: {program.get('orgNm', '정보 없음')}
    """.strip()

    metadata = sanitize_metadata(
        {
            "pgmNm": program.get("pgmNm", ""),
            "pgmSubNm": program.get("pgmSubNm", ""),
            "pgmTarget": program.get("pgmTarget", ""),
            "pgmStdt": program.get("pgmStdt", ""),
            "pgmEndt": program.get("pgmEndt", ""),
            "operationTime": program.get("operationTime", ""),
            "openTimeClcd": program.get("openTimeClcd", ""),
            "openTime": program.get("openTime", ""),
            "openPlcCont": program.get("openPlcCont", ""),
            "orgNm": program.get("orgNm", ""),
        }
    )

    return Document(page_content=page_content, metadata=metadata)


def process_and_store_employment_data():
    """
    고용24 데이터를 수집 후 ChromaDB에 저장
    """
    try:
        tqdm.write("=== 고용24 데이터 로딩 시작 ===")
        start_time = time.time()

        embeddings = get_embeddings()
        db = clear_collection_for_employment(embeddings)

        all_programs = []
        root = fetch_employment_programs(start_page=1)
        _, total_count = parse_employment_programs(root)
        total_pages = min(MAX_PAGES, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        tqdm.write(f"총 프로그램 수: {total_count}, 페이지 수: {total_pages}")

        with tqdm(
            total=total_count, desc="데이터 수집", unit="건", dynamic_ncols=True
        ) as pbar:
            for page in range(1, total_pages + 1):
                try:
                    root = fetch_employment_programs(start_page=page)
                    page_programs, _ = parse_employment_programs(root)
                    all_programs.extend(page_programs)
                    pbar.update(len(page_programs))
                except Exception as e:
                    tqdm.write(f"[WARNING] 페이지 {page} 수집 실패: {e}")
                time.sleep(API_RATE_LIMIT_DELAY)

        program_documents = []
        for program in tqdm(
            all_programs, desc="문서 변환", unit="건", dynamic_ncols=True
        ):
            doc = prepare_employment_program_document(program)
            if doc:
                program_documents.append(doc)

        program_documents = prepare_metadata_for_chroma(program_documents)
        save_documents_with_progress(db, program_documents)

        elapsed = time.time() - start_time
        tqdm.write(
            f"\n총 {len(program_documents)}건 저장 완료. 소요 시간: {elapsed:.2f}초"
        )
    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    process_and_store_employment_data()
