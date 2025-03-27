from __future__ import absolute_import, unicode_literals

# 이 파일을 통해 Celery 인스턴스를 Django가 시작할 때 초기화합니다.
from .celery import app as celery_app

__all__ = ("celery_app",)
