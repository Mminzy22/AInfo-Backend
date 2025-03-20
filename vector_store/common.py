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


def get_chroma_collection(collection_name, embeddings):
    """
    Chroma 컬렉션 객체 반환 함수
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )


def clear_collection(collection, collection_name):
    """
    지정된 컬렉션 내 모든 문서 삭제
    """
    result = collection.get()
    if result and "ids" in result and result["ids"]:
        collection.delete(ids=result["ids"])
        tqdm.write(f"'{collection_name}' 컬렉션의 모든 문서를 삭제했습니다.")
    else:
        tqdm.write(f"'{collection_name}' 컬렉션에 삭제할 문서가 없습니다.")


def save_documents_with_progress(collection, documents, batch_size=64):
    """
    문서를 배치로 저장하며 tqdm로 진행률 표시
    """
    total = len(documents)
    if total == 0:
        tqdm.write("저장할 문서가 없습니다.")
        return

    tqdm.write(f"총 {total}개 문서 저장 시작")
    for i in tqdm(range(0, total, batch_size), desc="Saving documents"):
        batch = documents[i : i + batch_size]
        collection.add_documents(batch)
    tqdm.write("모든 문서 저장 완료.")
