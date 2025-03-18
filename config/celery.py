from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Django 설정 파일을 Celery에서 사용할 수 있도록 환경 변수 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Django settings.py에서 'CELERY_'로 시작하는 설정을 Celery가 가져오도록 설정
app.config_from_object("django.conf:settings", namespace="CELERY")

# Django 앱에서 task 자동 탐색
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
