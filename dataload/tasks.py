import time
import traceback

from celery import shared_task
from tqdm import tqdm

from .load_gov24_data import process_and_store_gov24_data
from .load_mongddang_data import process_and_store_mongddang_data
from .load_youth_policy_data import process_and_store_youth_policy_data


@shared_task
def load_gov24_data_task():
    """
    Celery를 통해 실행되는 정부24 정보 데이터 로딩 작업
    """
    try:
        tqdm.write("=== 정부24 데이터 로딩 시작 (Celery) ===")
        start_time = time.time()
        process_and_store_gov24_data()
        elapsed = time.time() - start_time
        tqdm.write(f"=== 데이터 로딩 완료. 소요 시간: {elapsed:.2f}초 ===")
    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


@shared_task
def load_youth_policy_data_task():
    """
    Celery를 통해 실행되는 온통청년 정보 데이터 로딩 작업
    """
    try:
        tqdm.write("=== 온통청년 데이터 로딩 시작 (Celery) ===")
        start_time = time.time()
        process_and_store_youth_policy_data()
        elapsed = time.time() - start_time
        tqdm.write(f"=== 데이터 로딩 완료. 소요 시간: {elapsed:.2f}초 ===")
    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()


@shared_task
def load_mongddang_data_task():
    """
    Celery를 통해 실행되는 온통청년 정보 데이터 로딩 작업
    """
    try:
        tqdm.write("=== 몽땅정보 데이터 로딩 시작 (Celery) ===")
        start_time = time.time()
        process_and_store_mongddang_data()
        elapsed = time.time() - start_time
        tqdm.write(f"=== 데이터 로딩 완료. 소요 시간: {elapsed:.2f}초 ===")
    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()
