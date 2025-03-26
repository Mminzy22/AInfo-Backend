import time
import traceback

from celery import shared_task
from tqdm import tqdm

from .load_employment_data import process_and_store_employment_data


@shared_task
def load_employment_data_task():
    """
    Celery를 통해 실행되는 고용정보 데이터 로딩 작업
    """
    try:
        tqdm.write("=== 고용정보 데이터 로딩 시작 (Celery) ===")
        start_time = time.time()
        process_and_store_employment_data()
        elapsed = time.time() - start_time
        tqdm.write(f"=== 데이터 로딩 완료. 소요 시간: {elapsed:.2f}초 ===")
    except Exception as e:
        tqdm.write(f"[ERROR] 데이터 로딩 실패: {e}")
        traceback.print_exc()
