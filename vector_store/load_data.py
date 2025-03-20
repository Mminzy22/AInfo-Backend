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
