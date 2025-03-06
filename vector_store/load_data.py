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


def save_api_data_to_chroma():
    """API 데이터를 벡터DB에 저장"""
    # 데이터 수집
    gov_services = get_gov_services()
    youth_policies = get_youth_policies()
    employment_programs = get_employment_programs()

    documents = []
    print("문서 변환 중...")

    # 정부24 데이터 추가
    print(f"정부24 데이터 처리 중... ({len(gov_services)}개)")
    for item in tqdm(gov_services, desc="정부24 문서 변환", dynamic_ncols=True):
        doc = Document(
            page_content=f"{item.get('servNm', '이름 없음')}\n{item.get('servDgst', '설명 없음')}",
            metadata={"source": "정부24", "id": item.get("servId", "unknown_id")},
        )
        documents.append(doc)

    # 청년정책 데이터 추가
    print(f"청년정책 데이터 처리 중... ({len(youth_policies)}개)")
    for item in tqdm(youth_policies, desc="청년정책 문서 변환", dynamic_ncols=True):
        doc = Document(
            page_content=f"{item.get('plcyNm', '이름 없음')}\n{item.get('plcyExplnCn', '설명 없음')}",
            metadata={"source": "청년정책", "id": item.get("plcyNo", "unknown_id")},
        )
        documents.append(doc)

    # 고용24 데이터 추가
    print(f"고용24 데이터 처리 중... ({len(employment_programs)}개)")
    for item in tqdm(employment_programs, desc="고용24 문서 변환", dynamic_ncols=True):
        doc = Document(
            page_content=f"{item.get('title', '이름 없음')}\n{item.get('content', '설명 없음')}",
            metadata={"source": "고용24", "id": item.get("code", "unknown_id")},
        )
        documents.append(doc)

    if not documents:
        print("벡터화할 문서가 없습니다.")
        return 0

    print(f"총 {len(documents)}개 문서 임베딩 준비 완료")

    # 벡터DB 저장
    print("임베딩 모델 초기화 중...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        from langchain_chroma import Chroma

        print("langchain_chroma 패키지 사용")
    except ImportError:
        from langchain_community.vectorstores import Chroma

        print("langchain_community 패키지 사용")

    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        collection_name="startup_support_policies",
        embedding_function=embeddings,
    )

    # 배치 처리
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size

    print(f"벡터DB에 저장 중... (총 {total_batches}개 배치)")
    for i in tqdm(range(total_batches), desc="벡터DB 저장 진행", dynamic_ncols=True):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(documents))
        vectorstore.add_documents(documents[start_idx:end_idx])
        tqdm.write(
            f"  배치 {i+1}/{total_batches} 완료 ({start_idx+1}-{end_idx}번 문서)"
        )

    print(f"API 데이터 {len(documents)}개 벡터DB 저장 완료")
    return len(documents)


if __name__ == "__main__":
    try:
        print("=== 데이터 로딩 시작 ===")
        start_time = time.time()

        print("\n[STEP 1/2] PDF 벡터 저장")
        pdf_count = create_pdf_vectorstore()

        print("\n[STEP 2/2] API 데이터 벡터 저장")
        api_count = save_api_data_to_chroma()

        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print("\n=== 데이터 로딩 완료 ===")
        print(f"PDF 문서: {pdf_count}개")
        print(f"API 문서: {api_count}개")
        print(f"총 문서: {pdf_count + api_count}개")
        print(f"소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")
    except Exception as e:
        print(f"데이터 로딩 실패: {e}")
        import traceback

        traceback.print_exc()
