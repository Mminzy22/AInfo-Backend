# Dockerfile
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Python이 실행될 때 바이트코드 파일(.pyc)을 디스크에 저장하지 않도록 하기위함
ENV PYTHONDONTWRITEBYTECODE 1
# Python 의 출력 버퍼링을 비활성화
ENV PYTHONUNBUFFERED 1

# 프로젝트 복사
COPY . .

# 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
