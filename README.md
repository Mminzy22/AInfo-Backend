## 💡 아이디어, 기획

### *“정책은 있는데, 정보는 어디 있나요?”*

> 1만 개가 넘는 지원 정책, 나에게 맞는 정책은 어디에 있을까요?
> 
> 
> 정부와 공공기관은 방대한 지원 정책과 복지 서비스를 제공하고 있지만,
> 
> 정작 필요한 정보를 찾는 과정은 복잡하고 어렵습니다.
> 

### ***“정보를 몰라 기회를 놓치지 않도록.”***

> 공공서비스 정보 탐색의 복잡함을 줄이고, 누구나 필요한 지원을 빠르게 찾을 수 있도록 돕는 AI 챗봇 서비스를 개발했습니다.
> 
- AI 챗봇을 통한 대화형 탐색.
- 나이, 지역, 관심 분야 기반의 맞춤형 추천 및 필터링.
- 유사 정책 비교로 전략적인 선택까지!

**AInfo**는 국민취업지원제도를 몰라 지원 받지 못했던 **우리의 경험**에서 시작했습니다.

우리의 불편이 더 많은 사람에게 **도움이 되는 정보**로 이어지길 바랍니다.

---

## 📝 프로젝트 개요

AInfo는 맞춤형 공공서비스 추천 AI 챗봇입니다. Django Rest Framework(DRF)를 기반으로 API를 제공하며, AI 모델과 연동하여 실시간으로 사용자의 질의에 응답합니다.

---

| 📆 개발 기간 | 🙋🏻‍♂️ 팀원 | 📜 SA 문서 |
| --- | --- | --- |
| 25.2.27 ~ 25.3.31 | [양주영](https://github.com/JuyoungYang), [박민지](https://github.com/Mminzy22), [유종열](https://github.com/jongyeol2), [채희경](https://github.com/cheaheekyung), [정지웅](https://github.com/JaceJung-dev) |  [SA 문서 바로가기](https://www.notion.so/Fourtato-19faf76d38e280cd8ebbc140c6588adf?pvs=21) |

---

# 📚 서비스 소개

### 서비스 시연 영상

[영상]

### 서비스 아키텍처

---

### 🍟 팀원:

- **양주영(팀장)**
    - PDF 및 공공 API 데이터를 벡터 DB로 변환하고 저장하는 파이프라인 구축
    - LangChain + ChromaDB 기반 벡터 임베딩 및 컬렉션 구조 설계
    - 멀티 컬렉션 + 메타데이터 필터링이 가능한 커스텀 리트리버 시스템 구현
- **박민지(부팀장)**
    - JWT 기반 회원 기능 (가입, 로그인, 프로필)
    - 백엔드 EC2 배포, 프론트 S3 + CloudFront 배포
    - HTTPS 적용 (Route53 + ACM)
    - 뉴스 기반 검색 LangChain Agent 개발
    - CrewAI 활용한 Multi-Agent 개발
- **유종열(서기)**
    - WebSocket 기반 챗봇 구현
    - 도커를 활용한 애플리케이션 및 레디스 컨테이너화
    - SMTP서버 활용한 본인인증 메일 및 관리자페이지 공지메일 기능 구현
    - 회원 추가기능 구현
    - Celery 활용한 비동기 처리
    - PortOne 활용한 결제 기능 구현
    - Celery-Beat 활용한 VectorDB 데이터 로드 스케쥴링
- **채희경(서기)**
    - 정부 정책 특화 챗봇을 위한 시스템 프롬프트 설계 및 응답 포맷 구성 (MVP모델)
    - 사용자 질문 기반 문서 검색 및 LLM 응답 생성을 위한 LangChain 체인 구성 (MVP모델)
    - WebSocket 및 REST API 기반 챗룸 생성·조회·수정·삭제 기능 구현
    - 백엔드 애플리케이션 자동 배포를 위한 GitHub Actions 기반 CD 파이프라인 작성
    - 채팅방 목록, 메시지 출력 등 챗봇 프론트엔드 기능 개발
- **정지웅(총무)**
    - WebSocket 기반 챗봇 구현
    - WebSocket에서 JWT 인증 미들웨어 적용
    - 챗봇 메시지 스트리밍 기능 추가
    - Redis 세션 저장소, LangChain의 메모리 관리 기능를 활용한 요약 기반의 멀티턴 대화 시스템 구현
    - LangChain, OpenAI 기반 LLM과 규칙 기반 분류를 결합하여 사용자 의도를 분석하는 하이브리드 방식의 입력 분류기 구현
    - 사용자 입력 분류 유형에 따른 맞춤형 agent(RAG agent, 보고서 작성 agent)를 동적으로 호출하는 플로우 설계, 구현 및 RAG agent 구현

---

### 🐣 Release Version : 2.1.2

### 🔗 서비스 접속 : [https://www.ainfo.ai.kr](https://www.ainfo.ai.kr/)

### 🔗 연결 Frontend repo: [AInfo-Frontend](https://github.com/Mminzy22/AInfo-Frontend)

---

## 🛠️ 기술 스택

- **언어:** Python (Django, Django Rest Framework)
- **데이터베이스:** PostgresQL, ChromaDB
- **LLM 및 데이터 처리:** OpenAI API, LangChain, CrewAI
- **웹소켓:** Django Channels, Redis
- **비동기**: Celery, Celery-beat, Redis
- **배포:** Docker, AWS (EC2, S3, Route 53), Nginx, Gunicorn

---

## 📂 프로젝트 구조

```
📂 AInfo-Backend/
│
├── .github/                   # GitHub 관련 설정 (CI/CD 및 이슈 템플릿)
│   ├── ISSUE_TEMPLATE/        # GitHub 이슈 템플릿
│   │   ├── bug_report.md      # 버그 리포트 양식
│   │   ├── documentation.md   # 문서화 관련 템플릿
│   │   └── feature_request.md # 기능 요청 양식
│   │
│   └── workflows/             # GitHub Actions 설정
│       ├── ci.yml             # CI 관련 설정
│       └── cd.yml             # CD 관련 설정
│
├── accounts/                             # 사용자 인증 및 관리
│   ├── migrations/                       # DB 마이그레이션 파일
│   ├── templates/                        # 메일인증 및 render 를 위한 템플릿
│   │   └── account/
│   │       ├── activate_email.html
│   │       ├── password_reset_email.html
│   │       └── password_reset.html
│   ├── admin.py                         # Django 관리자 페이지 설정
│   ├── apps.py                          # 앱 설정 파일
│   ├── models.py                        # 사용자 관련 모델 정의
│   ├── serializers.py                   # 데이터 직렬화 로직
│   ├── tasks.py
│   ├── tests.py                         # accounts 관련 테스트 코드
│   ├── tokens.py                        # 인증링크 조작 방지를 위한 토큰생성을 위한 파일
│   ├── urls.py                          # accounts 관련 URL 라우팅
│   └── views.py                         # accounts 관련 뷰 로직
│
├── chatbot/            # AI 챗봇 관련 기능
│   ├── migrations/     # DB 마이그레이션 파일
│   ├── admin.py        # 챗봇 관리자 페이지 설정
│   ├── apps.py         # 챗봇 앱 설정 파일
│   ├── consumers.py    # WebSocket 컨슈머
│   ├── middleware.py   # JWT 인증 미들웨어 (WebSocket 연결 시 인증 처리)
│   ├── models.py       # 챗봇 관련 데이터 모델 (선택적으로 사용)
│   ├── routing.py      # WebSocket 라우팅 설정
│   ├── retriever.py    # RAG 검색 리트리버 (Chroma 등)
│   ├── serializers.py  # chatroom 및 메시지 유효성 검사
│   ├── tests.py        # 챗봇 기능 테스트 코드
│   ├── urls.py         # chatroom REST API 라우팅 설정
│   ├── views.py        # chatroom REST API 뷰 
│   │
│   ├── langchain_flow/                 # LangChain 기반 에이전트 구성
│   │   ├── prompts/                    # LangChain 전용 프롬프트 (optional)
│   │   │   └── search_prompt.py  
│   │   ├── tools/                      # LangChain용 단일 툴 모듈
│   │   │   └── tavily_news_tool.py 
│   │   ├── chains/                     # 체인 및 Executor 구성
│   │   │   └── news_search_executor.py 
│   │   ├── memory.py                   # 멀티턴 memory 관리
│   │   ├── filter_utils.py             # Chroma 필터 문법 변환
│   │   └── run.py                      # LangChain 최상위 실행 지점
│   │
│   └── crew_wrapper/              # CrewAI 기반 멀티에이전트 구조 구성 디렉토리
│       ├── tests/                 # 통합 테스트 코드 디렉토리
│       │   ├── __init__.py
│       │   └── flows/
│       │       ├── __init__.py
│       │       └── test_policy_flow.py   # 정책 추천 Flow 테스트 코드
│       │
│       ├── crews/                        # 기능별 크루(Crew) 정의 디렉토리
│       │   ├── __init__.py
│       │   ├── compare_crew/             # 비교 분석 크루 (예: 서비스 비교, 정책 비교)
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── compare_agent.py  # 비교 분석용 에이전트 정의
│       │   │   │   ├── compare_task.py   # 비교 Task 정의
│       │   │   │   └── prompts.py        # 비교용 프롬프트 정의
│       │   │   └── compare_crew.py       # 비교 크루 구성
│       │   ├── rag_crew/                 # RAG 기반 정책 추천 크루
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── prompts.py           # 정책 추천용 프롬프트
│       │   │   │   ├── rag_search_input.py  # RAG 검색 입력 스키마 정의
│       │   │   │   ├── rag_search_task.py   # RAG 검색 Task 정의
│       │   │   │   └── reg_agent.py         # 정책 추천 RAG 에이전트
│       │   │   └── rag_crew.py              # RAG 크루 구성
│       │   ├── report_crew/                 # 리포트 요약 및 생성 크루
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── prompts.py           # 보고서 생성용 프롬프트
│       │   │   │   ├── report_agent.py      # 보고서 생성 Agent 정의
│       │   │   │   └── report_task.py       # 보고서 Task 정의
│       │   │   └── report_crew.py           # 리포트 크루 구성
│       │   ├── strategy_crew/               # 맞춤형 전략 제안 크루
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── prompts.py           # 전략 제안 프롬프트
│       │   │   │   ├── strategy_agent.py    # 전략 제안 Agent 정의
│       │   │   │   └── strategy_task.py     # 전략 Task 정의
│       │   │   └── strategy_crew.py         # 전략 크루 구성
│       │   └── web_crew/                    # 웹 검색 기반 정보 수집 크루
│       │       ├── __init__.py
│       │       ├── config/
│       │       │   ├── __init__.py
│       │       │   ├── compare_agent.py     # 외부 정보 비교 Agent 정의
│       │       │   ├── compare_task.py      # 외부 비교 Task 정의
│       │       │   ├── compare_task.py      # 외부 정보 프롬프트
│       │       │   └── prompts.py           # 웹 기반 비교 크루 구성
│       │       └── compare_crew.py
│       ├── flows/                  # 다양한 크루들의 실행 흐름(Flow) 정의
│       │   ├── __init__.py
│       │   └── policy_flow.py      # 정책 추천을 위한 크루 실행 흐름 정의
│       │
│       └── tools/                  # CrewAI Task에서 사용하는 공통 툴 정의
│           ├── __init__.py 
│           ├── rag_search_tool.py  # 벡터 기반 RAG 검색 툴
│           └── web_search_tool.py  # 웹 검색용 API 툴
│
├── config/          # 프로젝트 설정 및 환경 변수
│   ├── init.py      # 설정 패키지 초기화
│   ├── asgi.py      # ASGI 서버 설정
│   ├── celery.py
│   ├── settings.py  # Django 프로젝트 설정
│   ├── urls.py      # 프로젝트 전체 URL 매핑
│   └── wsgi.py      # WSGI 서버 설정
│
├── notifications/      # 메일, 알림 관련 기능
│   ├── migrations/     # DB 마이그레이션 파일
│   ├── admin.py        # notifications 관리자 페이지 설정
│   ├── apps.py         # notifications 앱 설정 파일
│   ├── models.py       # notifications 관련 데이터 모델
│   ├── tasks.py        # 비동기 처리를 위한 task 설정 
│   ├── tests.py        # notifications 기능 테스트 코드
│   ├── urls.py         # REST API 라우팅 설정
│   └── views.py        # notifications REST API 방식의 뷰
│ 
├── payments/           # 결제 관련 기능
│   ├── migrations/     # DB 마이그레이션 파일
│   ├── admin.py        # payments 관리자 페이지 설정
│   ├── apps.py         # payments 앱 설정 파일
│   ├── models.py       # payments 관련 데이터 모델
│   ├── tests.py        # payments 기능 테스트 코드
│   ├── urls.py         # REST API 라우팅 설정
│   └── views.py        # payments REST API 방식의 뷰
│
├── data/               # 데이터 관련 폴더
│   └── pdf/            # PDF 데이터 저장
│       └── 2025년_중앙부처_및_지자체_창업지원사업_안내책자.pdf 
├── dataload/
│   ├── common.py                  # ChromaDB 및 임베딩 관련 공통 유틸리티
│   ├── load_data.py               # 모든 데이터 로더를 통합 실행하는 메인 스크립트
│   ├── load_employment_data.py    # 고용24 API 데이터 로더
│   ├── load_gov24_data.py         # 정부24 API 데이터 로더
│   ├── load_pdf_data.py           # Kstartup PDF 데이터 로더
│   ├── load_youth_policy_data.py  # 청년정책 API 데이터 로더
│   ├── admin.py                   # dataload 관리자 페이지 설정
│   ├── apps.py                    # dataload 앱 설정 파일
│   ├── models.py                  # dataload 관련 데이터 모델
│   ├── tests.py                   # dataload 기능 테스트 코드
│   ├── tasks.py                   # 비동기 처리를 위한 task 설정
│   └── views.py                   # dataload REST API 방식의 뷰
│
│
├── .flake8           # 코드 스타일 규칙
├── .gitignore        # Git에 포함되지 않을 파일 설정
├── README.md         # 프로젝트 설명 파일
├── manage.py         # Django 실행 파일
├── pyproject.toml    # Python 프로젝트 설정
└── requirements.txt  # 필수 패키지 목록
```

---

## ✨ 주요 기능

### 유저 기능

- JWT 기반 로그인/회원가입
    
    ![회원가입_로그인.gif]()
    
- 이메일 인증
    
    ![회원가입_로그인.gif]()
    
- 소셜 로그인
    
    ![소셜로그인.gif]()
    
- 본인인증 및 비밀번호 재설정
    
    ![비밀번호재설정.gif]()
    
- 회원 탈퇴
    
    ![회원탈퇴.gif]()
    
- 프로필 수정
    
    ![프로필수정.gif]()
    

### AI 챗봇

- LangChain + ChromaDB 기반 RAG 모델 연동
- Django Channels, Redis를 이용한 WebSocket 실시간 대화 지원
- 맞춤형 공공서비스 추천 기능
    
    ![챗봇대화일반모드.gif]()
    
- 대화 흐름 기억
    
    ![news-31-2025 01-21-00.gif]()
    
- 부족한 정보 → 웹검색
    
    ![news-31-2025 01-21-00.gif]()
    
- 보고서 작성 기능
    
    ![Mar-31-2025 01-17-32.gif]()
    

### 공공 데이터 연동

- 정부 API(고용24, 정부24, 온통청년) 활용
- K스타트업 안내책자 pdf 활용
- 주기적 데이터 로드
    
    []()
    

### 메일 기능

- 본인인증을 위한 메일 발송
    
    ![mail-31-2025 01-11-48.gif]()
    
- 전체유저 대상 공지메일 발송
    
    ![image.png]()
    

### 결제 기능

- KG 이니시스 PG 사 연동
- 결제 관련정보 DB 관리

![pay-31-2025 01-04-33.gif]()

---

## 💿 설치 및 실행 방법

### 1. 백엔드 프로젝트 클론

```bash
git clone https://github.com/your-repo/AInfo-Backend.git
cd AInfo-Backend
```

### 2. 환경 변수 설정

`.env` 파일을 생성하여 필요한 환경 변수를 설정합니다.

```
# 디버그 모드 (운영에서는 False)
DEBUG=True
# DEBUG=False

# Django Secret Key
DJANGO_SECRET_KEY="YOUR DJANGO_SECRET_Key"

# 운영 환경에서만 적용됨
ALLOWED_HOSTS=example.com
CORS_ALLOWED_ORIGINS=http://example.com

# 운영 환경에서만 적용됨 (개발 환경에서는 SQLite 사용)
DATABASE_URL=postgres://<이름>:<패스워드>@<이름>.czc602cim9iz.ap-northeast-2.rds.amazonaws.com:5432/<DB이름>

# 로컬 개발 환경용 Google OAuth & Redirect URI
GOOGLE_CLIENT_ID=YOUR GOOGLE_CLIENT_ID

# 운영 환경용 Google OAuth & Redirect URI
# GOOGLE_CLIENT_ID=your-prod-client-id

# OPENAI_API Key
OPENAI_API_KEY="YOUR OPENAI_API_KEY"

# DB API Key 
GOV24_API_KEY="YOUR API KEY" 
YOUTH_POLICY_API_KEY="YOUR API KEY" 
EMPLOYMENT_API_KEY="YOUR API KEY" 

# PDF 파일명(경로는 settings.py에서 자동으로 설정됨) 
PDF_PATH=2025년_중앙부처_및_지자체_창업지원사업_안내책자.pdf

# ChromaDB 저장 경로 
CHROMA_DB_DIR=./chroma_db

# 기본 권한 클래스 설정
DEFAULT_PERMISSION_CLASSES=rest_framework.permissions.IsAuthenticated

# 웹 검색 API
TAVILY_API_KEY="YOUR API KEY"

# Gmail SMTP서버 관련 설정
EMAIL_PORT="YOUR PORT"
EMAIL_ID="YOUR EMAIL ID"
EMAIL_APP_PW="YOUR EMAIL APP PW"
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 5. 데이터 로드

```bash
python -m dataload.load_data
```

### 6. 서버 실행

```bash
docker run --rm -p 6379:6379 --name redis-server redis
python manage.py runserver

# celery-worker 실행
celery -A config worker --loglevel=info
# celery-beat 실행
celery -A config beat --loglevel=info
```

---

## API 문서

API 엔드포인트 및 요청/응답 예시는 [API 문서](https://www.notion.so/API-1a7af76d38e28182a3d5e14e7d24b764?pvs=21)에서 확인하세요.

---

## 📒 Release Notes

### [V1.0.0](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v1.0.0)


### [V1.0.1](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v1.0.1)


### [V2.0.0](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v2.0.0)


### [V2.0.1](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v2.0.1)


### [V2.1.0](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v2.1.0)


### [V2.1.1](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v2.1.1)


### [V2.1.2](https://github.com/Mminzy22/AInfo-Backend/releases/tag/v2.1.2)

---

## 📄 라이센스

이 프로젝트는 학습 목적으로 제작되었으며, 공개된 코드는 자유롭게 참고할 수 있습니다. 

단, 상업적 사용은 금지됩니다.
