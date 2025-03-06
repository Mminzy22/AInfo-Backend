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


def get_gov_services():
    """정부24 공공서비스 목록 조회"""
    url = f"{GOV24_BASE_URL}/serviceList"
    all_services = []
    total_count = 0

    print("정부24 데이터 수집 중...")

    # 첫 페이지 요청으로 총 개수 확인
    try:
        first_page_params = {
            "serviceKey": GOV24_API_KEY,
            "page": 1,
            "perPage": PAGE_SIZE,
        }
        first_response = requests.get(url, params=first_page_params)
        if first_response.status_code == 200:
            first_data = first_response.json()
            total_count = first_data.get("totalCount", 0)
            if "data" in first_data:
                all_services.extend(first_data.get("data", []))

            expected_pages = min(MAX_PAGES, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)
            print(f"정부24 총 정책 수: {total_count}, 예상 페이지 수: {expected_pages}")

            # 2페이지부터 데이터 수집
            for page in tqdm(
                range(2, expected_pages + 1),
                desc="정부24 데이터 수집",
                dynamic_ncols=True,
            ):
                params = {
                    "serviceKey": GOV24_API_KEY,
                    "page": page,
                    "perPage": PAGE_SIZE,
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    services = data.get("data", [])
                    if not services:
                        break
                    all_services.extend(services)
                else:
                    print(f"정부24 API 요청 실패: 상태 코드 {response.status_code}")
                    break
                time.sleep(API_RATE_LIMIT_DELAY)
    except Exception as e:
        print(f"정부24 API 오류: {e}")

    print(f"정부24 데이터 수집 완료: {len(all_services)}개")
    return all_services


def get_youth_policies():
    """청년정책 목록 조회"""
    all_policies = []
    total_count = 0

    print("청년정책 데이터 수집 중...")

    # 첫 페이지 요청으로 총 개수 확인
    try:
        first_page_params = {
            "apiKeyNm": YOUTH_POLICY_API_KEY,
            "pageNum": 1,
            "pageSize": PAGE_SIZE,
            "rtnType": "json",
        }
        first_response = requests.get(
            YOUTH_POLICY_URL, params=first_page_params, timeout=10
        )
        if first_response.status_code == 200:
            first_data = first_response.json()
            total_count = (
                first_data.get("result", {}).get("pagging", {}).get("totCount", 0)
            )
            policies = first_data.get("result", {}).get("youthPolicyList", [])
            all_policies.extend(policies)

            expected_pages = min(MAX_PAGES, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)
            print(
                f"청년정책 총 정책 수: {total_count}, 예상 페이지 수: {expected_pages}"
            )

            # 2페이지부터 데이터 수집
            for page in tqdm(
                range(2, expected_pages + 1),
                desc="청년정책 데이터 수집",
                dynamic_ncols=True,
            ):
                params = {
                    "apiKeyNm": YOUTH_POLICY_API_KEY,
                    "pageNum": page,
                    "pageSize": PAGE_SIZE,
                    "rtnType": "json",
                }
                response = requests.get(YOUTH_POLICY_URL, params=params, timeout=10)
                if response.status_code != 200 or not response.text.strip():
                    break
                try:
                    data = response.json()
                    policies = data.get("result", {}).get("youthPolicyList", [])
                    if not policies:
                        break
                    all_policies.extend(policies)
                except requests.exceptions.JSONDecodeError:
                    break
                time.sleep(API_RATE_LIMIT_DELAY)
    except requests.exceptions.RequestException as e:
        print(f"청년정책 API 오류: {e}")

    print(f"청년정책 데이터 수집 완료: {len(all_policies)}개")
    return all_policies


def get_employment_programs():
    """고용24 구직자취업역량강화 프로그램 조회"""
    all_programs = []
    total_count = 0

    print("고용24 데이터 수집 중...")

    # 첫 페이지 요청으로 총 개수 확인
    try:
        first_page_params = {
            "authKey": EMPLOYMENT_API_KEY,
            "returnType": "XML",
            "startPage": 1,
            "display": PAGE_SIZE,
        }
        first_response = requests.get(
            EMPLOYMENT_URL, params=first_page_params, timeout=15
        )
        if first_response.status_code == 200:
            try:
                root = ET.fromstring(first_response.text)
                total_element = root.find(".//total")
                if total_element is not None and total_element.text:
                    total_count = int(total_element.text)

                # 첫 페이지 데이터 처리
                items = root.findall(".//empPgmSchdInvite")
                for item in items:
                    program = {}
                    for child in item:
                        program[child.tag] = child.text

                    mapped_program = {
                        "title": program.get("pgmNm", "")
                        + (
                            " - " + program.get("pgmSubNm", "")
                            if program.get("pgmSubNm")
                            else ""
                        ),
                        "content": program.get("pgmTarget", ""),
                        "code": program.get("pgmNm", ""),
                        "startDate": program.get("pgmStdt", ""),
                        "endDate": program.get("pgmEndt", ""),
                        "location": program.get("openPlcCont", ""),
                        "time": program.get("operationTime", ""),
                        "organization": program.get("orgNm", ""),
                    }
                    all_programs.append(mapped_program)

                expected_pages = min(
                    MAX_PAGES, (total_count + PAGE_SIZE - 1) // PAGE_SIZE
                )
                print(
                    f"고용24 총 정책 수: {total_count}, 예상 페이지 수: {expected_pages}"
                )

                # 2페이지부터 데이터 수집
                for page in tqdm(
                    range(2, expected_pages + 1),
                    desc="고용24 데이터 수집",
                    dynamic_ncols=True,
                ):
                    params = {
                        "authKey": EMPLOYMENT_API_KEY,
                        "returnType": "XML",
                        "startPage": page,
                        "display": PAGE_SIZE,
                    }
                    response = requests.get(EMPLOYMENT_URL, params=params, timeout=15)
                    if response.status_code != 200 or not response.text.strip():
                        break
                    try:
                        root = ET.fromstring(response.text)
                        error_element = root.find(".//error")
                        if error_element is not None:
                            break

                        items = root.findall(".//empPgmSchdInvite")
                        if not items:
                            break

                        for item in items:
                            program = {}
                            for child in item:
                                program[child.tag] = child.text

                            mapped_program = {
                                "title": program.get("pgmNm", "")
                                + (
                                    " - " + program.get("pgmSubNm", "")
                                    if program.get("pgmSubNm")
                                    else ""
                                ),
                                "content": program.get("pgmTarget", ""),
                                "code": program.get("pgmNm", ""),
                                "startDate": program.get("pgmStdt", ""),
                                "endDate": program.get("pgmEndt", ""),
                                "location": program.get("openPlcCont", ""),
                                "time": program.get("operationTime", ""),
                                "organization": program.get("orgNm", ""),
                            }
                            all_programs.append(mapped_program)
                    except ET.ParseError:
                        break
                    time.sleep(API_RATE_LIMIT_DELAY)
            except ET.ParseError as e:
                print(f"XML 파싱 오류: {e}")
    except requests.exceptions.RequestException as e:
        print(f"고용24 API 오류: {e}")

    print(f"고용24 데이터 수집 완료: {len(all_programs)}개")
    return all_programs
