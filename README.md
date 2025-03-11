## 📝 프로젝트 개요

AInfo는 맞춤형 공공서비스 추천 AI 챗봇입니다. Django Rest Framework(DRF)를 기반으로 API를 제공하며, AI 모델과 연동하여 실시간으로 사용자의 질의에 응답합니다.

### 📆 개발 기간: 2025년 2월 27일 ~ 2025년 3월 31일

### 🍟 팀원:

- **양주영(팀장)**
    - API 및 PDF 데이터의 ChromaDB 인덱싱 및 저장 로직 구현
    - 고급 검색을 위한 리트리버(Retriever) 시스템 구현
- **박민지(부팀장)**
    - JWT 기반 회원 기능 (가입, 로그인, 프로필)
    - 백엔드 EC2 배포, 프론트 S3 + CloudFront 배포
    - HTTPS 적용 (Route53 + ACM)
- **유종열(서기)**
    - WebSocket 기반 챗봇 구현
    - 도커를 활용한 애플리케이션 및 레디스 컨테이너화
    - 챗봇UI 및 프론트엔드 개발
- **채희경(서기)**
    - LLM 및 Prompt 작성
    - LangChain을 활용한 로직 구현
- **정지웅(총무)**
    - WebSocket 기반 챗봇 구현
    - WebSocket에서 JWT 인증 미들웨어 적용
    - 챗봇 메시지 스트리밍 기능 추가

### 🔗연결 Frontend repo: [AInfo-Frontend](https://github.com/Mminzy22/AInfo-Frontend)

---

## 🛠️ 기술 스택

- **언어:** Python (Django, Django Rest Framework)
- **데이터베이스:** PostgresQL, ChromaDB
- **LLM 및 데이터 처리:** OpenAI API, LangChain
- **웹소켓:** Django Channels, Redis
- **배포:** Docker, AWS (EC2, S3, Route 53), Nginx, Gunicorn

---

## 📂 프로젝트 구조

```
📂 AInfo-Backend/
├── .github/ # GitHub 관련 설정 (CI/CD 및 이슈 템플릿)
│   ├── ISSUE_TEMPLATE/ # GitHub 이슈 템플릿
│   │   ├── bug_report.md → 버그 리포트 양식
│   │   ├── documentation.md → 문서화 관련 템플릿
│   │   └── feature_request.md → 기능 요청 양식
│   └── workflows/ # GitHub Actions 설정
│       └── ci.yml → CI/CD 관련 설정
│
├── accounts/ # 사용자 인증 및 관리
│   ├── migrations/ → DB 마이그레이션 파일
│   ├── admin.py → Django 관리자 페이지 설정
│   ├── apps.py → 앱 설정 파일
│   ├── models.py → 사용자 관련 모델 정의
│   ├── serializers.py → 데이터 직렬화 로직
│   ├── tests.py → accounts 관련 테스트 코드
│   ├── urls.py → accounts 관련 URL 라우팅
│   └── views.py → accounts 관련 뷰 로직
│
├── chatbot/ # AI 챗봇 관련 기능
│   ├── migrations/ → DB 마이그레이션 파일
│   ├── admin.py → 챗봇 관리자 페이지 설정
│   ├── apps.py → 챗봇 앱 설정 파일
│   ├── consumers.py → WebSocket 소비자 설정
│   ├── middleware.py → JWT 인증 미들웨어
│   ├── models.py → 챗봇 관련 데이터 모델
│   ├── prompt.py → AI 프롬프트 관련 파일
│   ├── retriever.py → RAG 검색 관련 파일
│   ├── routing.py → WebSocket 라우팅 설정
│   ├── serializers.py → 챗봇 데이터 직렬화 로직
│   ├── tests.py → 챗봇 테스트 코드
│   ├── urls.py → 챗봇 관련 URL 설정
│   └──  utils.py → 챗봇 LLM 구현 관련 파일
│
├── config/ # 프로젝트 설정 및 환경 변수
│   ├── init.py → 설정 패키지 초기화
│   ├── asgi.py → ASGI 서버 설정
│   ├── settings.py → Django 프로젝트 설정
│   ├── urls.py → 프로젝트 전체 URL 매핑
│   └── wsgi.py → WSGI 서버 설정
│
├── data/ # 데이터 관련 폴더
│   └── pdf/ # PDF 데이터 저장
│       └── 2025년_중앙부처_및_지자체_창업지원사업_안내책자.pdf → PDF 문서
│
├── vector_store/ # 벡터 데이터 저장 및 로딩
│   └── load_data.py → 벡터 데이터 로딩 스크립트
│
├── .flake8 → 코드 스타일 규칙
├── .gitignore → Git에 포함되지 않을 파일 설정
├── README.md → 프로젝트 설명 파일
├── docker-compose.yml → Docker 컨테이너들을 정의하고 관리하는 파일
├── dockerfile → Django 애플리케이션의 컨테이너를 빌드하는 파일
├── manage.py → Django 실행 파일
├── pyproject.toml → Python 프로젝트 설정
└── requirements.txt → 필수 패키지 목록
```

---

## ✨ 주요 기능

### 사용자 인증

- JWT 기반 로그인/회원가입
- 이메일 인증
- 소셜 로그인

### AI 챗봇

- LangChain + ChromaDB 기반 RAG 모델 연동
- Django Channels, Redis를 이용한 WebSocket 실시간 대화 지원

### 공공 데이터 연동

- 정부 API(고용24, 정부24, 온통청년) 활용
- 맞춤형 공공서비스 추천 기능

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
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 5. 서버 실행

```bash
redis-server
python manage.py runserver
```

---

## API 문서

API 엔드포인트 및 요청/응답 예시는 [API 문서](https://www.notion.so/1a7af76d38e28182a3d5e14e7d24b764?pvs=21)에서 확인하세요.

---

## 📄 라이센스

이 프로젝트는 학습 목적으로 제작되었으며, 공개된 코드는 자유롭게 참고할 수 있습니다. 

단, 상업적 사용은 금지됩니다.