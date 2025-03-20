"""
데이터 로더 실행 스크립트 (load_data.py)
- gov24, youth 정책, 고용정보, PDF 데이터를 개별 또는 일괄로 로드하는 메인 스크립트
"""

import argparse
import os
import shutil
from django.conf import settings
from tqdm import tqdm

from .common import run_loader
from .load_employment_data import process_and_store_employment_data
from .load_gov24_data import process_and_store_gov24_data
from .load_pdf_data import process_and_store_pdf_data
from .load_youth_policy_data import process_and_store_youth_policy_data


def delete_all_collections():
    """
    CHROMA_DB_DIR 내 모든 컬렉션 폴더를 삭제
    """
    chroma_dir = settings.CHROMA_DB_DIR

    if not os.path.exists(chroma_dir):
        tqdm.write("Chroma 디렉토리가 존재하지 않습니다.")
        return

    collections = [
        f for f in os.listdir(chroma_dir) if os.path.isdir(os.path.join(chroma_dir, f))
    ]

    if collections:
        tqdm.write("\n=== 모든 컬렉션 삭제 시작 ===")
        for collection in collections:
            path = os.path.join(chroma_dir, collection)
            shutil.rmtree(path)
            tqdm.write(f"'{collection}' 폴더가 삭제되었습니다.")
        tqdm.write("=== 모든 컬렉션 삭제 완료 ===\n")
    else:
        tqdm.write("삭제할 컬렉션 폴더가 없습니다.")
