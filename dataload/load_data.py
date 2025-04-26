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
from .load_fifty_portal_edu_data import process_and_store_fifty_portal_edu_data
from .load_gov24_data import process_and_store_combined_gov24
from .load_mongddang_data import process_and_store_mongddang_data
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


def main():
    """
    명령어 인자를 받아 개별/전체 데이터 로더를 실행
    """
    parser = argparse.ArgumentParser(description="데이터 로더 실행 스크립트")
    parser.add_argument(
        "--gov24", action="store_true", help="정부24 API 데이터 로더 실행"
    )
    parser.add_argument(
        "--youth", action="store_true", help="청년정책 API 데이터 로더 실행"
    )
    parser.add_argument("--pdf", action="store_true", help="PDF 데이터 로더 실행")
    parser.add_argument(
        "--mongddang", action="store_true", help="몽당정보 데이터 로더 실행"
    )  # 몽땅정보 추가
    parser.add_argument(
        "--fifty_portal_edu",
        action="store_true",
        help="50플러스포털 교육정보 데이터 로더 실행",
    )  # 50플러스 교육정보 추가
    parser.add_argument("--all", action="store_true", help="모든 데이터 로더 실행")
    parser.add_argument(
        "--wipe", action="store_true", help="모든 컬렉션 삭제 후 로딩 실행"
    )

    args = parser.parse_args()

    # --wipe 사용 시 컬렉션 삭제
    if args.wipe:
        delete_all_collections()

    # 인자가 없을 경우 전체 실행으로 처리
    if not (
        args.gov24
        or args.youth
        or args.mongddang
        or args.fifty_portal_edu
        or args.pdf
        or args.all
    ):
        args.all = True

    if args.gov24 or args.all:
        run_loader(process_and_store_combined_gov24, "정부24 API")

    if args.youth or args.all:
        run_loader(process_and_store_youth_policy_data, "청년정책 API")

    if args.pdf or args.all:
        run_loader(process_and_store_pdf_data, "PDF 데이터")

    if args.mongddang or args.all:
        run_loader(process_and_store_mongddang_data, "몽땅정보 API")  # 몽땅정보 추가

    if args.fifty_portal_edu or args.all:
        run_loader(
            process_and_store_fifty_portal_edu_data, "50플러스포털 교육정보 API"
        )  # 50플러스 교육정보 추가


if __name__ == "__main__":
    main()
