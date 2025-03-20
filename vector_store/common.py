"""
공통 유틸리티 모듈 (common.py)
- ChromaDB 및 임베딩 관련 공통 함수 제공
"""

import os
import traceback
import django
import environ
from django.conf import settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
import logging

# 환경 변수 및 Django 설정
env = environ.Env()
environ.Env.read_env()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# 설정 값 로드
CHROMA_DB_DIR = settings.CHROMA_DB_DIR
OPENAI_API_KEY = env("OPENAI_API_KEY")

# ChromaDB 로깅 레벨 설정
logging.getLogger("chromadb").setLevel(logging.ERROR)


def get_embeddings():
    """
    OpenAI 임베딩 반환 함수
    """
    return OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
