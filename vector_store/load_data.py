import os
import django
import time
import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.schema import Document
from tqdm import tqdm  # 진행 상황 표시용

# Django 설정 로드
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# 설정값
CHROMA_DB_DIR = settings.CHROMA_DB_DIR
PDF_PATH = settings.PDF_PATH
GOV24_API_KEY = settings.GOV24_API_KEY
YOUTH_POLICY_API_KEY = settings.YOUTH_POLICY_API_KEY
EMPLOYMENT_API_KEY = settings.EMPLOYMENT_API_KEY

# API URL
GOV24_BASE_URL = "https://api.odcloud.kr/api/gov24/v3"
YOUTH_POLICY_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
EMPLOYMENT_URL = (
    "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo217L01.do"
)

# 데이터 수집 설정
MAX_PAGES = 600
PAGE_SIZE = 20
API_RATE_LIMIT_DELAY = 0.5


def load_pdf():
    """PDF 문서 로드"""
    if not PDF_PATH or not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {PDF_PATH}")
    print("PDF 파일 로드 중...")
    return PyMuPDFLoader(PDF_PATH).load()


def create_pdf_vectorstore():
    """PDF 문서를 벡터로 변환하여 저장"""
    documents = load_pdf()
    print(f"PDF 문서 분할 중... (총 {len(documents)}개 문서)")

    text_splitter = CharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200, separator="\n"
    )
    texts = text_splitter.split_documents(documents)

    print(f"PDF 문서 임베딩 중... (총 {len(texts)}개 조각)")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        collection_name="startup_support_policies",
        persist_directory=CHROMA_DB_DIR,
    )
    print(f"PDF 벡터 저장 완료 ({len(texts)}개)")
    return len(texts)
