"""
Kstartup PDF 데이터 로더
Kstartup PDF에서 데이터를 로드하여 ChromaDB에 저장하는 파이프라인
PDF → 페이지별 추출 → 목차에서 정책명 + 페이지 매핑 → 임베딩 후 ChromaDB 저장
"""

import os
import re
import django
import fitz
from django.conf import settings
from langchain.docstore.document import Document
from tqdm import tqdm

from .common import (
    clear_collection,
    get_chroma_collection,
    get_embeddings,
    save_documents_with_progress,
)

# Django 환경설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

PDF_PATH = settings.PDF_PATH


def extract_pdf_pages(file_path):
    """
    PDF 페이지를 개별적으로 추출하여 텍스트 리스트로 반환
    """
    doc = fitz.open(file_path)
    return [page.get_text() for page in doc]


def parse_toc_improved(pages_text):
    """
    목차 페이지에서 정책 정보(코드, 제목, 페이지번호) 추출
    """
    toc_text = "\n".join(pages_text[1:15])

    pattern = re.compile(r"(\d{3})\s*\u25b6\u25b6\s*(.+?)\s+(\d{1,3})(?:\D|$)")
    toc_items = pattern.findall(toc_text)

    policies = []
    for match in toc_items:
        code, title, page = match
        page_num = int(page)
        if page_num > 483:
            continue
        policies.append({"code": code, "title": title.strip(), "page_num": page_num})

    return policies


def find_pdf_page_offset(file_path, policies):
    """
    페이지 내용과 정책 제목을 비교하여 최적의 오프셋 자동 계산
    """
    doc = fitz.open(file_path)
    possible_offsets = list(range(-5, 6))

    test_policies = policies[:10] if len(policies) > 10 else policies

    best_offset = 0
    best_match_score = -1

    for offset in possible_offsets:
        match_score = 0
        for policy in test_policies:
            page_num = policy["page_num"]
            page_idx = page_num - 1 - offset
            if 0 <= page_idx < len(doc):
                page_text = doc[page_idx].get_text()
                keywords = [kw for kw in policy["title"].split() if len(kw) > 1]
                keyword_matches = sum(1 for kw in keywords if kw in page_text)
                if keyword_matches > len(keywords) // 2:
                    match_score += keyword_matches
        if match_score > best_match_score:
            best_match_score = match_score
            best_offset = offset

    return best_offset


def build_documents_with_offset(policies, pages_text, offset=0):
    """
    페이지 오프셋을 적용하여 Document 객체 생성
    """
    docs = []
    skipped = []

    for policy in policies:
        page_idx = policy["page_num"] - 1 - offset
        if 0 <= page_idx < len(pages_text):
            text = pages_text[page_idx].strip()
            doc_obj = Document(
                page_content=text,
                metadata={
                    "title": policy["title"],
                    "page_num": policy["page_num"],
                },
            )
            docs.append(doc_obj)
        else:
            skipped.append(
                f"{policy['title']} (페이지 {policy['page_num']}, 인덱스 {page_idx})"
            )

    if skipped:
        tqdm.write(f"[WARN] 다음 {len(skipped)}개 정책의 페이지를 찾을 수 없어 건너뜀:")
        for item in skipped[:5]:
            tqdm.write(f"  - {item}")

    return docs
