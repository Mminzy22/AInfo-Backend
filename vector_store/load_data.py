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
